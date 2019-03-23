import pygame
import base
import interface

LITTLE_HEART_SPRITE = None
LITTLE_HEART_WEAK_SPRITE = None


class Heart(base.AdvancedSprite, interface.Pickupable):
    def __init__(self, coords, weak=False):
        super(Heart, self).__init__()
        self.weak = weak
        self.rect = pygame.Rect(coords.x, coords.y, 30, 30)
        if not weak:
            self.image = LITTLE_HEART_SPRITE
        else:
            self.image = LITTLE_HEART_WEAK_SPRITE

    def pickup(self, who):
        who.heal(1, self.weak)

        self.kill()

    def draw(self, screen, window):
        screen.blit(self.image, (self.rect.x - window.x, self.rect.y - window.y))
