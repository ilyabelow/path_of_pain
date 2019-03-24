import pygame
import base
import interface
import random
import constants

LITTLE_HEART_SPRITE = None
LITTLE_HEART_WEAK_SPRITE = None

KEY_SPRITE = None


class Heart(base.AdvancedSprite, interface.Pickupable):
    def __init__(self, coords, weak=False):
        base.AdvancedSprite.__init__(self)
        interface.Pickupable.__init__(self)
        self.weak = weak
        self.rect = pygame.Rect(coords.x, coords.y, 30, 30)
        self.image = None
        if not weak:
            self.image = LITTLE_HEART_SPRITE
        else:
            self.image = LITTLE_HEART_WEAK_SPRITE
        self.y = coords.y - 50  # TODO improve because it is really flat and should me under everything

    def draw(self, screen, window):
        return screen.blit(self.image, (self.rect.x - window.x, self.rect.y - window.y))


class Key(base.AdvancedSprite, interface.Pickupable):
    def __init__(self, coords, face=None):
        base.AdvancedSprite.__init__(self)
        interface.Pickupable.__init__(self)
        self.rect = pygame.Rect(0, 0, 25, 25)
        self.rect.centerx, self.rect.centery = coords.x, coords.y
        self.y = coords.y - 100  # TODO improve because it is really flat and should me under everything
        if face is None:
            self.face = constants.V_LEFT.rotate(random.randint(-180, 180))
        else:
            self.face = face
        self.image = pygame.transform.rotate(KEY_SPRITE, self.face.angle_to(constants.V_UP))
        # TODO rethink
        self.im_rect = self.image.get_rect(centerx=self.rect.centerx, centery=self.rect.centery)

    def draw(self, screen, window):
        return screen.blit(self.image, (self.im_rect.x - window.x, self.im_rect.y - window.y))
