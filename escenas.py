#!/usr/bin/env python
# -*- coding: utf-8 -*-

# License: GPL 3
# Córdoba Game Jam 2013
# Abrutsky - Bravo - Cabral - Ruscitti - Taira


#===============================================================================
# DOC
#===============================================================================

"""Escenas para el juego"""


#===============================================================================
# IMPORTS
#===============================================================================

import random
import pilas
import actores


#===============================================================================
# CANTIDAD PAREJAS
#===============================================================================

CANTIDAD_PAREJAS = 20
CANTIDAD_ITEMS = CANTIDAD_PAREJAS + 10
TIEMPO_DE_JUEGO = int((CANTIDAD_PAREJAS / 2.0) * 60)


#===============================================================================
# LOGOS INICIALES
#===============================================================================

class Logos(pilas.escena.Normal):

    def __init__(self, logos=[]):
        super(Logos, self).__init__()
        if logos:
            self._logos_futuros = list(logos)
        else:
            self._logos_futuros = [(2.5, "pilasengine.png", "roar.wav"),
                                   (2.0, "cbagamejam2013.png", "corazon.mp3"),
                                   (2.0, "globalgamejam2013.png", None)]
        lst = self._logos_futuros.pop(0)
        self._timer = lst[0]
        self._logo = pilas.imagenes.cargar_imagen(lst[1])
        self._sound = pilas.sonidos.cargar(lst[2]) if lst[2] else None

    def iniciar(self):
        pilas.fondos.Fondo(imagen=self._logo)
        if self._sound:
            self._sound.reproducir()
        pilas.mundo.agregar_tarea(self._timer, self.siguiente)
        self.pulsa_tecla.conectar(self.siguiente)
        self.click_de_mouse.conectar(self.siguiente)

    def siguiente(self, *args, **kwargs):
        if self._sound:
            self._sound.detener()
        if self._logos_futuros:
            pilas.cambiar_escena(Logos(self._logos_futuros))
        else:
            pilas.cambiar_escena(Menu())


#===============================================================================
# ABOUT
#===============================================================================

class About(pilas.escena.Base):

    def iniciar(self):
        pilas.fondos.Fondo(imagen=pilas.imagenes.cargar_imagen("about.png"))
        self.pulsa_tecla.conectar(self.volver_al_menu)
        self.click_de_mouse.conectar(self.volver_al_menu)

    def volver_al_menu(self, evt):
        pilas.recuperar_escena()


#===============================================================================
# MENU PRINCIPAL
#===============================================================================

class Menu(pilas.escena.Base):

    def __init__(self):
        pilas.escena.Base.__init__(self)
        self.musicamenu = pilas.sonidos.cargar("musicamenu.mp3")


    def juego(self):
        self.musicamenu.detener()
        pilas.cambiar_escena(Juego())

    def about(self):
        pilas.almacenar_escena(About())

    def full_screen(self):
        pilas.mundo.motor.canvas.alternar_pantalla_completa()

    def salir_del_juego(self):
        pilas.terminar()

    def mostrar_menu(self):
        self.menu = pilas.actores.Menu([("Let's Break Some Hearts", self.juego),
                                        ("About", self.about),
                                        ("Full Screen?", self.full_screen),
                                        ("Exit", self.salir_del_juego)],
                                        fuente="visitor1.ttf",
                                        y=-40)

        self.p = pilas.actores.Pizarra(0, -120, 640, 200)
        self.p.pintar(pilas.colores.negro)
        self.p.transparencia = 40
        self.p.z = 300

    def reanudar(self):
        self.musicamenu.continuar()

    def iniciar(self):
        self.musicamenu.reproducir()
        pilas.fondos.Fondo("menu.png")
        pilas.mundo.agregar_tarea(1.5, self.mostrar_menu)


#===============================================================================
# JUEGO
#===============================================================================

