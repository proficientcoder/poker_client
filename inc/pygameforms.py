import pygame
import time
import datetime
import string

CHARACTERS = set(string.ascii_letters+string.digits+string.punctuation)

def remap(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class pygameButton:
    rect = None
    color1 = None
    color2 = None
    text = None
    font = None
    callBack = None
    state = False

    def __init__(self, position, size, color1, color2, text, font, callBack):
        self.rect = pygame.Rect(position[0],
                                position[1],
                                size[0],
                                size[1])
        self.color1 = color1
        self.color2 = color2
        self.text = text
        self.font = font
        self.callBack = callBack

    def doEvents(self, events):
        remove = []
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.rect.collidepoint(pygame.mouse.get_pos()):
                        remove.append(event)
                        self.state = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.state:
                            self.state = False
                            self.callBack()

        for r in remove:
            events.remove(r)

    def draw(self, canvas):
        if not self.state:
            pygame.draw.rect(canvas,
                             self.color1,
                             self.rect,
                             0,
                             border_radius=0)

        pygame.draw.rect(canvas,
                         self.color2,
                         self.rect,
                         1,
                         border_radius=0)

        imgText = self.font.render(self.text, True, self.color2)
        text_rect = imgText.get_rect(center=((self.rect.width / 2) + self.rect.left,
                                             (self.rect.height / 2) + self.rect.top))
        canvas.blit(imgText, text_rect)

class pygameTextField:
    rect = None
    color1 = None
    color2 = None
    text = None
    font = None
    callBack = None
    state = False
    cursor = 0


    def __init__(self, position, size, color1, color2, text, font, callBack):
        self.rect = pygame.Rect(position[0],
                                position[1],
                                size[0],
                                size[1])
        self.color1 = color1
        self.color2 = color2
        self.text = text
        self.font = font
        self.offset = 0
        self.callBack = callBack
        self.events = {}

    def doEvents(self, events):
        remove = []
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.rect.collidepoint(pygame.mouse.get_pos()):
                        remove.append(event)
                        self.state = True
                    else:
                        self.state = False
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if not self.rect.collidepoint(pygame.mouse.get_pos()):
                        self.state = False
            if self.state:
                if event.type == pygame.KEYDOWN:
                    if event.unicode in CHARACTERS:
                        e = event.unicode
                    else:
                        e = event.key

                    if e not in self.events:
                        self.events[e] = 0
                if event.type == pygame.KEYUP:
                    if event.unicode in CHARACTERS:
                        e = event.unicode
                    else:
                        e = event.key

                    if e in self.events:
                        del self.events[e]

        to_del = []
        for e, timeout in self.events.items():

            if timeout == 0:
                self.events[e] = time.time_ns() + (8 * 10 ** 8)
            else:
                if time.time_ns() < timeout:
                    continue
                else:
                    self.events[e] = time.time_ns() + (1 * 10 ** 8)

            to_del.append(e)

            if e == pygame.K_LEFT:
                if self.cursor > 0:
                    self.cursor -= 1
            if e == pygame.K_RIGHT:
                if self.cursor < len(self.text):
                    self.cursor += 1
            if e == pygame.K_BACKSPACE:
                if self.cursor > 0:
                    self.text = self.text[:self.cursor - 1] + self.text[self.cursor:]
                    self.cursor -= 1
            if e == pygame.K_DELETE:
                if self.cursor < len(self.text):
                    self.text = self.text[:self.cursor] + self.text[self.cursor + 1:]
            if e == pygame.K_HOME:
                self.cursor = 0
            if e == pygame.K_END:
                self.cursor = len(self.text)
            if e == pygame.K_RETURN:
                self.state = False
                self.callBack()
            if e in CHARACTERS:
                self.text = self.text[:self.cursor] + e + self.text[self.cursor:]
                self.cursor += 1

        for r in remove:
            events.remove(r)

    def draw(self, canvas):
        if self.state:
            color = self.color2
        else:
            color = self.color1

        pygame.draw.rect(canvas,
                         color,
                         self.rect,
                         1,
                         border_radius=0)

        arr = []
        fontHeight = 0
        for t in self.text + ' ':   # +1 for the cursor
            imgText = self.font.render(t, True, color)
            size = imgText.get_size()
            fontHeight = max(size[1], fontHeight)
            arr.append(imgText)

        now = datetime.datetime.now()
        swing = fontHeight / 2
        x = self.rect[0] + 3 + self.offset
        y_center = self.rect[1] + (self.rect[3]/2)
        p = 0
        for a in arr:
            if p == self.cursor:
                if x > self.rect[0]+self.rect[2]-3:
                    self.offset -= 20
                if x < self.rect[0]:
                    self.offset += 20
                if now.microsecond > 500000 and self.state:
                    pygame.draw.line(canvas, color, (x,  y_center - swing), (x, y_center + swing), 1)
            size = a.get_size()
            y = self.rect[1] + (self.rect[3]/2) - (fontHeight/2)
            if x > self.rect[0] and x+size[0] < self.rect[0]+self.rect[2]:
                canvas.blit(a, (x, y))

            x += size[0]
            p += 1

class pygameSlider:
    rect = None
    slider = None
    color1 = None
    color2 = None
    color3 = None
    text = None
    font = None
    callBack = None
    state = False
    min = None
    max = None
    x = None
    value = None

    def __init__(self, position, size, color1, color2, color3, min, max, value):
        self.rect = pygame.Rect(position[0],
                                position[1],
                                size[0],
                                size[1])
        self.slider = self.rect.copy()
        self.slider[2] /= 10

        self.color1 = color1
        self.color2 = color2
        self.color3 = color3
        self.min = min
        self.max = max
        self.value = value
        self.min_x = self.rect[0] + (self.slider[2]/2)
        self.max_x = self.rect[0] + self.rect[2] - (self.slider[2]/2)
        self.value_x = int(remap(self.value, self.min, self.max, self.min_x, self.max_x))
        self.slider[0] = self.value_x - (self.slider[2]/2)


    def doEvents(self, events):
        remove = []
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.rect.collidepoint(pygame.mouse.get_pos()):
                        remove.append(event)
                        self.state = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.state = False

        for r in remove:
            events.remove(r)

        if self.state:
            pos = pygame.mouse.get_pos()
            self.value_x = pos[0]
            self.value_x = max(self.value_x, self.min_x)
            self.value_x = min(self.value_x, self.max_x)
            self.slider[0] = self.value_x - (self.slider[2]/2)

        self.value = remap(self.value_x, self.min_x, self.max_x, self.min, self.max)


    def draw(self, canvas):
        pygame.draw.rect(canvas,
                         self.color1,
                         self.rect,
                         0,
                         border_radius=0)
        pygame.draw.rect(canvas,
                         self.color2,
                         self.rect,
                         1,
                         border_radius=0)

        pygame.draw.rect(canvas,
                         self.color3,
                         self.slider,
                         0,
                         border_radius=0)
        pygame.draw.rect(canvas,
                         self.color2,
                         self.slider,
                         1,
                         border_radius=0)



