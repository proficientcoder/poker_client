import pygame
import requests
from timeit import default_timer as timer
from datetime import timedelta
import math


def rotate(origin, point, angle):
    angle = math.radians(angle)
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return [qx, qy]


def center_blit(screen, grp, cord):
    r = grp.get_rect()
    cord = cord[0] - r.width/2, cord[1] - r.height/2
    screen.blit(grp, cord)


def get_line(x1, y1, x2, y2):
    points = []
    issteep = abs(y2-y1) > abs(x2-x1)
    if issteep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    rev = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        rev = True
    deltax = x2 - x1
    deltay = abs(y2-y1)
    error = int(deltax / 2)
    y = y1
    ystep = None
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
    for x in range(x1, x2 + 1):
        if issteep:
            points.append((y, x))
        else:
            points.append((x, y))
        error -= deltay
        if error < 0:
            y += ystep
            error += deltax
    # Reverse the list if the coordinates were reversed
    if rev:
        points.reverse()
    return points


def translate(value, fromBegin, fromEnd, toBegin, toEnd):
    '''Translates a point from one system to the other. A system is defined (but
     not limited) by a begin- and end-value.
    Parameters:
        value               : The point to be transformed
        fromBegin, fromEnd  : System in which the value parameter is now
        toBegin, toEnd      : System to which value is to be translated

    Returns:
        translated value in the new system

    Notes:
    1. For examele; if you wanted 10 on a scale of 1-10 to be translated to a
       scale of 20-40 you would do:
           v_new = translate(10, 1, 10, 20, 40)
    '''
    leftSpan = fromEnd - fromBegin
    rightSpan = toEnd - toBegin

    valueScaled = float(value - fromBegin) / float(leftSpan)

    return toBegin + (valueScaled * rightSpan)


def main():
    pygame.init()
    pygame.font.init()
    myfont = pygame.font.SysFont('arial', 38)
    myfont2 = pygame.font.SysFont('arial', 20)
    myfont3 = pygame.font.SysFont('arial', 56)

    ses = requests.Session()

    size = (1440, 1080)
    aspect = size[0] / size[1]

    background = pygame.image.load('static/background.png')
    seat = pygame.image.load('static/seat.png')
    button = pygame.image.load('static/button.png')
    cardSmallFront = pygame.image.load('static/card-small-front.png')
    cardBigFront = pygame.image.load('static/card-big-front.png')

    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    pygame.display.set_caption("Public-exchange.com")

    terminated = False
    clock = pygame.time.Clock()

    while not terminated:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminated = True

        center_blit(screen, background, (size[0]/2, size[1]/2))

        # result = ses.get('http://127.0.0.1:8000/poker/tableState/')
        # result = result.json()

        center = int(size[0] / 2), int(size[1] / 2) - 40
        dist = 450

        seatPositions = []
        buttonPositions = []
        moneyPositions = []
        seats = 5  #result['nrOfSeats']
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

        for i in range(0, len(seatPositions)):
            seatp = seatPositions[i]
            center_blit(screen, seat, seatp)

            center_blit(screen, cardSmallFront, (seatp[0] - 20, seatp[1] - 54))

            card1 = myfont.render('A', True, (0,0,0))
            center_blit(screen, card1, (seatp[0] - 21, seatp[1] - 66))

            suit1 = myfont.render('♠', True, (0,0,0))
            center_blit(screen, suit1, (seatp[0] - 20, seatp[1] - 41))

            center_blit(screen, cardSmallFront, (seatp[0] + 20, seatp[1] - 54))

            card2 = myfont.render('K', True, (255,0,0))
            center_blit(screen, card2, (seatp[0] + 19, seatp[1] - 66))

            suit2 = myfont.render('♦', True, (255,0,0))
            center_blit(screen, suit2, (seatp[0] + 20, seatp[1] - 41))

            buttonp = buttonPositions[i]
            center_blit(screen, button, buttonp)

            name = myfont2.render(f'Player {i}', True, (192,192,192))
            center_blit(screen, name, (seatp[0] + 0, seatp[1] - 11))

            money = myfont2.render('$123.45', True, (192,192,192))
            center_blit(screen, money, (seatp[0] + 0, seatp[1] + 13))

            bet = myfont2.render('$12.34', True, (192,192,192))
            center_blit(screen, bet, moneyPositions[i])


        for i in range(0, 5):
            center_blit(screen, cardBigFront, (center[0] + (i*65) - 130, center[1]-25))

            card2 = myfont3.render('K', True, (255,0,0))
            center_blit(screen, card2, (center[0] + (i*65) - 131, center[1]-16-25))

            suit2 = myfont3.render('♦', True, (255,0,0))
            center_blit(screen, suit2, (center[0] + (i*65) - 130, center[1]+18-25))


        bet = myfont2.render('Total pot: $56.78', True, (192,192,192))
        center_blit(screen, bet, (center[0], center[1]+75-25))

        pygame.display.flip()
        clock.tick(30)

pygame.quit()



if __name__ == '__main__':
    main()