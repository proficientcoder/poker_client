import pygame
import requests
from multiprocessing import Process
import time

from inc.support import rotate, center_blit, get_line


def main(tableId):
    pygame.init()
    pygame.font.init()
    myfont = pygame.font.SysFont('arial', 38)
    myfont2 = pygame.font.SysFont('arial', 20)
    myfont3 = pygame.font.SysFont('arial', 56)
    myfont4 = pygame.font.SysFont('arial', 28)

    ses = requests.Session()

    size = (1440, 810)
    aspect = size[0] / size[1]

    background = pygame.image.load('static/background.png')
    seat = pygame.image.load('static/seat.png')
    button = pygame.image.load('static/button.png')
    cardSmallFront = pygame.image.load('static/card-small-front.png')
    cardBigFront = pygame.image.load('static/card-big-front.png')
    actionButton = pygame.image.load('static/action-button.png')
    betSlider = pygame.image.load('static/bet-slider.png')
    slider = pygame.image.load('static/slider.png')

    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    pygame.display.set_caption("Public-exchange.com")

    terminated = False
    clock = pygame.time.Clock()

    while not terminated:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminated = True

        center_blit(screen, background, (size[0] / 2, size[1] / 2))

        result = ses.get(f'http://127.0.0.1:8000/poker/tableState/{tableId}/')
        result = result.json()

        center = int(size[0] / 2), int(size[1] / 2) - 40
        dist = 450

        seatPositions = []
        buttonPositions = []
        moneyPositions = []
        seats = result['nrOfSeats']
        org = (center[0], center[1] + dist)

        for i in range(0, seats):
            r = (360/seats)*i
            w = rotate(center, org, r)
            w[0] = ((w[0] - center[0]) * aspect) + center[0]
            points = get_line(center[0], center[1], int(w[0]), int(w[1]))
            for j in range(0, len(points)):
                c = background.get_at(points[j])
                if c == (128, 128, 128, 255):
                    seatPositions.append(points[j])
                    buttonPositions.append(points[int(j * 0.8)])
                    moneyPositions.append(points[int(j * 0.5)])
                    break

        for i in range(0, seats):
            seatp = seatPositions[i]
            center_blit(screen, seat, seatp)

            if result['players'][i] is not None:
                if result['players'][i]['cards'] is not None:
                    c1 = result['players'][i]['cards'][0][0]
                    s1 = result['players'][i]['cards'][0][1]
                    c2 = result['players'][i]['cards'][1][0]
                    s2 = result['players'][i]['cards'][1][1]

                    if s1 in ['♠','♣']:
                        color1 = (0,0,0)
                    else:
                        color1 = (255,0,0)

                    if s2 in ['♠','♣']:
                        color2 = (0,0,0)
                    else:
                        color2 = (255,0,0)

                center_blit(screen, cardSmallFront, (seatp[0] - 20, seatp[1] - 54))

                card1 = myfont.render(c1, True, color1)
                center_blit(screen, card1, (seatp[0] - 21, seatp[1] - 66))

                suit1 = myfont.render(s1, True, color1)
                center_blit(screen, suit1, (seatp[0] - 20, seatp[1] - 41))

                center_blit(screen, cardSmallFront, (seatp[0] + 20, seatp[1] - 54))

                card2 = myfont.render(c2, True, color2)
                center_blit(screen, card2, (seatp[0] + 19, seatp[1] - 66))

                suit2 = myfont.render(s2, True, color2)
                center_blit(screen, suit2, (seatp[0] + 20, seatp[1] - 41))

                if result['players'][i]['is_dealer'] == True:
                    buttonp = buttonPositions[i]
                    center_blit(screen, button, buttonp)

                txt = result['players'][i]['name']
                name = myfont2.render(txt, True, (192,192,192))
                center_blit(screen, name, (seatp[0] + 0, seatp[1] - 13))

                money = myfont2.render(result['players'][i]['balance'], True, (192,192,192))
                center_blit(screen, money, (seatp[0] + 0, seatp[1] + 12))

                if result['players'][i]['last_bet'] != '':
                    bet = myfont2.render(result['players'][i]['last_bet'], True, (192,192,192))
                    center_blit(screen, bet, moneyPositions[i])

            else:
                name = myfont2.render('Empty seat', True, (192,192,192))
                center_blit(screen, name, (seatp[0] + 0, seatp[1] - 13))


        for i in range(0, 5):
            if result['board'][i] is not None:
                center_blit(screen, cardBigFront, (center[0] + (i * 65) - 130, center[1] - 25))

                card2 = myfont3.render('K', True, (255,0,0))
                center_blit(screen, card2, (center[0] + (i * 65) - 131, center[1] - 16 - 25))

                suit2 = myfont3.render('♦', True, (255,0,0))
                center_blit(screen, suit2, (center[0] + (i * 65) - 130, center[1] + 18 - 25))


        pot = result['pot']
        bet = myfont2.render(f'Total pot: {pot}', True, (192,192,192))
        center_blit(screen, bet, (center[0], center[1] + 75 - 25))

        if 'FOLD' in result['actions']:
            center_blit(screen, actionButton, (125, 760))
            fold_button = myfont4.render('FOLD', True, (192,192,192))
            center_blit(screen, fold_button, (125, 760))

        if 'CALL' in result['actions']:
            center_blit(screen, actionButton, (375, 760))
            call_button = myfont4.render('CALL 100', True, (192,192,192))
            center_blit(screen, call_button, (375, 760))

        if 'RAISE' in result['actions']:
            center_blit(screen, actionButton, (625, 760))
            raise_button = myfont4.render('RAISE 200', True, (192,192,192))
            center_blit(screen, raise_button, (625, 760))

        if 'BET' in result['actions'] or 'RAISE' in result['actions']:
            center_blit(screen, betSlider, (1095, 760))
            raise_m = myfont4.render('300', True, (192,192,192))
            center_blit(screen, raise_m, (845, 760))

            center_blit(screen, slider, (1000, 763))

        pygame.display.flip()
        clock.tick(2)

pygame.quit()


if __name__ == '__main__':
    tables = []

    while True:
        results = requests.get('http://127.0.0.1:8000/poker/listMyTables/')
        results = results.json()
        results = results['tables']

        nt = []
        for t in tables:
            if t[1].is_alive():
                nt.append(t)
        tables = nt

        for r in results:
            found = False
            for t in tables:
                if t[0] == r:
                    found = True

            if found == False:
                tableId = r
                tableProcess = Process(target=main, args=(tableId,))
                tableProcess.start()
                tables.append([tableId, tableProcess])

        time.sleep(5)