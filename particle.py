import pygame
import const
import base
import clock


# TODO make base class for particles


# TODO rename and make more general?
class Blood(base.AdvancedSprite):
    def __init__(self, position, speed, size, fadeout, color):
        base.AdvancedSprite.__init__(self)
        # TODO more customisable blood
        self.color = color
        self.speed = speed
        self.fadeout = fadeout
        self.pos = position
        self.size = size

    def update(self, *args):
        self.pos.x += self.speed.x
        self.pos.y += self.speed.y
        self.size -= self.fadeout
        if self.size < 0:
            self.kill()
            return
        self.fetch_layer(self.pos.y)

    def draw(self, screen, window):
        image = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA, 32)
        pygame.draw.circle(image, self.color, [i // 2 for i in image.get_size()], int(self.size))
        return screen.blit(image, (self.pos.x - window.x, self.pos.y - window.y))


class Exclamation(base.AdvancedSprite):
    def __init__(self, pos, lifetime):
        base.AdvancedSprite.__init__(self)
        # TODO move font somewhere in shared place?
        font = pygame.font.Font(None, 80)

        self.image = font.render("!", 3, const.C_BLACK)
        self.rect = self.image.get_rect(centerx=pos.x, centery=pos.y)
        self.y = 3000  # +inf
        self.clock = clock.Clock(self.kill, lifetime)
        self.clock.wind_up()

    def update(self):
        self.clock.tick()

    def draw(self, screen, window):
        return screen.blit(self.image, (self.rect.x - window.x, self.rect.y - window.y))


class Fade(base.AdvancedSprite):
    def __init__(self, duration, to_black, when_stops=None):
        base.AdvancedSprite.__init__(self)
        if when_stops is None:
            when_stops = self.kill
        self.to_black = to_black
        self.duration = duration
        self.y = const.FADE_Y
        self.clock = clock.Clock(when_stops, duration)
        self.clock.wind_up()

    def update(self):
        self.clock.tick()

    def draw(self, screen, window):
        image = pygame.Surface(const.RESOLUTION).convert_alpha()
        if self.to_black:
            image.fill((0, 0, 0, 255 * ((self.duration - self.clock.how_much_is_left() - 1) / self.duration)))
        else:
            image.fill((0, 0, 0, int(255 * ((self.clock.how_much_is_left() + 1) / self.duration))))
        return screen.blit(image, (0, 0))


# 0 - wait, 1 - fade in, 2 - stay, 3 - fade out
class Title(base.AdvancedSprite):
    def __init__(self, image):
        base.AdvancedSprite.__init__(self)
        self.image = image
        self.stage = 0
        self.times = const.fade_in + 5, 20, 30, 20
        self.clock = clock.Clock(self.next_stage)
        self.clock.wind_up(self.times[self.stage])
        self.y = const.HUD_Y

    def update(self):
        self.clock.tick()

    def draw(self, screen, offset):
        if 0 < self.stage:
            temp = self.image.copy()
            alpha = 255
            if self.stage == 1:
                alpha = 255 * (self.times[1] - self.clock.how_much_is_left()) / self.times[1]
            if self.stage == 3:
                alpha = 255 * self.clock.how_much_is_left() / self.times[3]
            temp.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
            return screen.blit(temp,
                               self.image.get_rect(centerx=const.RESOLUTION[0] / 2, bottom=const.RESOLUTION[1] - 25))
        return pygame.Rect(0, 0, 0, 0)

    def next_stage(self):
        self.stage += 1
        if self.stage > 3:
            self.kill()
        else:
            self.clock.wind_up(self.times[self.stage])
