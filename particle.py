import pygame
import constants


# TODO CLEAR UP THIS FILE

class Particle(pygame.sprite.Sprite):
    def __init__(self, countdown):
        super(Particle, self).__init__()
        # TODO remove dull rect and image inits
        self.rect = pygame.Rect(10, 10, 10, 10)
        self.image = None
        # TODO move to clocks?
        self.countdown = countdown

    # TODO move shared functionality here (countdown of death for example)


# TODO rename and make more general?
class Blood(Particle):
    def __init__(self, position, speed, lifetime, fadeout, color, round_shape=True):
        super(Blood, self).__init__(lifetime)
        self.color = color
        self.speed = speed
        self.fadeout = fadeout
        self.pos = position
        self.round_shape = round_shape  # TODO make permanent solution and allow different shaped oficially

    def update(self, *args):
        # MOVING
        # TODO optimize positioning
        self.pos.x += self.speed.x
        self.pos.y += self.speed.y

        self.rect.centerx = self.pos.x
        self.rect.centery = self.pos.y
        # TIMER HANDLING
        # TODO make countdown class?
        self.countdown -= self.fadeout
        if self.countdown < 0:
            self.kill()
            return
        # IMAGE COMPOSING
        # TODO move drawing
        self.image = pygame.Surface((int(self.countdown * 2), int(self.countdown * 2)), pygame.SRCALPHA, 32)
        if self.round_shape:
            pygame.draw.circle(self.image, self.color, [i // 2 for i in self.image.get_size()], int(self.countdown))
        else:
            self.image.fill(constants.C_BOX)


class Exclamation(Particle):
    def __init__(self, position, lifetime):
        super(Exclamation, self).__init__(lifetime)
        # TODO move font to game obj?
        font = pygame.font.Font(None, 80)

        self.image = font.render("!", 3, constants.C_BLACK)
        self.rect = self.image.get_rect(centerx=position.x, centery=position.y)

    def update(self, *args):
        # TODO this clearly can move to Clock!
        if self.countdown >= 0:
            if self.countdown == 0:
                self.kill()
            else:
                pass
            self.countdown -= 1


class Fade(Particle):
    def __init__(self, duration, to_black):
        super(Fade, self).__init__(duration)
        self.rect = pygame.Rect(0, 0, 1920, 1080)
        self.to_black = to_black
        self.duration = duration

    def update(self):
        # TIMER HANDLING
        if self.countdown >= 0:
            self.countdown -= 1
        # IMAGE COMPOSING
        self.image = pygame.Surface(self.rect[2:4]).convert_alpha()
        if self.to_black:
            self.image.fill((0, 0, 0, 255 * ((self.duration - self.countdown - 1) / self.duration)))  # not used
        else:
            self.image.fill((0, 0, 0, int(255 * ((self.countdown + 1) / self.duration))))
