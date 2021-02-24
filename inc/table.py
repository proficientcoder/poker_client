import pygame
import requests
from pygame.constants import MOUSEBUTTONUP

import inc.support as support


def tableMain(tableId):
    pygame.init()
    pygame.font.init()

    white = (255, 255, 255)
    black = (0, 0, 0)
    red = (255, 0, 0)

    tableRingColor = (128, 128, 128, 255)   # Used to detect edge of table

    playerCardFont = pygame.font.SysFont('arial', 36)
    playerInfoFont = pygame.font.SysFont('arial', 20)
    boardCardFont = pygame.font.SysFont('arial', 56)
    actionButtonFont = pygame.font.SysFont('arial', 28)

    http_session = requests.Session()

    imgBackground = pygame.image.load('static/background.png')
    imgSeat = pygame.image.load('static/seat.png')
    imgButton = pygame.image.load('static/button.png')
    imgCardSmallFront = pygame.image.load('static/card-small-front.png')
    imgCardSmallBack = pygame.image.load('static/card-small-back.png')
    imgCardBigFront = pygame.image.load('static/card-big-front.png')
    imgActionButton = pygame.image.load('static/action-button.png')
    imgBetSlider = pygame.image.load('static/bet-slider.png')
    imgSlider = pygame.image.load('static/slider.png')

    sliderMin = 970
    sliderMax = 1380
    sliderPos = 970
    sliderValue = 0

    canvasSize = (1440, 810)
    screen = pygame.display.set_mode(canvasSize, pygame.RESIZABLE)
    pygame.display.set_caption("Public-exchange.com")

    terminated = False
    clock = pygame.time.Clock()

    canFold = False
    canCall = False
    canCheck = False
    canRaise = False
    t = 0
    while not terminated:
        screen.fill(0)
        support.center_blit(screen, imgBackground, (canvasSize[0] / 2, canvasSize[1] / 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminated = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    fold_rect = pygame.Rect(6, 720, 240, 80)
                    if fold_rect.collidepoint(pygame.mouse.get_pos()) and canFold:
                        http_session.get(f'http://{support.host}/poker/actionFold/{tableId}/', params={'key': support.key})
                        print('Fold')
                    if fold_rect.collidepoint(pygame.mouse.get_pos()) and canCheck:
                        http_session.get(f'http://{support.host}/poker/actionCheck/{tableId}/', params={'key': support.key})
                        print('Check')
                    call_rect = pygame.Rect(256, 720, 240, 80)
                    if call_rect.collidepoint(pygame.mouse.get_pos()) and canCall:
                        http_session.get(f'http://{support.host}/poker/actionCall/{tableId}/', params={'key': support.key})
                        print('Call')
                    raise_rect = pygame.Rect(506, 720, 240, 80)
                    if raise_rect.collidepoint(pygame.mouse.get_pos()) and canRaise:
                        #http_session.get(f'http://{support.host}/poker/actionRaise/{tableId}/', params={'key': support.key})
                        print('Raise')
                    slider_rect = pygame.Rect(sliderMin, 720, sliderMax-sliderMin, 80)
                    if slider_rect.collidepoint(pygame.mouse.get_pos()) and canRaise:
                        x, y = pygame.mouse.get_pos()
                        sliderPos = x
                        print('slide')

        # Get actual table state
        if t == 0:
            result = http_session.get(f'http://{support.host}/poker/tableState/{tableId}/', params={'key': support.key})
            result = result.json()

        # Raytrace seat positions
        tableCenter = int(canvasSize[0] / 2), int(canvasSize[1] / 2) - 40
        sweepRange = 450

        seatPositions = [None]
        buttonPositions = [None]
        moneyPositions = [None]

        nrOfSeats = result['nrOfSeats']
        firstRay = (tableCenter[0], tableCenter[1] + sweepRange)
        aspect = canvasSize[0] / canvasSize[1]

        for i in range(1, nrOfSeats+1):
            angle = (360 / nrOfSeats) * (i - 1)
            newRay = support.rotate(tableCenter, firstRay, angle)

            # Do some aspect ratio stretching
            newRay[0] = ((newRay[0] - tableCenter[0]) * aspect) + tableCenter[0]

            # Get all the points from the center of the table to
            rayPoints = support.get_line(tableCenter[0], tableCenter[1], int(newRay[0]), int(newRay[1]))
            for j in range(0, len(rayPoints)):
                if imgBackground.get_at(rayPoints[j]) == tableRingColor:
                    seatPositions.append(rayPoints[j])
                    buttonPositions.append(rayPoints[int(j * 0.8)])
                    moneyPositions.append(rayPoints[int(j * 0.5)])
                    break

        # Paint in the seats
        for i in range(1, nrOfSeats+1):
            seatPosition = seatPositions[i]
            support.center_blit(screen, imgSeat, seatPosition)

            if result['players'][i] is not None:
                if result['players'][i]['cards'] is not None:
                    if result['players'][i]['cards'] == '':
                        support.center_blit(screen, imgCardSmallBack, (seatPosition[0] - 20, seatPosition[1] - 54))
                        support.center_blit(screen, imgCardSmallBack, (seatPosition[0] + 20, seatPosition[1] - 54))
                    else:
                        c1 = result['players'][i]['cards'][0]
                        s1 = result['players'][i]['cards'][1]
                        c2 = result['players'][i]['cards'][2]
                        s2 = result['players'][i]['cards'][3]

                        if s1 in 'SC':
                            color1 = black
                        else:
                            color1 = red

                        if s2 in 'SC':
                            color2 = black
                        else:
                            color2 = red

                        support.center_blit(screen, imgCardSmallFront, (seatPosition[0] - 20, seatPosition[1] - 54))

                        card1 = playerCardFont.render(c1, True, color1)
                        support.center_blit(screen, card1, (seatPosition[0] - 21, seatPosition[1] - 67))

                        suit1 = playerCardFont.render(support.suitTranslate(s1), True, color1)
                        support.center_blit(screen, suit1, (seatPosition[0] - 20, seatPosition[1] - 40))

                        support.center_blit(screen, imgCardSmallFront, (seatPosition[0] + 20, seatPosition[1] - 54))

                        card2 = playerCardFont.render(c2, True, color2)
                        support.center_blit(screen, card2, (seatPosition[0] + 19, seatPosition[1] - 67))

                        suit2 = playerCardFont.render(support.suitTranslate(s2), True, color2)
                        support.center_blit(screen, suit2, (seatPosition[0] + 20, seatPosition[1] - 40))

                if result['dealer'] == i+1:
                    buttonp = buttonPositions[i]
                    support.center_blit(screen, imgButton, buttonp)

                color = white
                if i+1 == result['next_to_act']:
                    color = red

                txt = result['players'][i]['name']
                name = playerInfoFont.render(txt, True, color)
                support.center_blit(screen, name, (seatPosition[0] + 0, seatPosition[1] - 13))

                money = playerInfoFont.render(result['players'][i]['balance'], True, color)
                support.center_blit(screen, money, (seatPosition[0] + 0, seatPosition[1] + 12))

                if float(result['players'][i]['last_bet']) != 0:
                    bet = playerInfoFont.render(result['players'][i]['last_bet'], True, white)
                    support.center_blit(screen, bet, moneyPositions[i])

            else:
                name = playerInfoFont.render('Empty seat', True, white)
                support.center_blit(screen, name, (seatPosition[0] + 0, seatPosition[1] - 13))


        for j in range(0, len(result['board']), 2):
            card = result['board'][j]
            suit = result['board'][j+1]

            if suit in 'SC':
                color = (0, 0, 0)
            else:
                color = (255, 0, 0)

            i = j / 2
            support.center_blit(screen, imgCardBigFront, (tableCenter[0] + (i * 65) - 130, tableCenter[1] - 25))

            card2 = boardCardFont.render(card, True, color)
            support.center_blit(screen, card2, (tableCenter[0] + (i * 65) - 131, tableCenter[1] - 16 - 25))

            suit2 = boardCardFont.render(support.suitTranslate(suit), True, color)
            support.center_blit(screen, suit2, (tableCenter[0] + (i * 65) - 130, tableCenter[1] + 18 - 25))


        pot = result['pot']
        bet = playerInfoFont.render(f'Total pot: {pot}', True, white)
        support.center_blit(screen, bet, (tableCenter[0], tableCenter[1] + 75 - 25))

        # Actions
        actor = result['next_to_act']
        if result['players'][actor]['name'] == result['you']:

            canFold = False
            if 'FOLD' in result['actions']:
                canFold = True
                support.center_blit(screen, imgActionButton, (125, 760))
                fold_button = actionButtonFont.render('FOLD', True, white)
                support.center_blit(screen, fold_button, (125, 760))

            canCheck = False
            if 'CHECK' in result['actions']:
                canCheck = True
                support.center_blit(screen, imgActionButton, (125, 760))
                fold_button = actionButtonFont.render('Check', True, white)
                support.center_blit(screen, fold_button, (125, 760))

            if 'CALL' in result['actions']:
                canCall = True
                support.center_blit(screen, imgActionButton, (375, 760))
                call_button = actionButtonFont.render('CALL', True, white)
                support.center_blit(screen, call_button, (375, 760))

            canRaise = False
            if 'RAISE' in result['actions']:
                canRaise = True
                support.center_blit(screen, imgActionButton, (625, 760))
                raise_button = actionButtonFont.render('RAISE', True, white)
                support.center_blit(screen, raise_button, (625, 760))

            if 'BET' in result['actions']:
                canRaise = True
                support.center_blit(screen, imgActionButton, (625, 760))
                raise_button = actionButtonFont.render('BET', True, white)
                support.center_blit(screen, raise_button, (625, 760))

            if 'BET' in result['actions'] or 'RAISE' in result['actions']:
                sliderValue = support.translate(sliderPos, sliderMin, sliderMax, float(result['blind'])/2, float(result['players'][actor]['balance']))
                sliderValue = round(sliderValue, 2)

                support.center_blit(screen, imgBetSlider, (1095, 760))
                raise_m = actionButtonFont.render(str(sliderValue), True, white)
                support.center_blit(screen, raise_m, (845, 760))

                support.center_blit(screen, imgSlider, (sliderPos, 763))

        pygame.display.flip()
        clock.tick(30)

        t += 1
        if t > 15:
            t = 0

    pygame.quit()