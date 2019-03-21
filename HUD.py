import pygame


# TODO base class for hud?
class HealthHUD(pygame.sprite.Sprite):

    def __init__(self, obj):
        super(HealthHUD, self).__init__()
        self.obj = obj
        # TODO move adding to group?
        self.obj.game.hud_group.add(self)
        # TODO remove dummy init? somehow???????
        self.image = None
        self.rect = None
        self.makeup()

    def makeup(self):
        # IMAGE COMPOSING
        self.image = pygame.Surface((100 * (self.obj.max_health+self.obj.weak_health), 100), pygame.SRCALPHA, 32)
        # normal hearts
        for i in range(self.obj.max_health):
            if i < self.obj.health:
                self.image.blit(self.obj.game.HEART_SPRITE, (i * 100, 0))
            else:
                self.image.blit(self.obj.game.HEART_EMPTY_SPRITE, (i * 100, 0))
        # weak hearts
        for i in range(self.obj.weak_health):
            self.image.blit(self.obj.game.HEART_WEAK_SPRITE, ((i + self.obj.max_health) * 100, 0))

        self.rect = self.image.get_rect(top=30, left=30)
