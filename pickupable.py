import pygame


# TODO make interface for pickupable
class Pickupable(pygame.sprite.Sprite):
    def __init__(self):
        super(Pickupable, self).__init__()

    def pickup(self, who):
        pass


class Heart(Pickupable):
    def __init__(self, game, coords, weak=False):
        super(Heart, self).__init__()
        self.weak = weak
        self.rect = pygame.Rect(coords.x, coords.y, 30, 30)
        if not weak:
            self.image = game.LITTLE_HEART_SPRITE
        else:
            self.image = game.LITTLE_HEART_WEAK_SPRITE

    def pickup(self, who):
        who.heal(1, self.weak)
        self.kill()
