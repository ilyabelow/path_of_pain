import pygame
import base
import interface

LITTLE_HEART_SPRITE = None
LITTLE_HEART_WEAK_SPRITE = None


class Heart(base.AdvancedSprite, interface.Pickupable):
    def __init__(self, coords, weak=False):
        base.AdvancedSprite.__init__(self)
        interface.Pickupable.__init__(self)
        self.weak = weak
        self.rect = pygame.Rect(coords.x, coords.y, 30, 30)
        if not weak:
            self.image = LITTLE_HEART_SPRITE
        else:
            self.image = LITTLE_HEART_WEAK_SPRITE
        self.y = coords.y - 50  # TODO improve because it is really flat and should me under everything

    def pickup(self, who):
        who.heal(1, self.weak)
        self.kill()

    def draw(self, screen, window):
        return screen.blit(self.image, (self.rect.x - window.x, self.rect.y - window.y))
