import pygame
import requests
import json
from pygame.constants import MOUSEBUTTONUP

import inc.support as support
from inc.pygameforms import pygameButton
from inc.pygameforms import pygameTextField
from inc.pygameforms import pygameSlider


http_session = requests.Session()
tableId = None
sliderValue = None
bb = None


def callbackFoldButton():
    http_session.get(f'{support.host}/poker/actionFold/{tableId}/', params={'key': support.key})

def callbackCheckButton():
    http_session.get(f'{support.host}/poker/actionCheck/{tableId}/', params={'key': support.key})

def callbackCallButton():
    http_session.get(f'{support.host}/poker/actionCall/{tableId}/', params={'key': support.key})

def callbackBetButton():
    _result = http_session.get(f'{support.host}/poker/actionRaise/{tableId}/{sliderValue}/', params={'key': support.key})
    _result = _result.json()
    print(_result)

def callbackRaiseButton():
    _result = http_session.get(f'{support.host}/poker/actionRaise/{tableId}/{sliderValue}/', params={'key': support.key})
    _result = _result.json()
    print(_result)

def callbackLeaveButton():
    http_session.get(f'{support.host}/poker/tableLeave/{tableId}/', params={'key': support.key})

def callbackJoinButton():
    http_session.get(f'{support.host}/poker/tableJoin/{tableId}/{bb}/', params={'key': support.key})
    exit()


