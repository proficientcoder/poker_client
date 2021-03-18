import pygame
import time
import os
import pyperclip
import json
from multiprocessing import Process
import requests
from pygame.constants import MOUSEBUTTONUP, KEYDOWN, K_BACKSPACE
from inc.table import tableMain
import inc.support as support
from inc.pygameDropDown import DropDown
from inc.pygameforms import pygameButton
from inc.pygameforms import pygameTextField
from inc.pygameforms import pygameSlider

selected_table = None
key_color = (0, 0, 0)
ses = requests.Session()
result = None
tableSize = 2
buyinSize = 40


def callbackCreateButton():
    createRect = pygame.Rect(11, 61,240,80)
    if createRect.collidepoint(pygame.mouse.get_pos()):
        try:
            _result = ses.get(f'{support.host}/poker/tableCreate/{tableSize}/')
            _result = _result.json()
        except json.decoder.JSONDecodeError:
            pass

def callbackJoinButton():
    _result = ses.get(f'{support.host}/poker/tableJoin/{selected_table}/{buyinSize}/',
                         params={'key': support.key})
    _result = _result.json()

def callbackViewButton():
    if selected_table:
        tableProcess = Process(target=tableMain, args=(selected_table,))
        tableProcess.start()

def callbackKeyButton():
    global key_color
    support.key = pyperclip.paste()
    if os.getenv("DEVELOPMENT_MODE", "False") == "True":
        support.cfg['development'] = support.key
    else:
        support.cfg['production'] = support.key
    with open('..\key.txt', 'w') as f:
        json.dump(support.cfg, f)
    if support.test_key():
        key_color = (0, 255, 0)
    else:
        key_color = (255, 0, 0)


def lobbyMain():
    global key_color, ses, result, tableSize, selected_table, buyinSize

    pygame.init()
    pygame.font.init()
    myfont3 = pygame.font.SysFont('arial', 26)

    if support.test_key():
        key_color = (0, 255, 0)
    else:
        key_color = (255, 0, 0)

    # Define color
    COLOR_INACTIVE = (100, 80, 255)
    COLOR_ACTIVE = (100, 200, 255)
    COLOR_LIST_INACTIVE = (255, 100, 100)
    COLOR_LIST_ACTIVE = (255, 150, 150)

    menuTableSize = DropDown(
        [COLOR_INACTIVE, COLOR_ACTIVE],
        [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
        220, 150, 150, 30,
        pygame.font.SysFont(None, 30),
        "2 Players", ["2 Players", "3 Players"])

    menubuyinSize = DropDown(
        [COLOR_INACTIVE, COLOR_ACTIVE],
        [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
        10, 150, 150, 30,
        pygame.font.SysFont(None, 30),
        "40 big blind", ["40 big blind", "100 big blind"])

    createButton = pygameButton((20, 75),
                                (240, 50),
                                (64, 64, 64),
                                (192, 192, 192),
                                'CREATE TABLE',
                                pygame.font.SysFont('arial', 26),
                                callbackCreateButton)

    joinButton = pygameButton((290, 75),
                              (240, 50),
                              (64, 64, 64),
                              (192, 192, 192),
                              'JOIN TABLE',
                              pygame.font.SysFont('arial', 26),
                              callbackJoinButton)

    viewButton = pygameButton((560, 75),
                              (240, 50),
                              (64, 64, 64),
                              (192, 192, 192),
                              'VIEW TABLE',
                              pygame.font.SysFont('arial', 26),
                              callbackViewButton)

    keyButton = pygameButton((830, 75),
                              (240, 50),
                              (64, 64, 64),
                              (192, 192, 192),
                              'PASTE KEY',
                              pygame.font.SysFont('arial', 26),
                              callbackKeyButton)

    size = (1440, 810)
    screen = pygame.display.set_mode(size)#, pygame.RESIZABLE)
    username = support.cfg['username']
    pygame.display.set_caption(f'Public Exchange Poker - {username}')

    terminated = False
    clock = pygame.time.Clock()

    rows = []
    t = 0
    while not terminated:
        screen.fill(0)
        allevents = pygame.event.get()

        selected_option = menuTableSize.update(allevents)
        if selected_option >= 0:
            tableSize = selected_option + 2

        selected_option = menubuyinSize.update(allevents)
        if selected_option >= 0:
            if selected_option == 0:
                buyinSize = 40
            if selected_option == 1:
                buyinSize = 100

        createButton.doEvents(allevents)
        joinButton.doEvents(allevents)
        viewButton.doEvents(allevents)
        keyButton.doEvents(allevents)

        for event in allevents:
            if event.type == pygame.QUIT:
                terminated = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    for trect in rows:
                        if trect[1].collidepoint(pygame.mouse.get_pos()):
                            selected_table = trect[0]

        if t == 0:
            if tableSize:
                tables = ses.get(f'{support.host}/poker/listTables/{tableSize}/')
                tables = tables.json()
            else:
                tables = {'tables': []}

        color1 = (192, 192, 192)

        y = 214

        s = 'Table ID'
        strImg = myfont3.render(s, True, color1)
        support.center_blit(screen, strImg, (45, y))

        s = 'Seats'
        strImg = myfont3.render(s, True, color1)
        support.center_blit(screen, strImg, (145, y))

        rows = []
        for r in tables['tables']:
            y += 28

            s = str(r['id'])
            strImg = myfont3.render(s, True, color1)
            support.center_blit(screen, strImg, (45, y))

            s = str(r['seated']) + '/' + str(r['size'])
            strImg = myfont3.render(s, True, color1)
            support.center_blit(screen, strImg, (145, y))

            rows.append((r['id'],pygame.Rect(0, y-14, 720, 28)))

            if r['id'] == selected_table:
                pygame.draw.rect(screen, (192, 0, 0), rows[-1][1], 1)

        # Key
        fold_button = myfont3.render(support.key, True, key_color)
        support.center_blit(screen, fold_button, (720, 30))

        # Dropdowns
        keyButton.draw(screen)
        viewButton.draw(screen)
        joinButton.draw(screen)
        createButton.draw(screen)
        menubuyinSize.draw(screen)
        menuTableSize.draw(screen)

        # Draw the frame and do time management
        pygame.display.flip()
        clock.tick(60)
        t += 1
        if t > 30:
            t = 0

    pygame.quit()

