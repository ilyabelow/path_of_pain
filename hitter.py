import constants
import pygame
import random
import clock


# TODO projectiles!
# TODO base class with better name then "hitter"
class Sword(pygame.sprite.Sprite):
    def __init__(self, owner):
        super(Sword, self).__init__()
        self.game = owner.game
        self.owner = owner
        self.image = self.game.SWORD_SPRITE
        self.rect = self.image.get_rect()
        self.game.hitter_group.add(self)  # redundant?
        self.pos = None

        # SWING STATS
        self.swing_count = 0
        self.right_hand = True

        # CLOCKS
        self.current_swing_clock = clock.Clock(None)
        self.next_combo_clock = clock.Clock(self.swinging_stopped)
        self.next_swing_clock = clock.Clock(None)
        self.clock_ticker = clock.ClockTicker(self.current_swing_clock, self.next_swing_clock, self.next_combo_clock)

    def swing(self):
        # continue combo
        if 0 < self.swing_count <= 2 and self.next_swing_clock.is_not_running() \
                or self.swing_count == 0 and self.next_combo_clock.is_not_running():  # start new combo
            # TODO nerf this because triple attack is too OP
            self.next_swing_clock.wind_up(constants.sword_swing_wait[self.swing_count])
            self.next_combo_clock.wind_up(constants.sword_combo_wait[self.swing_count])
            self.current_swing_clock.wind_up(constants.sword_swing_duration[self.swing_count])
            self.swing_count += 1
            self.right_hand = not self.right_hand  # switch hand, just for aesthetics

            # HITTING
            self.pos = self.owner.pos + self.owner.face * 70
            # TODO good hitbox for sword
            self.rect = pygame.Rect(0, 0, 50, 50)
            # TODO this pos will be overwritten in update, may be remove from here?
            self.rect.centerx = self.pos.x
            self.rect.centery = self.pos.y
            got_hit = pygame.sprite.spritecollide(self, self.game.hittable_group, False)
            for entity in got_hit:
                entity.hit(1, self)

            # SOUND EFFECTS
            random.choice(self.game.SWORD_SOUNDS).play()
            wall = pygame.sprite.spritecollideany(self, self.game.wall_group)
            if wall is not None:
                self.game.SWORD_WALL_SOUND.play()

    def update(self):
        self.clock_ticker.tick_all()
        # COOL IMAGE COMPOSING AND POSITION UPDATING
        # TODO separate and move to different functions
        if self.current_swing_clock.is_not_running():
            self.pos = self.owner.pos + self.owner.face.rotate(90) * (80 * self.right_hand - 40)
            self.image = pygame.transform.rotate(self.game.SWORD_SPRITE,
                                                 self.owner.face.angle_to(constants.V_UP))
        else:
            self.pos = self.owner.pos + self.owner.face * 70
            if self.right_hand:
                self.image = pygame.transform.rotate(pygame.transform.flip(self.game.SWORD_SWANG_SPRITE, True, False),
                                                     self.owner.face.angle_to(constants.V_UP) - 45)
            else:
                self.image = pygame.transform.rotate(self.game.SWORD_SWANG_SPRITE,
                                                     self.owner.face.angle_to(constants.V_UP) + 45)
        self.rect = self.image.get_rect(centerx=self.pos.x, centery=self.pos.y)

    def swinging_stopped(self):
        self.swing_count = 0
