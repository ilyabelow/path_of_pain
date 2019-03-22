import pygame
import random
import constants
import particle
import enemy
import pickupable

# TODO common base class Static for non-moving sprites
class Wall(pygame.sprite.Sprite):
    def __init__(self, rect, has_down=False):
        super(Wall, self).__init__()
        self.image = pygame.Surface(tuple(rect)[2:4])
        self.image.fill((137, 107, 77))
        self.rect = rect
        # pseudo 3D effect
        if has_down:
            pygame.draw.rect(self.image, (117, 90, 63), (0, rect.h - 50, rect.w, 50))


# TODO make this class more general to allow different boxes: jars, skulls, etc
class Box(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        super(Box, self).__init__()
        self.rect = pygame.Rect(*pos, 50, 50)
        self.image = game.BOX_SPRITE
        self.game = game
        # TODO better randomizer
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
        # TODO health>1 for sturdy boxes
        # TODO stacked boxes!

    def hit(self, who):
        # SOUND AND VISUAL EFFECTS
        # TODO find better sound effect for breaking
        random.choice(self.game.BOX_BREAK_SOUND).play()
        for i in range(10):
            direction = constants.V_LEFT.rotate(random.randint(-180, 180))
            self.game.particle_group.add(particle.Blood(pygame.Vector2(self.rect.centerx, self.rect.centery),
                                                        direction * 6,
                                                        random.randint(15, 20),
                                                        2,
                                                        constants.C_BOX, False))

        # BOX ACTION
        if self.mode == constants.BOX_HEALTH or self.mode == constants.BOX_WEAK_HEALTH:
            heal = pickupable.Heart(self.game, self.rect.move(10, 10), self.mode == constants.BOX_WEAK_HEALTH)
            # TODO add group manager
            self.game.pickupable_group.add(heal)
            self.game.common_group.add(heal)
        if self.mode == constants.BOX_ENEMY:
            # TODO temp solution, should sort out groups
            # TODO factory here
            self.game.enemies_count -= 1  # otherwise it will be incremented twice in box constructor and enemy one
            en = enemy.Enemy(self.game, self.rect[:2])
            self.game.enemy_group.add(en)
            self.game.common_group.add(en)
            self.game.hittable_group.add(en)
            en.stun(15)

        self.kill()
