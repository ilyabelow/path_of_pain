import constants
import pygame
import random
import clock
import base

SPRITE = None
SWANG_SPRITE = None

SWING_SOUNDS = None
CLING_SOUND = None


# TODO projectiles!
# TODO base class with better name then "hitter"
class Sword(base.AdvancedSprite):
    def __init__(self, owner):
        super(Sword, self).__init__()
        self.game = owner.game
        self.owner = owner
        self.game.hitter_group.add(self)  # redundant?
        self.pos = None
        self.rect = None

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
            self.rect.centerx = self.pos.x
            self.rect.centery = self.pos.y
            got_hit = pygame.sprite.spritecollide(self, self.game.hittable_group, False)
            for entity in got_hit:
                entity.hit(1, self)

            # SOUND EFFECTS
            random.choice(SWING_SOUNDS).play()
            wall = pygame.sprite.spritecollideany(self, self.game.wall_group)
            if wall is not None:
                CLING_SOUND.play()

    def update(self):
        self.clock_ticker.tick_all()
        if self.current_swing_clock.is_not_running():
            self.pos = self.owner.pos + self.owner.face.rotate(90) * (80 * self.right_hand - 40)
        else:
            self.pos = self.owner.pos + self.owner.face * 70
        self.fetch_layer(self.owner.pos.y)  # TODO make better layer calculation

    def swinging_stopped(self):
        self.swing_count = 0

    def draw(self, screen, window):
        if self.current_swing_clock.is_not_running():
            image = pygame.transform.rotate(SPRITE, self.owner.face.angle_to(constants.V_UP))
        else:
            if self.right_hand:
                image = pygame.transform.rotate(pygame.transform.flip(SWANG_SPRITE, True, False),
                                                self.owner.face.angle_to(constants.V_UP) - 45)
            else:
                image = pygame.transform.rotate(SWANG_SPRITE, self.owner.face.angle_to(constants.V_UP) + 45)
        rect = image.get_rect(centerx=self.pos.x, centery=self.pos.y)
        return screen.blit(image, (rect.x - window.x, rect.y - window.y))
