"""
Module for spikes
"""
# TODO move to enemy or obstacle?
from enum import Enum
from typing import Tuple

import pygame

from path_of_pain.src.framework import base, clock, const


class SpikesState(Enum):
    """
    Different states of spikes
    """
    SLEEP = 1
    READY = 2
    ATTACK = 3


class SpikesFactory:
    """
    Factory that creates new spikes and adds them to corresponding group
    """

    def __init__(self, game, *groups: pygame.sprite.AbstractGroup):
        self.groups = groups
        self.game = game
        self.flyweight = SpikesFlyweight()

    def create(self, coords: Tuple[int, int], start_phase: int = SpikesState.SLEEP.value):
        product = Spikes(self.flyweight, self.game, coords, start_phase)
        for group in self.groups:
            group.add(product)
        return product


class SpikesFlyweight:
    """
    Class with Spikes assets and constant
    """

    def __init__(self):
        self.SLEEP_SPRITE = pygame.image.load(const.IMG_PATH + 'spikes_sleep.png').convert_alpha()
        self.READY_SPRITE = pygame.image.load(const.IMG_PATH + 'spikes_ready.png').convert_alpha()
        self.ATTACK_SPRITE = pygame.image.load(const.IMG_PATH + 'spikes_attack.png').convert_alpha()

        self.ATTACK_SOUND = pygame.mixer.Sound(const.SND_PATH + 'white_spikes_appear_03.wav')
        self.READY_SOUND = pygame.mixer.Sound(const.SND_PATH + 'white_spikes_disappear_01.wav')
        self.state_durations = {SpikesState.SLEEP: 30, SpikesState.READY: 10, SpikesState.ATTACK: 20}


class Spikes(base.AdvancedSprite):
    """
    Spikes are static objects that periodically activate and hit you from the floor
    """

    def __init__(self, flyweight: SpikesFlyweight, game, coords: Tuple[int, int], start_phase: int):
        """
        Spikes init

        :param flyweight: flyweight for assets and constants
        :param game: game in which spikes are
        :param coords: tuple with coordinates
        :param start_phase: starting spikes phase, hidden phase is default
        """
        base.AdvancedSprite.__init__(self)
        self.rect = pygame.Rect(*coords, 50, 50)
        self.state = SpikesState(start_phase)
        self.game = game
        self.pos = pygame.Vector2(coords)
        self.flyweight = flyweight
        self.state_clock = clock.Clock(self.next_state)
        self.state_clock.wind_up(self.flyweight.state_durations[self.state])
        self.postponed_fetch_layer(coords[1] - 50)

    def update(self):
        self.state_clock.tick()
        if self.state == SpikesState.ATTACK and self.game.player.rect.colliderect(self.rect):
            self.game.player.hit(1, self)

    def draw(self, screen, window):
        image = None
        if self.state == SpikesState.SLEEP:
            image = self.flyweight.SLEEP_SPRITE
        elif self.state == SpikesState.READY:
            image = self.flyweight.READY_SPRITE
        elif self.state == SpikesState.ATTACK:
            image = self.flyweight.ATTACK_SPRITE
        return screen.blit(image, (self.rect.x - window.x, self.rect.y - window.y))

    def next_state(self):
        """
        Switches spikes state in circles

        :return: None
        """
        if self.state == SpikesState.SLEEP:
            self.state = SpikesState.READY
            self.play_sound(self.flyweight.READY_SOUND)
        elif self.state == SpikesState.READY:
            self.state = SpikesState.ATTACK
            self.play_sound(self.flyweight.ATTACK_SOUND)
        elif self.state == SpikesState.ATTACK:
            self.state = SpikesState.SLEEP
        self.state_clock.wind_up(self.flyweight.state_durations[self.state])

    # TODO remove this temp solution
    def play_sound(self, sound: pygame.mixer.Sound):
        """
        Plays the sound with volume proportional to distance to player

        If that sound is already played, it is stopped and played again with better volume
        This is done to remove sounds ugly overlaying

        :param sound: sound to play
        :return: None
        """
        # The volume is calculated as a upside-down parabola
        # pygame converts negative volume to 1
        volume = max(0, -0.000001 * (self.game.player.pos - self.pos).length_squared() + 1)
        if sound.get_num_channels() == 0 or sound.get_volume() < volume:
            sound.stop()
            sound.set_volume(volume)
            sound.play()
