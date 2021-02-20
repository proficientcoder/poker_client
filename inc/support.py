import math

key = '507a2881-2c1f-4b86-b250-56b0c05932ce'
host = '10.0.0.2:8000'

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