def tableMain(myTableId):
    global tableId, sliderValue, bb

    tableId = myTableId

    pygame.init()
    pygame.font.init()

    white = (255, 255, 255)
    grey = (127, 127, 127)
    black = (0, 0, 0)
    red = (255, 0, 0)

    tableRingColor = (128, 128, 128, 255)   # Used to detect edge of table

    playerCardFont = pygame.font.SysFont('arial', 36)
    playerInfoFont = pygame.font.SysFont('arial', 20)
    boardCardFont = pygame.font.SysFont('arial', 56)

    imgBackground = pygame.image.load('static/background.png')
    imgSeat = pygame.image.load('static/seat.png')
    imgButton = pygame.image.load('static/button.png')
    imgCardSmallFront = pygame.image.load('static/card-small-front.png')
    imgCardSmallBack = pygame.image.load('static/card-small-back.png')
    imgCardBigFront = pygame.image.load('static/card-big-front.png')

    canvasSize = (1440, 810)
    screen = pygame.display.set_mode(canvasSize)
    pygame.display.set_caption("Public Exchange Poker")

    terminated = False
    emptySeat = None
    clock = pygame.time.Clock()

    joinButton = pygameButton((1190, 10),
                              (240, 70),
                              (64, 64, 64),
                              (192, 192, 192),
                              'JOIN',
                              pygame.font.SysFont('arial', 26),
                              callbackJoinButton)

    leaveButton = pygameButton((1190, 10),
                               (240, 70),
                               (64, 64, 64),
                               (192, 192, 192),
                               'LEAVE',
                               pygame.font.SysFont('arial', 26),
                               callbackLeaveButton)

    foldButton = pygameButton((5, 725),
                              (240, 70),
                              (64, 64, 64),
                              (192, 192, 192),
                              'FOLD',
                              pygame.font.SysFont('arial', 26),
                              callbackFoldButton)

    checkButton = pygameButton((5, 725),
                               (240, 70),
                               (64, 64, 64),
                               (192, 192, 192),
                               'CHECK',
                               pygame.font.SysFont('arial', 26),
                               callbackCheckButton)

    callButton = pygameButton((255, 725),
                              (240, 70),
                              (64, 64, 64),
                              (192, 192, 192),
                              'CALL',
                              pygame.font.SysFont('arial', 26),
                              callbackCallButton)

    betButton = pygameButton((505, 725),
                             (240, 70),
                             (64, 64, 64),
                             (192, 192, 192),
                             'BET',
                             pygame.font.SysFont('arial', 26),
                             callbackBetButton)

    raiseButton = pygameButton((505, 725),
                               (240, 70),
                               (64, 64, 64),
                               (192, 192, 192),
                               'RAISE',
                               pygame.font.SysFont('arial', 26),
                               callbackBetButton)

    betSlider = pygameSlider((925, 720),
                             (505, 80),
                             (32, 32, 32),
                             (96, 96, 96),
                             (64, 64, 64),
                             0,
                             100,
                             0)

    seatSlider = pygameSlider((470, 5),
                              (500, 30),
                              (32, 32, 32),
                              (96, 96, 96),
                              (64, 64, 64),
                              0,
                              360,
                              180)

    buyinSlider = pygameSlider((1190, 90),
                               (240, 30),
                               (32, 32, 32),
                               (96, 96, 96),
                               (64, 64, 64),
                               40,
                               100,
                               40)

    canFold = False
    canCall = False
    canCheck = False
    canBet = False
    canRaise = False
    canLeave = False
    canJoin = False

    t = 0
    while not terminated:
        try:
            screen.fill(0)

            support.center_blit(screen, imgBackground, (canvasSize[0] / 2, canvasSize[1] / 2))

            sliderValue = int(betSlider.value)
            allevents = pygame.event.get()

            seatSlider.doEvents(allevents)
            if canBet or canRaise:
                betSlider.doEvents(allevents)
            if canRaise:
                raiseButton.doEvents(allevents)
            if canBet:
                betButton.doEvents(allevents)
            if canCall:
                callButton.doEvents(allevents)
            if canCheck:
                checkButton.doEvents(allevents)
            if canFold:
                foldButton.doEvents(allevents)
            if canLeave:
                leaveButton.doEvents(allevents)
            if canJoin:
                buyinSlider.doEvents(allevents)
                joinButton.doEvents(allevents)

            for event in allevents:
                if event.type == pygame.QUIT:
                    terminated = True

            # Get actual table state
            if t == 0:
                result = http_session.get(f'{support.host}/poker/tableState/{tableId}/', params={'key': support.key})
                result = result.json()

            # Raytrace seat positions
            tableCenter = int(canvasSize[0] / 2), int(canvasSize[1] / 2) - 40
            sweepRange = 450

            seatPositions = []
            buttonPositions = []
            moneyPositions = []

            nrOfSeats = result['nrOfSeats']
            firstRay = (tableCenter[0], tableCenter[1] + sweepRange)
            aspect = canvasSize[0] / canvasSize[1]

            for i in range(0, nrOfSeats):
                angle = (360 / nrOfSeats) * (i - 1) + seatSlider.value
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
            totalPot = 0
            max_bet = 0
            mySeat = None

            for i in range(0, nrOfSeats):
                seatPosition = seatPositions[i]
                support.center_blit(screen, imgSeat, seatPosition)

                if result['players'][i] is not None:
                    if result['players'][i]['name'] == result['you']:
                        mySeat = i
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
                            support.center_blit(screen, suit1, (seatPosition[0] - 19, seatPosition[1] - 40))

                            support.center_blit(screen, imgCardSmallFront, (seatPosition[0] + 20, seatPosition[1] - 54))

                            card2 = playerCardFont.render(c2, True, color2)
                            support.center_blit(screen, card2, (seatPosition[0] + 19, seatPosition[1] - 67))

                            suit2 = playerCardFont.render(support.suitTranslate(s2), True, color2)
                            support.center_blit(screen, suit2, (seatPosition[0] + 21, seatPosition[1] - 40))

                    if result['dealer'] == i:
                        buttonp = buttonPositions[i]
                        support.center_blit(screen, imgButton, buttonp)

                    color = white
                    if i == result['next_to_act']:
                        color = red

                    txt = result['players'][i]['name']
                    name = playerInfoFont.render(txt, True, color)
                    support.center_blit(screen, name, (seatPosition[0] + 0, seatPosition[1] - 13))

                    money = playerInfoFont.render(str(result['players'][i]['balance']), True, color)
                    support.center_blit(screen, money, (seatPosition[0] + 0, seatPosition[1] + 12))

                    nbet = int(result['players'][i]['new_bet'])
                    pbet = int(result['players'][i]['prev_bet'])
                    max_bet = max(max_bet, nbet)
                    totalPot += nbet + pbet
                    if nbet != 0:
                        bet = playerInfoFont.render(str(nbet), True, white)
                        support.center_blit(screen, bet, moneyPositions[i])

                else:
                    emptySeat = i
                    name = playerInfoFont.render('Empty seat', True, white)
                    support.center_blit(screen, name, (seatPosition[0] + 0, seatPosition[1] - 13))

            pot = playerInfoFont.render(f'Total pot: {totalPot}', True, white)
            support.center_blit(screen, pot, (tableCenter[0], tableCenter[1] + 75 - 25))

            if result['board']:
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
                    support.center_blit(screen, card2, (tableCenter[0] + (i * 65) - 131, tableCenter[1] - 17 - 25))

                    suit2 = boardCardFont.render(support.suitTranslate(suit), True, color)
                    support.center_blit(screen, suit2, (tableCenter[0] + (i * 65) - 129, tableCenter[1] + 19 - 24))

            # Timer
            if 'timer' in result:   # and result['actions']:
                tmr = int(result['timer'])
                tmr = playerInfoFont.render(f'Timeout in: {tmr}', True, white)
                screen.blit(tmr, (0, 0))

            # Log
            y = 20
            for l in result['log']:
                y += 20
                tmr = playerInfoFont.render(l, True, grey)
                screen.blit(tmr, (0, y))

            # Actions
            actor = result['next_to_act']
            canFold = False
            canCheck = False
            canCall = False
            canRaise = False
            canBet = False
            if result['players'][actor]:
                if result['players'][actor]['name'] == result['you']:
                    if 'FOLD' in result['actions']:
                        canFold = True

                    if 'CHECK' in result['actions']:
                        canCheck = True

                    if 'CALL' in result['actions']:
                        canCall = True

                    if 'RAISE' in result['actions']:
                        canRaise = True

                    if 'BET' in result['actions']:
                        canBet = True

                    toCall = max_bet - int(result['players'][actor]['new_bet'])
                    minRaise = toCall + float(result['blind'])/2
                    minRaise = min(minRaise, result['players'][actor]['balance'])
                    betSlider.min = minRaise
                    betSlider.max = result['players'][actor]['balance']

            canLeave = False
            if mySeat is not None:
                canLeave = True

            canJoin = False
            if mySeat is None and emptySeat:
                canJoin = True

            if canJoin:
                buyinSlider.draw(screen)
                bb = int(buyinSlider.value)
                joinButton.text = 'JOIN with ' + str(bb) + ' BB'
                joinButton.draw(screen)
            if canLeave:
                leaveButton.draw(screen)
            if canFold:
                foldButton.draw(screen)
            if canCheck:
                checkButton.draw(screen)
            if canCall:
                callButton.draw(screen)
            if canBet:
                betButton.draw(screen)
            if canRaise:
                raiseButton.draw(screen)
            if canRaise or canBet:
                s = str(int(round(betSlider.value, 0)))
                img_v = playerCardFont.render(s, True, white)
                support.center_blit(screen, img_v, (845, 760))
                betSlider.draw(screen)

            seatSlider.draw(screen)

            pygame.display.flip()
            clock.tick(30)

            t += 1
            if t > 15:
                t = 0
        except:
            json.decoder.jsondecodeerror
            continue

    pygame.quit()