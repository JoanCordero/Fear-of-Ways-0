import pygame
import sys
import json
import os
from nivel import nivel
from pared import pared
from salida import salida


class Camera:
    def __init__(self, ancho_mundo, alto_mundo, pantalla_w, pantalla_h, zoom=1.0):
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = zoom
        self.ancho_mundo = ancho_mundo
        self.alto_mundo = alto_mundo
        self.pantalla_w = pantalla_w
        self.pantalla_h = pantalla_h
        # margen externo en píxeles para mostrar un borde vacío alrededor del mapa
        self.margin = 120

    def aplicar(self, rect: pygame.Rect) -> pygame.Rect:
        """Convierte un rect del mundo a coordenadas de pantalla aplicando offset y zoom."""
        return pygame.Rect(
            int((rect.x - self.offset_x) * self.zoom),
            int((rect.y - self.offset_y) * self.zoom),
            int(rect.w * self.zoom),
            int(rect.h * self.zoom),
        )

    def centrar_en(self, x, y):
        """Centra la cámara en la posición (x, y) del mundo, con límites en los bordes del mapa."""
        self.offset_x = x - (self.pantalla_w / (2 * self.zoom))
        self.offset_y = y - (self.pantalla_h / (2 * self.zoom))
        # Clamp allowing a margin outside the world so the map can be centered
        min_x = -self.margin
        max_x = self.ancho_mundo - self.pantalla_w / self.zoom + self.margin
        min_y = -self.margin
        max_y = self.alto_mundo - self.pantalla_h / self.zoom + self.margin
        self.offset_x = max(min_x, min(self.offset_x, max_x))
        self.offset_y = max(min_y, min(self.offset_y, max_y))

    def world_rect(self):
        """Devuelve el rectángulo del mundo (útil para dibujar bordes)."""
        return pygame.Rect(0, 0, int(self.ancho_mundo), int(self.alto_mundo))


