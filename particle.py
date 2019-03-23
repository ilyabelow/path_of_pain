import pygame
import constants
import base


# TODO CLEAR UP THIS FILE

class Particle(base.AdvancedSprite):
    def __init__(self, countdown):
        base.AdvancedSprite.__init__(self)
        # TODO move to clocks?
        self.countdown = countdown

    # TODO move shared functionality here (countdown of death for example)


# TODO rename and make more general?
class Blood(Particle):
    def __init__(self, position, speed, lifetime, fadeout, color):
        Particle.__init__(self, lifetime)
        # TODO more customisable blood
        self.color = color
        self.speed = speed
        self.fadeout = fadeout
        self.pos = position

    def update(self, *args):
        # MOVING
        # TODO optimize positioning
        self.pos.x += self.speed.x
        self.pos.y += self.speed.y
        # TIMER HANDLING
        # TODO make countdown class?
        self.countdown -= self.fadeout
        if self.countdown < 0:
            self.kill()
            return
        self.fetch_layer(self.pos.y)

    def draw(self, screen, window):
        image = pygame.Surface((int(self.countdown * 2), int(self.countdown * 2)), pygame.SRCALPHA, 32)
        pygame.draw.circle(image, self.color, [i // 2 for i in image.get_size()], int(self.countdown))
        return screen.blit(image, (self.pos.x - window.x, self.pos.y - window.y))


class Exclamation(Particle):
    def __init__(self, position, lifetime):
        Particle.__init__(self, lifetime)
        # TODO move font to game obj?
        font = pygame.font.Font(None, 80)

        self.image = font.render("!", 3, constants.C_BLACK)
        self.rect = self.image.get_rect(centerx=position.x, centery=position.y)
        self.y = 3000  # +inf

    def update(self, *args):
        # TODO this clearly can move to Clock!
        if self.countdown >= 0:
            if self.countdown == 0:
                self.kill()
            else:
                pass
            self.countdown -= 1

    def draw(self, screen, window):
        return screen.blit(self.image, (self.rect.x - window.x, self.rect.y - window.y))


class Fade(Particle):
    def __init__(self, duration, to_black):
        Particle.__init__(self, duration)
        self.rect = pygame.Rect(0, 0, 1920, 1080)
        self.to_black = to_black
        self.duration = duration
        self.image = None
        self.y = 5000  # +inf

    def update(self):
        # TIMER HANDLING
        if self.countdown >= 0:
            self.countdown -= 1
        # IMAGE COMPOSING
        self.image = pygame.Surface(self.rect[2:4]).convert_alpha()
        if self.to_black:
            self.image.fill((0, 0, 0, 255 * ((self.duration - self.countdown - 1) / self.duration)))
        else:
            self.image.fill((0, 0, 0, int(255 * ((self.countdown + 1) / self.duration))))

    def draw(self, screen, window):
        return screen.blit(self.image, self.rect)
