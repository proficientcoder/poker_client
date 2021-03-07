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

key_color = (0,0,0)


def lobbyMain():
    global key_color

    pygame.init()
    pygame.font.init()
    myfont3 = pygame.font.SysFont('arial', 26)
    actionButton = pygame.image.load('static/action-button.png')

    ses = requests.Session()

    if support.test_key():
        key_color = (0,255,0)
    else:
        key_color = (255,0,0)

    size = (1440, 810)
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    username = support.cfg['username']
    pygame.display.set_caption(f'Username {username} - Lobby - Holdem poker on public-exchange.com')

    terminated = False
    clock = pygame.time.Clock()

    rows = []
    selected = None
    t = 0
    while not terminated:
        screen.fill(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminated = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    for trect in rows:
                        if trect[1].collidepoint(pygame.mouse.get_pos()):
                            selected = trect[0]
                    createRect = pygame.Rect(11, 61,240,80)
                    if createRect.collidepoint(pygame.mouse.get_pos()):
                        _result = ses.get(f'{support.host}/poker/tableCreate/')
                        _result = _result.json()
                    viewRect = pygame.Rect(281, 61, 240, 80)
                    if viewRect.collidepoint(pygame.mouse.get_pos()):
                        print(selected)
                        if selected:
                            tableProcess = Process(target=tableMain, args=(selected,))
                            tableProcess.start()
                    joinRect = pygame.Rect(551, 61, 240, 80)
                    if joinRect.collidepoint(pygame.mouse.get_pos()):
                        _result = ses.get(f'{support.host}/poker/tableJoin/{selected}/',
                                         params={'key': support.key})
                        _result = _result.json()
                    pasteRect = pygame.Rect(821, 61, 240, 80)
                    if pasteRect.collidepoint(pygame.mouse.get_pos()):
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

        if t == 0:
            result = ses.get(f'{support.host}/poker/listTables/')
            result = result.json()

        color1 = (192, 192, 192)

        y = 214

        s = 'Table ID'
        strImg = myfont3.render(s, True, color1)
        support.center_blit(screen, strImg, (45, y))

        s = 'Seats'
        strImg = myfont3.render(s, True, color1)
        support.center_blit(screen, strImg, (145, y))

        rows = []
        for r in result['tables']:
            y += 28

            s = str(r['id'])
            strImg = myfont3.render(s, True, color1)
            support.center_blit(screen, strImg, (45, y))

            s = str(r['seated']) + '/' + str(r['size'])
            strImg = myfont3.render(s, True, color1)
            support.center_blit(screen, strImg, (145, y))

            rows.append((r['id'],pygame.Rect(0, y-14, 720, 28)))

            if r['id'] == selected:
                pygame.draw.rect(screen, (192, 0, 0), rows[-1][1], 1)

        support.center_blit(screen, actionButton, (130, 100))
        fold_button = myfont3.render('CREATE TABLE', True, (192,192,192))
        support.center_blit(screen, fold_button, (130, 100))

        support.center_blit(screen, actionButton, (400, 100))
        fold_button = myfont3.render('VIEW TABLE', True, (192,192,192))
        support.center_blit(screen, fold_button, (400, 100))

        support.center_blit(screen, actionButton, (670, 100))
        fold_button = myfont3.render('JOIN TABLE', True, (192,192,192))
        support.center_blit(screen, fold_button, (670, 100))

        support.center_blit(screen, actionButton, (940, 100))
        fold_button = myfont3.render('PASTE KEY', True, (192,192,192))
        support.center_blit(screen, fold_button, (940, 100))

        # Key
        fold_button = myfont3.render(support.key, True, key_color)
        support.center_blit(screen, fold_button, (720, 30))

        # Draw the frame and do time management
        pygame.display.flip()
        clock.tick(60)
        t += 1
        if t > 30:
            t = 0

    pygame.quit()

