import pygame
import random
import constants
import clock
import base


# TODO all common properties of Player and Anemy is bunched up here, needs disassembling to interfaces
class Alive(base.AdvancedSprite):
    def __init__(self, game, pos, face=None):  # TODO think about values sent to this __init__
        super(Alive, self).__init__()
        self.game = game
        # TODO remove dull inits??? (we have to init fields in init}
        self.rect = None
        if face is not None:
            self.face = face
        else:
            self.face = constants.V_LEFT.rotate(random.randint(-180, 180))

        self.pos = pygame.Vector2(pos)
        self.speed = constants.V_ZERO
        # TODO make up better way to state if the object is moving. This field is used in SOME cases
        self.moving = False
        self.can_be_moved = True  # object's ability to make decision about its movement!!!

        # BASE CLOCKS
        # TODO move to interfaces as well
        self.dash_clock = clock.Clock(self.unblock_movement)
        self.next_dash_clock = clock.Clock(None)
        self.stun_clock = clock.Clock(self.unblock_movement)
        self.throw_back_clock = clock.Clock(self.stop)
        self.clock_ticker = clock.ClockTicker()

    def move_and_collide_with_walls(self):
        # collision logic mostly copypasted from some example, so it works fine
        # move horizontally
        self.pos.x += self.speed.x
        self.rect.centerx = self.pos.x
        intersected = pygame.sprite.spritecollide(self, self.game.obstacle_group, False)
        for wall in intersected:
            if self.speed.x < 0:
                self.rect.left = wall.rect.right
                self.pos.x = self.rect.centerx
            else:
                self.rect.right = wall.rect.left
                self.pos.x = self.rect.centerx

        # move vertically
        self.pos.y += self.speed.y
        self.rect.centery = self.pos.y
        intersected = pygame.sprite.spritecollide(self, self.game.obstacle_group, False)
        for wall in intersected:
            if self.speed.y < 0:
                self.rect.top = wall.rect.bottom
                self.pos.y = self.rect.centery
            else:
                self.rect.bottom = wall.rect.top
                self.pos.y = self.rect.centery

    def pickup(self):
        pick = pygame.sprite.spritecollide(self, self.game.pickupable_group, False)
        for p in pick:
            p.pickup(self)

    def update(self):
        # woo hoo, shared update!
        # TODO add function for additional actions?
        self.clock_ticker.tick_all()
        self.move()
        self.pickup()

    # TODO merge throw back and stun because of conflict of can_be_moved????
    def throw_back(self, direction, speed, duration, stun_duration):
        self.throw_back_clock.wind_up(duration)
        self.speed = direction * speed
        self.stun(stun_duration)

    def stun(self, duration):
        self.stun_clock.wind_up(duration)
        self.can_be_moved = False

    def dash(self):
        pass

    def back_dash(self):
        pass

    def move(self):
        pass

    def unblock_movement(self):
        self.can_be_moved = True

    def stop(self):
        self.speed = constants.V_ZERO
