import copy
import math
import threading
import time

import numpy as np
from joblib import Parallel, delayed
import pygame
from pygame.locals import *

from utils import Text, COLORS
from tile import Tile

WindowSize = (1024, 768)
TileSize = 16
Tiles = []
Mode = 0
SimulationActive = False

Texts = {}

tiles_width = int(WindowSize[0] / TileSize)
tiles_height = int(WindowSize[1] / TileSize)

for col in range(tiles_width):
    column = []
    Tiles.append(column)
    for row in range(tiles_height):
        column.append(Tile(0, nmol=0)) #nmol=4.16


pygame.init()
display = pygame.display.set_mode(WindowSize)
clock = pygame.time.Clock()

def get_text(name):
    if name in Texts:
        return Texts[name]
    return None

def draw_tiles(display):
    col = -1
    while col < tiles_width-1:
        col += 1
        row = -1
        while row < tiles_height-1:
            row += 1
            tile = Tiles[col][row]
            if tile.tile_id == 1:
                display.fill(COLORS.GREEN, Rect(col*TileSize, row*TileSize, TileSize, TileSize))
            else:
                p = tile.get_pressure()
                fill = int(min(255, 255*math.sqrt(p)))
                fill_g = int(max(min(fill, 51*(5-p)), 0))
                display.fill(Color(0, fill_g, fill), Rect(col*TileSize, row*TileSize, TileSize, TileSize))

def update_mode(mode):
    txt = get_text('txt_mode')
    if mode == 0:
        txt.set_text('Tile Mode')
    elif mode == 1:
        txt.set_text('Air Mode')
    global Mode
    Mode = mode

def update_info(x, y):
    scaledx = int(x / TileSize)
    scaledy = int(y / TileSize)
    tile = Tiles[scaledx][scaledy]
    get_text('txt_info1').set_text(f'Pressure: {round(tile.get_pressure(), 2)} atm')
    get_text('txt_info2').set_text(f'Temp: {tile.temperature} C')
    get_text('txt_info3').set_text(f'Moles: {round(tile.num_moles, 2)}')
    get_text('txt_fps').set_text(f'FPS: {round(clock.get_fps(),2)}')

def handle_mouse(x, y, button):
    if button == 1 or button == 3:     
        scaledx = int(x / TileSize)
        scaledy = int(y / TileSize)
        if Mode == 0:
            if button == 1:
                Tiles[scaledx][scaledy] = Tile(1, solid=True)
            elif button == 3:
                Tiles[scaledx][scaledy] = Tile(0)
        elif Mode == 1:
            currentTile = Tiles[scaledx][scaledy]
            if not currentTile.solid:
                pressure = currentTile.get_pressure()
                delta = 0.5
                if button == 1:
                    currentTile.set_pressure(pressure+delta)
                elif button == 3:
                    currentTile.set_pressure(pressure-delta)
            #add air molecules to the selected tile

def one_iteration(a, new_state):
    # parallel(delayed(one_column)(col, a, new_state) for col in range(tiles_width))
    # Parallel(n_jobs=2, require='sharedmem') (delayed(one_column)(col, a, new_state) for col in range(tiles_width))
    for col in range(tiles_width):
        one_column(col, a, new_state)

def one_column(col, a, new_state):
    for row in range(tiles_height):
        tile = Tiles[col][row]
        if tile.solid: continue
        calc = 0
        neighbors = 0
        if col - 1 > 0 and not Tiles[col-1][row].solid:
            neighbors += 1
            calc += new_state[col-1 + row*tiles_width]
        if col + 1 < tiles_width and not Tiles[col+1][row].solid:
            neighbors += 1
            calc += new_state[col+1 + row*tiles_width]
        if row - 1 > 0 and not Tiles[col][row-1].solid:
            neighbors += 1
            calc += new_state[col + (row-1)*tiles_width]
        if row + 1 < tiles_height and not Tiles[col][row+1].solid:
            neighbors += 1
            calc += new_state[col + (row+1)*tiles_width]
        if not neighbors: 
            new_state[col + row*tiles_width] = tile.num_moles
            continue
        calc *= a
        calc = (tile.num_moles + calc) / (1+neighbors*a)
        new_state[col + row*tiles_width] = calc