def main():
    pygame.init()
    info = pygame.display.Info()
    pantalla_w, pantalla_h = info.current_w, info.current_h
    # Abrir en pantalla completa
    pantalla = pygame.display.set_mode((pantalla_w, pantalla_h), pygame.FULLSCREEN)
    pygame.display.set_caption("Mapas - Vista de Niveles (1/2/3)")
    reloj = pygame.time.Clock()

    # Crear instancias de niveles
    niveles = [nivel(1), nivel(2), nivel(3)]
    indice = 0

    cam = Camera(niveles[indice].ancho, niveles[indice].alto, pantalla_w, pantalla_h, zoom=1.0)
    cam.centrar_en(niveles[indice].ancho // 2, niveles[indice].alto // 2)

    fuente = pygame.font.SysFont(None, 28)

    # Editor state
    edit_mode = False
    tool = None  # 'wall', 'key', 'spawn', 'exit'
    dragging = False
    drag_start = None
    preview_rect = None
    edit_history = []  # stack of actions for undo
    rotate_lock = False
    snap_to_grid = False
    grid_size = 20

    mostrando = True
    while mostrando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                mostrando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    mostrando = False
                elif evento.key == pygame.K_m:
                    edit_mode = not edit_mode
                    tool = None
                elif evento.key == pygame.K_w:
                    if edit_mode:
                        tool = 'wall'
                elif evento.key == pygame.K_k:
                    if edit_mode:
                        tool = 'key'
                elif evento.key == pygame.K_s:
                    if edit_mode:
                        tool = 'spawn'
                elif evento.key == pygame.K_e:
                    if edit_mode:
                        tool = 'exit'
                elif evento.key == pygame.K_z:
                    if edit_mode and edit_history:
                        action = edit_history.pop()
                        if action['type'] == 'wall':
                            try:
                                niveles[indice].muros.remove(action['obj'])
                            except ValueError:
                                pass
                        elif action['type'] == 'key':
                            try:
                                niveles[indice].llaves.remove(action['obj'])
                            except Exception:
                                pass
                        elif action['type'] == 'spawn':
                            try:
                                niveles[indice].spawn_enemigos.remove(action['obj'])
                            except Exception:
                                pass
                        elif action['type'] == 'exit':
                            niveles[indice].salida = action.get('prev')
                elif evento.key == pygame.K_l:
                    if edit_mode:
                        data = {}
                        lvl = niveles[indice]
                        data['nivel'] = lvl.numero
                        data['muros'] = [{'x': m.rect.x, 'y': m.rect.y, 'w': m.rect.w, 'h': m.rect.h} for m in lvl.muros]
                        data['llaves'] = [{'x': r.x, 'y': r.y, 'w': r.w, 'h': r.h} for r in getattr(lvl, 'llaves', [])]
                        data['spawns'] = [{'x': p[0], 'y': p[1]} for p in getattr(lvl, 'spawn_enemigos', [])]
                        data['salida'] = None
                        if getattr(lvl, 'salida', None):
                            srect = lvl.salida.rect
                            data['salida'] = {'x': srect.centerx, 'y': srect.centery}
                        out = os.path.join(os.getcwd(), f'mapas_export_nivel_{lvl.numero}.json')
                        try:
                            with open(out, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2)
                            print(f"Guardado export: {out}")
                        except Exception as e:
                            print("Error guardando export:", e)
                elif evento.key == pygame.K_LEFTBRACKET:
                    # disminuir margin
                    cam.margin = max(0, cam.margin - 20)
                    print(f"Margin: {cam.margin}")
                elif evento.key == pygame.K_RIGHTBRACKET:
                    # aumentar margin
                    cam.margin = cam.margin + 20
                    print(f"Margin: {cam.margin}")
                elif evento.key == pygame.K_t:
                    # alinear vista para mostrar la parte superior del mapa (usar margin)
                    cam.offset_y = -cam.margin
                    # clamp horizontal as usual
                    cam.offset_x = max(-cam.margin, min(cam.offset_x, cam.ancho_mundo - cam.pantalla_w / cam.zoom + cam.margin))
                elif evento.key == pygame.K_r:
                    if edit_mode:
                        rotate_lock = not rotate_lock
                elif evento.key == pygame.K_g:
                    if edit_mode:
                        snap_to_grid = not snap_to_grid
                elif evento.key == pygame.K_PLUS or evento.key == pygame.K_EQUALS:
                    cam.zoom = min(3.0, cam.zoom + 0.1)
                elif evento.key == pygame.K_MINUS:
                    cam.zoom = max(0.4, cam.zoom - 0.1)
                elif evento.key == pygame.K_w and not edit_mode:
                    cam.offset_y -= 50 / cam.zoom
                elif evento.key == pygame.K_s and not edit_mode:
                    cam.offset_y += 50 / cam.zoom
                elif evento.key == pygame.K_a and not edit_mode:
                    cam.offset_x -= 50 / cam.zoom
                elif evento.key == pygame.K_d and not edit_mode:
                    cam.offset_x += 50 / cam.zoom
                elif evento.key in (pygame.K_RIGHT, pygame.K_KP_PLUS):
                    indice = (indice + 1) % len(niveles)
                    cam = Camera(niveles[indice].ancho, niveles[indice].alto, pantalla_w, pantalla_h, zoom=1.0)
                    cam.centrar_en(niveles[indice].ancho // 2, niveles[indice].alto // 2)
                elif evento.key in (pygame.K_LEFT, pygame.K_KP_MINUS):
                    indice = (indice - 1) % len(niveles)
                    cam = Camera(niveles[indice].ancho, niveles[indice].alto, pantalla_w, pantalla_h, zoom=1.0)
                    cam.centrar_en(niveles[indice].ancho // 2, niveles[indice].alto // 2)
                elif evento.key == pygame.K_1:
                    indice = 0
                    cam = Camera(niveles[indice].ancho, niveles[indice].alto, pantalla_w, pantalla_h, zoom=1.0)
                    cam.centrar_en(niveles[indice].ancho // 2, niveles[indice].alto // 2)
                elif evento.key == pygame.K_2:
                    indice = 1
                    cam = Camera(niveles[indice].ancho, niveles[indice].alto, pantalla_w, pantalla_h, zoom=1.0)
                    cam.centrar_en(niveles[indice].ancho // 2, niveles[indice].alto // 2)
                elif evento.key == pygame.K_3:
                    indice = 2
                    cam = Camera(niveles[indice].ancho, niveles[indice].alto, pantalla_w, pantalla_h, zoom=1.0)
                    cam.centrar_en(niveles[indice].ancho // 2, niveles[indice].alto // 2)
                elif evento.key == pygame.K_UP and not edit_mode:
                    # mover vista hacia arriba en modo espectador
                    cam.offset_y = max(-cam.margin, cam.offset_y - (100 / cam.zoom))
                elif evento.key == pygame.K_DOWN and not edit_mode:
                    # mover vista hacia abajo en modo espectador
                    cam.offset_y = min(cam.alto_mundo - cam.pantalla_h / cam.zoom + cam.margin, cam.offset_y + (100 / cam.zoom))
                elif evento.key == pygame.K_x:
                    # eliminar llave bajo el cursor (funciona en editor y espectador)
                    mx, my = pygame.mouse.get_pos()
                    world_x = int(mx / cam.zoom + cam.offset_x)
                    world_y = int(my / cam.zoom + cam.offset_y)
                    lvl = niveles[indice]
                    removed = None
                    for r in list(getattr(lvl, 'llaves', [])):
                        if r.collidepoint(world_x, world_y):
                            lvl.llaves.remove(r)
                            edit_history.append({'type': 'key', 'obj': r})
                            removed = r
                            print('Llave eliminada en:', (r.x, r.y))
                            break
                    if not removed:
                        print('No hay llave bajo el cursor')

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                mx, my = evento.pos
                world_x = int(mx / cam.zoom + cam.offset_x)
                world_y = int(my / cam.zoom + cam.offset_y)
                if evento.button == 1:  # left click
                    if edit_mode and tool == 'wall':
                        dragging = True
                        drag_start = (world_x, world_y)
                    elif edit_mode and tool == 'key':
                        lvl = niveles[indice]
                        if not hasattr(lvl, 'llaves'):
                            lvl.llaves = []
                        r = pygame.Rect(world_x - 10, world_y - 10, 20, 20)
                        lvl.llaves.append(r)
                        edit_history.append({'type': 'key', 'obj': r})
                    elif edit_mode and tool == 'spawn':
                        lvl = niveles[indice]
                        if not hasattr(lvl, 'spawn_enemigos'):
                            lvl.spawn_enemigos = []
                        p = (world_x, world_y)
                        lvl.spawn_enemigos.append(p)
                        edit_history.append({'type': 'spawn', 'obj': p})
                    elif edit_mode and tool == 'exit':
                        lvl = niveles[indice]
                        prev = getattr(lvl, 'salida', None)
                        lvl.salida = salida(world_x, world_y)
                        edit_history.append({'type': 'exit', 'prev': prev})
                elif evento.button == 3:  # right click: remove wall under cursor
                    if edit_mode:
                        lvl = niveles[indice]
                        to_remove = None
                        for m in lvl.muros:
                            if m.rect.collidepoint(world_x, world_y):
                                to_remove = m
                                break
                        if to_remove:
                            lvl.muros.remove(to_remove)
                            edit_history.append({'type': 'wall', 'obj': to_remove})

            elif evento.type == pygame.MOUSEBUTTONUP:
                if evento.button == 1 and dragging and edit_mode and tool == 'wall':
                    mx, my = evento.pos
                    world_x = int(mx / cam.zoom + cam.offset_x)
                    world_y = int(my / cam.zoom + cam.offset_y)
                    x1, y1 = drag_start
                    x2, y2 = world_x, world_y
                    rx = min(x1, x2)
                    ry = min(y1, y2)
                    rw = abs(x2 - x1)
                    rh = abs(y2 - y1)
                    if rw > 5 and rh > 5:
                        # Apply rotate lock (swap width/height)
                        if rotate_lock:
                            rw, rh = rh, rw
                        # Apply grid snapping
                        if snap_to_grid and grid_size > 1:
                            rx = (rx // grid_size) * grid_size
                            ry = (ry // grid_size) * grid_size
                            rw = max(grid_size, ((rw + grid_size // 2) // grid_size) * grid_size)
                            rh = max(grid_size, ((rh + grid_size // 2) // grid_size) * grid_size)
                        m = pared(rx, ry, rw, rh)
                        niveles[indice].muros.append(m)
                        edit_history.append({'type': 'wall', 'obj': m})
                    dragging = False
                    drag_start = None
                    preview_rect = None

            elif evento.type == pygame.MOUSEMOTION:
                if dragging and drag_start:
                    mx, my = evento.pos
                    world_x = int(mx / cam.zoom + cam.offset_x)
                    world_y = int(my / cam.zoom + cam.offset_y)
                    x1, y1 = drag_start
                    rx = min(x1, world_x)
                    ry = min(y1, world_y)
                    rw = abs(world_x - x1)
                    rh = abs(world_y - y1)
                    prx, pry, prw, prh = rx, ry, rw, rh
                    # during preview, apply rotate lock and snap visually
                    if rotate_lock:
                        prw, prh = prh, prw
                    if snap_to_grid and grid_size > 1:
                        prx = (prx // grid_size) * grid_size
                        pry = (pry // grid_size) * grid_size
                        prw = max(grid_size, ((prw + grid_size // 2) // grid_size) * grid_size)
                        prh = max(grid_size, ((prh + grid_size // 2) // grid_size) * grid_size)
                    preview_rect = pygame.Rect(prx, pry, prw, prh)

        pantalla.fill((10, 10, 10))

        # Dibujar nivel actual
        niveles[indice].dibujar(pantalla, cam)

        # Dibujar borde visual alrededor del mapa para que no quede pegado a la pantalla
        try:
            world_r = cam.world_rect()
            borde = cam.aplicar(world_r)
            pygame.draw.rect(pantalla, (180, 180, 220), borde, 4)
        except Exception:
            pass

        # Si estamos en modo editor dibujar overlay y preview
        if edit_mode:
            # semi-transparency for overlay
            s = pygame.Surface((pantalla_w, pantalla_h), pygame.SRCALPHA)
            s.fill((0, 0, 0, 40))
            pantalla.blit(s, (0, 0))
            # tool text
            instr_lines = [
                f"EDIT MODE — herramienta: {tool or 'ninguna'}",
                "W: muro (arrastrar LMB) | R: alternar rotación (swaps w/h)",
                "K: colocar llave (LMB) | S: colocar spawn (LMB) | E: colocar salida (LMB)",
                "RMB sobre muro: eliminar muro | Z: deshacer | L: guardar a JSON",
                "G: snap a grid (toggle) | +/-: zoom | WASD: pan (fuera de EDIT)",
                f"Rotate: {'ON' if rotate_lock else 'OFF'} | Snap: {'ON' if snap_to_grid else 'OFF'} | Grid: {grid_size}px",
            ]
            for i, line in enumerate(instr_lines):
                surf_tool = fuente.render(line, True, (255, 255, 200))
                pantalla.blit(surf_tool, (20, 40 + i * 22))

            if preview_rect:
                r = cam.aplicar(preview_rect)
                pygame.draw.rect(pantalla, (200, 80, 80), r, 3)
                # fill translucent
                tmp = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                tmp.fill((200, 80, 80, 40))
                pantalla.blit(tmp, (r.x, r.y))

        # Superposición de texto con instrucciones
        texto = f"Nivel {indice + 1} — Flechas izquierda/derecha para cambiar, 1/2/3 para seleccionar, ESC salir"
        surf = fuente.render(texto, True, (230, 230, 230))
        pantalla.blit(surf, (20, 20))

        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
