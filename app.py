import copy
import math

import pygame
from pygame.display import set_mode
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
        column.append(Tile(0))


pygame.init()
display = pygame.display.set_mode(WindowSize)
clock = pygame.time.Clock()

def get_text(name):
    if name in Texts:
        return Texts[name]
    return None

def draw_tiles(display):
    for col in range(tiles_width):
        for row in range(tiles_height):
            tile = Tiles[col][row]
            if tile.tile_id == 1:
                display.fill(COLORS.GREEN, Rect(col*TileSize, row*TileSize, TileSize, TileSize))
            else:
                p = tile.get_pressure()
                fill = int(min(255, 255*math.sqrt(p)))
                display.fill(Color(0, fill, fill), Rect(col*TileSize, row*TileSize, TileSize, TileSize))

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
                if button == 1:
                    currentTile.set_pressure(pressure+0.1)
                elif button == 3:
                    currentTile.set_pressure(pressure-0.1)
            #add air molecules to the selected tile

def move_air_to_neighbor(new_state, x, y, n_x, n_y, currentpressure=-1, num_neighbors=4):
    neighbor = Tiles[n_x][n_y]
    if neighbor.solid: return
    tile = Tiles[x][y]
    if currentpressure < 0:
        currentpressure = tile.get_pressure()
    n_pressure = neighbor.get_pressure()
    if n_pressure < currentpressure:
        #some molecules move
        max_moles = tile.num_moles / (num_neighbors * 2)
        diff = math.sqrt(2*abs(n_pressure - currentpressure))
        moved = min(max_moles * diff, max_moles)
        new_state[n_x][n_y].num_moles += moved
        new_state[x][y].num_moles -= moved

def simulate():
    global Tiles
    new_state = copy.deepcopy(Tiles)
    for col in range(tiles_width):
        for row in range(tiles_height):
            tile = Tiles[col][row]
            if tile.solid or tile.num_moles < 0.01: continue
            currentpressure = Tiles[col][row].get_pressure()
            neighbors = 0
            if col - 1 > 0 and not Tiles[col-1][row].solid: neighbors += 1
            if col + 1 < tiles_width and not Tiles[col+1][row].solid: neighbors += 1
            if row - 1 > 0 and not Tiles[col][row-1].solid: neighbors += 1
            if row + 1 < tiles_height and not Tiles[col][row+1].solid: neighbors += 1
            #for each tile, check the pressure against the neighbors
            #if the neighbor tiles have lower pressure, move some molecules over (at most 1/8?)
            if col - 1 > 0: move_air_to_neighbor(new_state, col, row, col-1, row, currentpressure, neighbors)
            if col + 1 < tiles_width: move_air_to_neighbor(new_state, col, row, col+1, row, currentpressure, neighbors)
            if row - 1 > 0: move_air_to_neighbor(new_state, col, row, col, row-1, currentpressure, neighbors)
            if row + 1 < tiles_height: move_air_to_neighbor(new_state, col, row, col, row+1, currentpressure, neighbors)
    #when done, the new_state becomes the current state
    Tiles = new_state

                    

def main():
    global SimulationActive
    Texts['txt_mode'] = Text('txt_mode', 'Tile Mode', (10, 10), color=COLORS.WHITE)
    Texts['txt_info1'] = Text('txt_info1', 'Pressure: 0 atm', (10, 40), height=25, color=COLORS.WHITE)
    Texts['txt_info2'] = Text('txt_info2', 'Temp: 0 C', (10, 60), height=25, color=COLORS.WHITE)
    Texts['txt_info3'] = Text('txt_info3', 'Moles: 0', (10, 80), height=25, color=COLORS.WHITE)
    while True:
        if SimulationActive:
            simulate()
            pos = pygame.mouse.get_pos()
            update_info(pos[0], pos[1])
        draw_tiles(display)
        for _, text in Texts.items():
            text.draw(display)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            elif event.type == MOUSEBUTTONUP:
                x = event.pos[0]
                y = event.pos[1]
                handle_mouse(x, y, event.button)
                update_info(x, y)
            elif event.type == MOUSEMOTION:
                update_info(event.pos[0], event.pos[1])
            elif event.type == KEYUP:
                if event.key == K_1:
                    update_mode(0)
                elif event.key == K_2:
                    update_mode(1)
                elif event.key == K_SPACE:
                    SimulationActive = not SimulationActive

            # print(event)
        clock.tick(60)

main()
print('done')