def simulate():
    if not SimulationActive: return
    t_start = time.perf_counter()
    #new_state = copy.deepcopy(Tiles)
    # new_state = np.zeros(tiles_width*tiles_height)
    new_state = [0] * tiles_width * tiles_height #somehow faster to access
    for i in range(tiles_width*tiles_height):
        col = i % tiles_width
        row = int(i / tiles_width)
        new_state[i] = Tiles[col][row].num_moles
    t_copy = time.perf_counter()
    diff = 250
    dt = 1/30
    a = dt*diff
    iterations = 10
    # with Parallel(n_jobs=2, require='sharedmem') as parallel:
    for k in range(iterations): #iterate to make sure it doesn't go crazy
        one_iteration(a, new_state)
    t_calc = time.perf_counter()
    #when done, the new_state becomes the current state
    for i in range(tiles_width*tiles_height):
        col = i % tiles_width
        row = int(i / tiles_width)
        m = new_state[i]
        if m < 0.05: m = 0
        Tiles[col][row].set_moles(m)
    t_done = time.perf_counter()
    print(f'Copy: {t_copy-t_start} Calc: {t_calc-t_copy} Finish: {t_done-t_calc} Total: {t_done-t_start}')


def simulation_thread():
    while True:
        simulate()
        time.sleep(0.001)

def main():
    global SimulationActive
    Texts['txt_mode'] = Text('txt_mode', 'Tile Mode', (10, 10), color=COLORS.WHITE)
    Texts['txt_info1'] = Text('txt_info1', 'Pressure: 0 atm', (10, 40), height=25, color=COLORS.WHITE)
    Texts['txt_info2'] = Text('txt_info2', 'Temp: 0 C', (10, 60), height=25, color=COLORS.WHITE)
    Texts['txt_info3'] = Text('txt_info3', 'Moles: 0', (10, 80), height=25, color=COLORS.WHITE)
    Texts['txt_fps'] = Text('txt_fps', 'FPS: 0', (10, 100), height=25, color=COLORS.WHITE)
    dragging = False
    simThread = threading.Thread(target=simulation_thread, daemon=True)
    simThread.start()
    counter = 0
    while True:
        counter += 1
        t_start = time.perf_counter()
        if SimulationActive:
            # simulate()
            pos = pygame.mouse.get_pos()
            update_info(pos[0], pos[1])
        t_simulate = time.perf_counter()
        draw_tiles(display)
        for _, text in Texts.items():
            text.draw(display)
        pygame.display.update()
        t_draw = time.perf_counter()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            elif event.type == MOUSEBUTTONDOWN:
                x = event.pos[0]
                y = event.pos[1]
                handle_mouse(x, y, event.button)
                update_info(x, y)
                dragging = True
            elif event.type == MOUSEBUTTONUP:
                dragging = False
            elif event.type == MOUSEMOTION:
                x = event.pos[0]
                y = event.pos[1]
                update_info(x, y)
                if dragging:
                    button = 0
                    if event.buttons[0]: button = 1
                    elif event.buttons[2]: button = 3
                    handle_mouse(x, y, button)
            elif event.type == KEYUP:
                if event.key == K_1:
                    update_mode(0)
                elif event.key == K_2:
                    update_mode(1)
                elif event.key == K_SPACE:
                    SimulationActive = not SimulationActive

            # print(event)
        t_event = time.perf_counter()
        clock.tick(30)
        t_final = time.perf_counter()
        if counter >= 10:
            print(f'Sim: {t_simulate-t_start} Draw: {t_draw-t_simulate} Event: {t_event-t_draw} Tick: {t_final-t_event} Total: {t_final-t_start}')
            counter = 0

main()
print('done')