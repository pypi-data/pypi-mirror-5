import pilas
from pilas.actores import Bomba

class BombaConMovimiento(Bomba):

    def __init__(self, x=0, y=0):
        Bomba.__init__(self, x, y)

        self.circulo = pilas.fisica.Circulo(x, y, 20, restitucion=1, friccion=0, amortiguacion=0)
        self.imitar(self.circulo)

        self._empujar()

    def _empujar(self):
        self.circulo.impulsar(2, 2)

class Aceituna(pilas.actores.Aceituna):

    def __init__(self):
        pilas.actores.Aceituna.__init__(self)
        self.aprender(pilas.habilidades.SeguirAlMouse)
        pilas.mundo.motor.ocultar_puntero_del_mouse()

def cuando_colisionan(aceituna, bomba):
    bomba.explotar()

pilas.iniciar(gravedad=(0,0))

protagonista = Aceituna()

bomba_1 = BombaConMovimiento()
bomba_2 = BombaConMovimiento(x=200, y=0)
bomba_3 = BombaConMovimiento(x=0, y=200)

lista_de_bombas = [bomba_1, bomba_2, bomba_3]

pilas.mundo.colisiones.agregar(protagonista, lista_de_bombas, cuando_colisionan)

pilas.ejecutar()
