# TODO make some base classes here

import pygame


# TODO move shared functionality here
class AdvancedSprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

    def draw(self, screen, offset):
        pass


class AdvancedRenderPlain(pygame.sprite.Group):
    def __init__(self, *sprites):
        pygame.sprite.Group.__init__(self, *sprites)

    def draw_all(self, surface, window):
        for sprite in self.sprites():
            sprite.draw(surface, window)