class Juego(pilas.escena.Base):

    def random_xy(self):
        valid = False
        while not valid:
            x = (random.randint(0, self.mapa.ancho) / 2) + 10
            y = (random.randint(0, self.mapa.alto) / 2) + 10
            if random.randint(0, 1):
                x = -x
            if random.randint(0, 1):
                y = -y
            try:
                if not self.mapa.es_punto_solido(x, y) \
                and self.viejo.distancia_al_punto(x, y) > 20:
                    valid = True
            except:
                pass
        return x, y

    def centrar_camara(self, evt):
        mm_ancho = self.mapa.ancho / 2
        mm_alto = self.mapa.alto / 2
        mp_ancho = pilas.mundo.motor.ancho_original / 2
        mp_alto = pilas.mundo.motor.alto_original / 2
        if abs(self.viejo.x) < mm_ancho - mp_ancho:
            self.camara.x = [self.viejo.x]
        if abs(self.viejo.y) < mm_alto - mp_alto:
            self.camara.y = [self.viejo.y]

    def iniciar(self):
        self.musicajuego = pilas.sonidos.cargar("musicajuego.mp3")
        self.musicajuego.reproducir()
        self.mapa = pilas.actores.MapaTiled("mapaprincipal.tmx")
        self.mapa.z = self.mapa.alto + 10
        self.viejo = actores.Viejo(self.mapa, x=-20, y=20)
        self.actualizar.conectar(self.centrar_camara)
        pilas.eventos.pulsa_tecla_escape.conectar(self.regresar_al_menu)

        # Crear parejas
        self.parejas = {}
        self.lista_items = []
        for x in range(CANTIDAD_PAREJAS):
            x, y = self.random_xy()
            pareja = actores.Pareja(x, y)
            self.parejas[pareja.as_actor] = pareja
            x, y = self.random_xy()
            item = actores.Item(imagen=pareja.nombre_imagen_item,
                                fijo=False, x=x, y=y)
            self.lista_items.append(item)

        # Agregamos todos los items que faltan mas la pistola
        x, y = self.random_xy()
        self.lista_items.append(actores.Item(imagen=actores.PISTOLA,
                                             fijo=False, x=x, y=y))
        while len(self.lista_items) < CANTIDAD_ITEMS:
            x, y = self.random_xy()
            nombre_imagen = random.choice(actores.PAREJAS_X_ITEMS.values())
            item = actores.Item(imagen=nombre_imagen, fijo=False, x=x, y=y)
            self.lista_items.append(item)

        # Creamos el timer del juego
        self.timer = pilas.actores.Temporizador(
            x=(pilas.mundo.motor.ancho_original/2)-50,
            y=(pilas.mundo.motor.alto_original/2)-10,
            fuente="visitor1.ttf",
        )
        self.timer.ajustar(TIEMPO_DE_JUEGO, self.youlose)
        self.timer.iniciar()

        # Contador de parejas rotas
        self.corazon_roto = pilas.actores.Animacion(
            pilas.imagenes.cargar_grilla("corazon_roto.png", 2), True,
            velocidad=0.9, x=110, y=-210
        )
        self.corazon_roto.fijo = True
        self.corazon_roto.z = -20000
        self.contador = pilas.actores.Texto(
            str(CANTIDAD_PAREJAS - len(self.parejas)),
            fuente="visitor1.ttf",
            x=130, y=-205
        )
        self.contador.color = pilas.colores.rojo
        self.contador.fijo = True
        self.contador.z = -20000

        # Vinculamos las colisiones
        self.vincular_colisiones()

    def regresar_al_menu(self, evento):
        pilas.escena_actual().camara.x = 0
        pilas.escena_actual().camara.y = 0
        pilas.cambiar_escena(Menu())

    def reanudar(self):
        self.camara.x, self.camara.y = self.viejo.x, self.viejo.y
        for k in self.parejas.keys():
            pareja = self.parejas[k]
            if pareja.debe_eliminarse:
                pareja.romper_pareja()
                self.parejas.pop(k)
        self.vincular_colisiones()
        self.contador.texto = str(CANTIDAD_PAREJAS - len(self.parejas))
        if not self.parejas:
            self.camara.x, self.camara.y = 0, 0
            pilas.cambiar_escena(
                Logos([(6, "youwin.png", "risa.wav")])
            )
        self.musicajuego.continuar()

    def vincular_colisiones(self):
        pilas.escena_actual().colisiones.agregar(self.viejo,
                                                 self.parejas.keys(),
                                                 self.ir_a_encuentro)
        pilas.escena_actual().colisiones.agregar(self.viejo,
                                                 self.lista_items,
                                                 self.encontrar_items)

    def youlose(self):
        self.musicajuego.detener()
        self.camara.x, self.camara.y = 0, 0
        pilas.cambiar_escena(
            Logos([(6, "youlose.png", "perder.wav")])
        )

    def encontrar_items(self, viejo, item):
        viejo.agarrar_item(item)

    def ir_a_encuentro(self, viejo, act):
        self.musicajuego.pausar()
        pareja = self.parejas[act]
        pilas.almacenar_escena(Encuentro(pareja, viejo, self.mapa))


#===============================================================================
# ENCUENTRO
#===============================================================================

class Encuentro(pilas.escena.Base):

    def __init__(self, pareja, viejo, mapa):
        pilas.escena.Base.__init__(self)
        self.pareja = pareja
        self.viejo = viejo
        self.timer = pilas.actores.Temporizador(
            x=(pilas.mundo.motor.ancho_original/2)-50,
            y=(pilas.mundo.motor.alto_original/2)-10,
            fuente="visitor1.ttf",
        )
        self.mapa = mapa
        self.timer.ajustar(10, self.salir)

    def iniciar(self):
        pilas.escena_actual().camara.x = 0
        pilas.escena_actual().camara.y = 0

        self.sonidocorazon = pilas.sonidos.cargar("corazon.mp3")
        self.sonidocorazon.reproducir()

        pilas.fondos.Fondo("fondoencuentro.png")
        fotopareja = pilas.actores.Actor(self.pareja.imagen)
        fotopareja.escala = 0.8
        fotopareja.escala = [1]
        fotopareja.y = 100

        # TODO: el redibujar,  meterlo en una funcion
        pilas.actores.utils.insertar_como_nuevo_actor(self.viejo.barra)
        for item in self.viejo.barra.items:
            pilas.actores.utils.insertar_como_nuevo_actor(item)

        # TODO: el timer no se dibuja
        self.timer.iniciar()

        pilas.eventos.click_de_mouse.conectar(self.hace_click_de_mouse)

    def hace_click_de_mouse(self, evento):
        item = pilas.actores.utils.obtener_actor_en(evento.x, evento.y)

        if isinstance(item, actores.Item):
            if self.pareja.se_elimina_con_item(item):
                self.pareja.debe_eliminarse = True
            self.salir()

    def salir(self):
        self.sonidocorazon.detener()
        self.viejo.y = self.viejo.y -50
        while self.mapa.es_punto_solido(self.viejo.x, self.viejo.y):
            self.viejo.y = self.viejo.y -50
        pilas.recuperar_escena()




#===============================================================================
# MAIN
#===============================================================================

if __name__ == "__main__":
    print(__doc__)
