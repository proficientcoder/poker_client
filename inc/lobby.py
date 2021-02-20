import pygame
import time
import requests
from pygame.constants import MOUSEBUTTONUP, KEYDOWN, K_BACKSPACE

import inc.support as support


def lobbyMain():
    pygame.init()
    pygame.font.init()
    myfont3 = pygame.font.SysFont('arial', 26)
    actionButton = pygame.image.load('static/action-button.png')

    ses = requests.Session()

    size = (1440, 810)
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    pygame.display.set_caption("Public-exchange.com")

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
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    if len(support.key) > 0:
                        support.key = support.key[:-1]
                else:
                    support.key += event.unicode

        if t == 0:
            result = ses.get(f'http://{support.host}/poker/listTables/')
            result = result.json()

        color1 = (192, 192, 192)

        y = 214
        s = 'Table ID'
        strImg = myfont3.render(s, True, color1)
        support.center_blit(screen, strImg, (45, y))
        rows = []
        for r in result['tables']:
            y += 28
            s = str(r['id'])
            strImg = myfont3.render(s, True, color1)
            support.center_blit(screen, strImg, (45, y))
            rows.append((r['id'],pygame.Rect(0, y-14, 720, 28)))

            if r['id'] == selected:
                pygame.draw.rect(screen, (192, 0, 0), rows[-1][1], 1)

        support.center_blit(screen, actionButton, (130, 100))
        fold_button = myfont3.render('CREATE TABLE', True, (192,192,192))
        support.center_blit(screen, fold_button, (130, 100))

        support.center_blit(screen, actionButton, (400, 100))
        fold_button = myfont3.render('JOIN TABLE', True, (192,192,192))
        support.center_blit(screen, fold_button, (400, 100))

        # Key
        fold_button = myfont3.render(support.key, True, (192,192,192))
        support.center_blit(screen, fold_button, (720, 30))

        if time.time() % 1 > 0.5:
            pygame.draw.rect(screen, (192,192,192), pygame.Rect(300,10,840,40), 1)


        pygame.display.flip()
        clock.tick(60)

        t += 1
        if t > 30:
            t = 0

    pygame.quit()

