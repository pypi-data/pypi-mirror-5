# -*- encoding: utf-8 -*-
import code
import sys

import os
os.environ['lanas'] = 'enabled'

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import highlighter
import autocomplete
import version

class Ventana(QWidget):

    def __init__(self, parent=None, scope=None, codigo_inicial="", with_log=False):
        super(Ventana, self).__init__(parent)
        box = QVBoxLayout()
        box.setMargin(0)
        box.setSpacing(0)

        self.setLayout(box)

        if not scope:
            scope = locals()

        self.text_edit = InterpreteTextEdit(self, codigo_inicial)
        self.text_edit.init(scope)

        self.log_widget = QListWidget(self)

        if not with_log:
            self.log_widget.hide()

        box.addWidget(self.text_edit)
        box.addWidget(self.log_widget)

        self.resize(650, 300)
        self.center_on_screen()
        self.raise_()
        self.log("Iniciando lanas ver " + version.VERSION)

    def center_on_screen(self):
        resolution = QDesktopWidget().screenGeometry()
        self.move((resolution.width()  / 2) - (self.frameSize().width()  / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def closeEvent(self, event):
        sys.exit(0)

    def log(self, mensaje):
        item = QListWidgetItem(mensaje)
        self.log_widget.addItem(item)

    def alternar_log(self):
        if self.log_widget.isHidden():
            self.log_widget.show()
        else:
            self.log_widget.hide()

    def raw_input(self, mensaje):
        text, state = QInputDialog.getText(self, "raw_input", mensaje)
        return str(text)

    def input(self, mensaje):
        text, state = QInputDialog.getText(self, "raw_input", mensaje)
        return eval(str(text))


class Output:

    def __init__(self, destino):
        self.destino = destino

    def write(self, linea):
        self.destino.insertar_error(linea)
        self.destino.ensureCursorVisible()

class NormalOutput(Output):
    pass

class InterpreteTextEdit(autocomplete.CompletionTextEdit):

    def __init__(self,  parent, codigo_inicial):
        super(InterpreteTextEdit,  self).__init__(parent)

        self.ventana = parent
        sys.stdout = self
        sys.stderr = Output(self)
        self.refreshMarker = False
        self.multiline = False
        self.command = ''
        self.history = []
        self.historyIndex = -1
        self.interpreterLocals = {}

        # setting the color for bg and text
        #palette = QPalette()
        #palette.setColor(QPalette.Base, QColor(20, 20, 20))
        #palette.setColor(QPalette.Text, QColor(0, 255, 0))
        #self.setPalette(palette)

        self._set_font_size(16)
        self._highlighter = highlighter.Highlighter(self.document(), 'python', highlighter.COLOR_SCHEME)

        if codigo_inicial:
            for line in codigo_inicial.split("\n"):
                self.insertar_comando_falso(line)

        self.marker()

    def insertar_error(self, mensaje):
        self.insertHtml(u"<b style='color: #FF0000'>  ×</b> %s" %(mensaje))
        self.insertPlainText('\n')

    def insertar_mensaje(self, mensaje):
        self.insertHtml("<p style='color: green'>%s</p><p></p>" %(mensaje))

    def insertar_comando_falso(self, comando):
        self.marker()
        self.insertHtml(comando)
        self.insertPlainText('\n')

    def _set_font_size(self, font_size):
        self.font_size = font_size
        font = QFont('Monaco', font_size)
        self.setFont(font)

    def _change_font_size(self, delta_size):
        self._set_font_size(self.font_size + delta_size)

    def marker(self):
        if self.multiline:
            self.insertHtml(u"<b style='color: #FF0000'>‥</b> ")
            self.insertPlainText("    ")
        else:
            self.insertHtml(u"<b style='color: #3583FC'>»</b> ")

    def init(self, interpreter_locals):
        if interpreter_locals:
            self.interpreter = code.InteractiveInterpreter(interpreter_locals)
            self.interpreter.runsource('raw_input = self.raw_input')
            self.interpreter.runsource('input = self.input')
            self.interpreterLocals = interpreter_locals

    def updateInterpreterLocals(self, newLocals):
        className = newLocals.__class__.__name__
        self.interpreterLocals[className] = newLocals

    def write(self, line):
        self.insertPlainText(line)
        self.ensureCursorVisible()

    def clearCurrentBlock(self):
        length = len(self.document().lastBlock().text()[2:])

        if length:
            [self.textCursor().deletePreviousChar() for x in xrange(length)]

    def recall_history(self):
        self.clearCurrentBlock()
        if self.historyIndex <> -1:
            self.insertPlainText(self.history[self.historyIndex])

    def _get_entered_line(self):
        textCursor = self.textCursor()
        position = len(self.document().toPlainText())
        textCursor.setPosition(position)
        self.setTextCursor(textCursor)

        line = unicode(self.document().lastBlock().text())[2:]
        line.rstrip()
        return line

    def _get_current_word(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def _get_current_block_prefix(self):
        tc = self.textCursor()
        tc.select(QTextCursor.BlockUnderCursor)
        current_block = tc.selectedText()
        words = current_block.split(" ")
        prefix = words[-1]

        if '(' in prefix:
            prefix = prefix.split('(')[-1]

        if '.' in prefix:
            prefixes = prefix.split('.')
            prefixes = prefixes[:-1]
            return '.'.join([str(s) for s in prefixes])
        else:
            return prefix

    def _set_current_word(self, word):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        tc.removeSelectedText()
        tc.insertText(word)

    def keyPressEvent(self, event):
        # cambia el tamano de la tipografia.
        if event.modifiers() & Qt.AltModifier:
            if event.key() == Qt.Key_Minus:
                self._change_font_size(-2)
                event.ignore()
                return
            elif event.key() == Qt.Key_Equal:
                self._change_font_size(+2)
                event.ignore()
                return
            elif event.key() == Qt.Key_I:
                self.ventana.alternar_log()
                return
            elif event.key() == Qt.Key_S:
                self.guardar_contenido_con_dialogo()
                return

        # navegar por el historial
        if event.key() == Qt.Key_Down:
            if self.historyIndex == len(self.history):
                self.historyIndex -= 1
            try:
                if self.historyIndex > -1:
                    self.historyIndex -= 1
                    self.recall_history()
                else:
                    self.clearCurrentBlock()
            except:
                pass
            return None

        # navegar por el historial
        if event.key() == Qt.Key_Up:
            try:
                if len(self.history) - 1 > self.historyIndex:
                    self.historyIndex += 1
                    self.recall_history()
                else:
                    self.historyIndex = len(self.history)
            except:
                pass
            return None

        # ir al primer caracter del interprete cuando pulsa HOME
        if event.key() == Qt.Key_Home:
            blockLength = len(self.document().lastBlock().text()[2:])
            lineLength  = len(self.document().toPlainText())
            position = lineLength - blockLength
            textCursor  = self.textCursor()
            textCursor.setPosition(position)
            self.setTextCursor(textCursor)
            return None

        if event.key() in [Qt.Key_Left, Qt.Key_Backspace]:
            if self.textCursor().positionInBlock() >= 3:
                super(InterpreteTextEdit, self).keyPressEvent(event)
            return


        try:
            if self.autocomplete(event):
                return None
        except UnicodeEncodeError:
            pass


        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            line = self._get_entered_line()
            self.historyIndex = -1

            if line == "clear":
                self.document().setPlainText("")
                self.marker()
                return

            try:
                line[-1]
                self.haveLine = True
                if line[-1] in [':', ',', '[', '(']:
                    self.multiline = True
                self.history.insert(0, line)
            except:
                self.haveLine = False

            # Cuando pulsa ENTER luego de haber hecho un texto multilinea y borrado todos los caracteres.
            if self.multiline and (not self.haveLine or self._ha_ingresado_solo_espacios(line)): #  multi line done
                self.append('') # move down one line
                self.interpreter.runsource(self.command)
                self.command = '' # clear command
                self.multiline = False # back to single line
                self.marker() # handle marker style
                return None

            if self.haveLine and self.multiline: # multi line command
                self.command += line + '\n' # + command and line
                self.append('')
                self.marker()
                return None

            # Permite escribir lineas terminas con '?' para consultar la documentacion
            # de manera similar a como lo hace ipython.
            if line.endswith('?'):
                line = 'print ' + line[:-1] + '.__doc__.decode("utf-8")'

            if self.haveLine and not self.multiline: # one line command
                self.command = line # line is the command
                self.append('') # move down one line
                self.interpreter.runsource(self.command)
                self.command = '' # clear command
                self.marker() # handle marker style
                return None

            # Cuando pulsa ENTER sin texto.
            if not self.haveLine and not self.multiline:
                self.append('')
                self.marker()
                return None

            return None

        super(InterpreteTextEdit, self).keyPressEvent(event)

    def guardar_contenido_con_dialogo(self):
        filename = QFileDialog.getSaveFileName(self, 'Guardar archivo', 'programa.py', 'Python (*.py)')

        if filename:
            fname = open(filename, 'w')
            texto = self.obtener_contenido_completo()
            fname.write(texto)
            fname.close()

    def _ha_ingresado_solo_espacios(self, linea):
        # TODO: Reemplazar por una expresion regular para
        #       detectar lineas donde solo hay espacios en blanco.
        if linea == "    ":
            return True

    def obtener_contenido_completo(self):
        texto = self.document().toPlainText()
        texto = texto.replace(u'‥ ', '')
        texto = texto.replace(u'» ', '')
        return texto
