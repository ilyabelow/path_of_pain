import pygame
import random
import constants
import enemy
import pickupable
import interface
import base

BOX_SPRITE = None
BOX_BREAK_SOUNDS = None
BLEED_ONE_DIR_STATS = {'amount': 5, 'splash': 45, 'fade': 2, 'sizes': [10, 15], 'speed': 6, 'offset': 10}
BLEED_ALL_DIR_STATS = {'amount': 15, 'fade': 2, 'sizes': [15, 20], 'speed': 6, 'offset': 0}


# TODO ADD HEIGHT! ITS IS NOW IMPLICITLY IN CODE!!!!!!!!!!!!!!!

class Wall(base.AdvancedSprite):
    def __init__(self, rect):
        base.AdvancedSprite.__init__(self)
        self.image = pygame.Surface((rect.w, rect.h + 50))
        self.image.fill((137, 107, 77))
        self.rect = rect
        pygame.draw.rect(self.image, (117, 90, 63), (0, rect.h, rect.w, 50))
        self.y = rect.y

    def draw(self, screen, window):
        return screen.blit(self.image, (self.rect.x - window.x, self.rect.y - window.y - 25))  # height = 25


# TODO make this class more general to allow different boxes: jars, skulls, etc
class Box(base.AdvancedSprite, interface.Healthy, interface.Bleeding):
    def __init__(self, game, pos):
        base.AdvancedSprite.__init__(self)
        interface.Healthy.__init__(self, random.randint(1, 3), None, BOX_BREAK_SOUNDS, None)
        interface.Bleeding.__init__(
            self,
            game.particle_group,
            BLEED_ONE_DIR_STATS,
            BLEED_ALL_DIR_STATS,
            constants.C_BOX
        )  # TODO square blood
        self.rect = pygame.Rect(*pos, 50, 35)
        self.game = game
        self.offsets = [[0, 0]] + [[random.randint(-5, 5), random.randint(-5, 5)] for i in range(self.max_health - 1)]
        # TODO better randomizer
        # TODO store not mode but objects itself
        if random.randint(0, 5) == 0 and not game.painful:
            if random.randint(0, 2) == 0:
                self.mode = constants.BOX_WEAK_HEALTH
            else:
                self.mode = constants.BOX_HEALTH
        elif random.randint(0, 15) == 0:
            self.mode = constants.BOX_ENEMY
            self.game.enemies_count += 1
        else:
            self.mode = constants.BOX_EMPTY
        self.y = self.rect.y

    def on_ok_health(self, who):
        pos = pygame.Vector2((self.rect.centerx, self.rect.centery - (self.health - 1) * 15))
        self.bleed_one_dir(pos, (pos - who.pos).normalize())

    def on_zero_health(self, who):
        pos = pygame.Vector2((self.rect.centerx, self.rect.centery))
        self.bleed_all_dir(pos)

        # BOX ACTION
        if self.mode == constants.BOX_HEALTH or self.mode == constants.BOX_WEAK_HEALTH:
            heal = pickupable.Heart(self.rect.move(10, 10), self.mode == constants.BOX_WEAK_HEALTH)
            self.game.pickupable_group.add(heal)
        if self.mode == constants.BOX_ENEMY:
            # TODO temp solution, should sort out groups
            # TODO factory here
            self.game.enemies_count -= 1  # otherwise it will be incremented twice in box constructor and enemy one
            en = enemy.Enemy(self.game, self.rect[:2])
            self.game.enemy_group.add(en)
            self.game.hittable_group.add(en)
            en.stun(15)

        self.kill()

    def draw(self, screen, window):
        rects = []
        for i in range(self.health):
            rects.append(screen.blit(BOX_SPRITE, (
                self.rect.x - window.x + self.offsets[i][0],
                self.rect.y - window.y - i * 15 + self.offsets[i][1] - 8)))  # height = 8
        return rects[0].unionall(rects[1:])
