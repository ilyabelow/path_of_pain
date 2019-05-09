"""Module for level generation"""
import random
from typing import Tuple

import pygame

from path_of_pain.src.framework import const
from path_of_pain.src.states import game


# TODO do you see this? this class just BEGS for separation of Game and factories
class LevelBuilder:
    def __init__(self):
        self.game = game.Game()

    def set_level_size(self, width: int, height: int):
        """
        Configures rectangle of the level

        :param width: level width
        :param height: level height
        :return: None
        """
        self.game.level_rect = pygame.Rect(0, 0, width, height)

    def set_pain(self, painful: bool):
        """
        Adjust pain

        :param painful: amount of PAIN in the game
        :return: None
        """
        self.game.painful = painful

    def set_level_number(self, number: int):
        """
        Lets game know what level it is in

        :param number: level number
        :return: None
        """
        self.game.room_num = number

    def set_music(self, music_name: str):
        """
        Set music for the level

        :param music_name: name of music file
        :return: None
        """
        pygame.mixer.music.load(const.SND_PATH + music_name)
        # TODO this works really bad because different music has different volume
        pygame.mixer.music.set_volume(const.MUSIC_NORMAL_VOLUME)
        pygame.mixer.music.play(loops=-1)

    def set_title(self, text: str):
        """
        Sets level title

        :param text: text of the title
        :return: None
        """
        self.game.title = text

    def build_boxes(self, *box_coords: Tuple[int, int]):
        """
        Construct boxes from list of their coordinates

        :param box_coords: list of tuples with box coordinates
        :return: None
        """
        for coords in box_coords:
            self.game.box_factory.create(coords)

    def build_enemies(self, *enemies_coords: Tuple[int, int]):
        """
        Construct enemies from list of their coordinates

        :param enemies_coords: list of tuples with box coordinates
        :return: None
        """
        for coords in enemies_coords:
            self.game.enemy_factory.create_enemy(coords)

    def build_spikes(self, *spikes_coords: Tuple[int, int]):
        """
        Construct spikes from list of their coordinates

        :param spikes_coords: list of tuples with box coordinates
        :return: None
        """
        for coords in spikes_coords:
            self.game.spikes_factory.create(coords)

    def build_walls(self, *walls_params: Tuple[int, int, int, int, int]):
        """
        Construct walls from the list of their coordinates, size and height

        :param walls_params: tuples (x, y, x_size, y_size, height)
        :return: None
        """
        for wall in walls_params:
            self.game.wall_factory.create(wall[:4], wall[4])

    def build_player(self, player_coords: Tuple[int, int]):
        """
        Construct player in designated coordinates. Moves health from player on previous level

        :param player_coords: initial player coordinates
        :return: None
        """
        # TODO movement of player's health
        self.game.player = self.game.player_factory.create(player_coords)

    def build_door(self, coords: Tuple[int, int], next_level: int, locks: int):
        """
        Construct door for the next level

        :param coords: coordinates of the door
        :param next_level: number of next level
        :param locks: amount of locks on the door
        :return: None
        """
        self.game.door_factory.create(coords, next_level, locks)

    def distribute_keys(self, keys: int):
        """
        Give random enemies according number of keys

        :param keys: amount of keys to be distributed
        :return: None
        """
        if len(self.game.enemy_group) < keys:
            # foolproofing
            raise BaseException('um there is not enough enemies to distribute so much keys')
        while keys > 0:
            enemy = random.choice(self.game.enemy_group.sprites())
            if not enemy.has_key:
                keys -= 1
                enemy.has_key = True

    def get_result(self) -> game.Game:
        """
        Return constructed level

        :return: Game object to be given to Application object
        """
        return self.game


class LevelChooser:
    def __init__(self, builder: LevelBuilder):
        self.builder = builder

    def choose_level(self, number: int, painful: bool) -> game.Game:
        if number == 1:
            keys_on_level = 5
            self.builder.set_pain(painful)
            self.builder.set_level_size(3000, 2000)
            self.builder.set_title('{}STAGE ONE'.format(painful * 'PAINFUL '))
            self.builder.set_level_number(number)
            if painful:
                self.builder.set_music('Furious_Gods.wav')
            else:
                self.builder.set_music('Gods_and_Glory.wav')
            self.builder.build_boxes((200, 200), (250, 200), (250, 250), (200, 350),
                                     (1300, 700), (1350, 750), (1450, 750), (2400, 200),
                                     (2400, 400), (2450, 400), (2650, 350), (2400, 500),
                                     (2400, 700), (2500, 400), (2600, 300), (2600, 600),
                                     (2700, 400), (2500, 550), (2550, 500), (200, 650),
                                     (200, 700), (250, 700), (200, 750), (250, 750),
                                     (300, 750), (650, 150), (650, 200), (1100, 1700),
                                     (1150, 1700), (1200, 1700), (300, 1450), (250, 1500),
                                     (2400, 1450), (2450, 1450), (2500, 1450), (2550, 1450),
                                     (2600, 1450), (2400, 1700), (2450, 1700), (2500, 1700),
                                     (2550, 1700), (2600, 1700), (2350, 1500), (2350, 1450),
                                     (2350, 1550), (2350, 1600), (2350, 1650), (2350, 1700),
                                     (2600, 1500), (2600, 1550), (2600, 1600), (2600, 1650),
                                     (1800, 1750), (2050, 1700))
            self.builder.build_enemies((500, 1300), (900, 1300), (500, 1300), (900, 1300),
                                       (500, 1600), (900, 1600), (700, 1450), (1700, 450),
                                       (2200, 450), (2850, 150), (2850, 750), (2100, 1200),
                                       (2100, 1500), (1800, 1500), (2450, 1600), (2500, 1600),
                                       (2450, 1550), (2500, 1550))
            # between ul and dl rooms
            self.builder.build_spikes((600, 950), (650, 900), (700, 950), (750, 900), (800, 950), (850, 900),
                                      (600, 1050), (650, 1000), (700, 1050), (750, 1000), (800, 1050), (850, 1000), )
            # in ur room
            self.builder.build_spikes((2500, 350), (2500, 600), (2600, 400), (2700, 450),
                                      (2500, 500), (2700, 300), (2600, 550), (2400, 450))
            self.builder.distribute_keys(keys_on_level)
            self.builder.build_door((1450, 125), 2, keys_on_level)
            # vertical center walls
            self.builder.build_walls((1400, 900, 200, 500, 50), (1400, 1600, 200, 300, 50))
            # horizontal center walls
            self.builder.build_walls((100, 900, 500, 200, 50), (900, 900, 500, 200, 50),
                                     (1600, 900, 500, 200, 50), (2400, 900, 500, 200, 50))
            # pillars
            self.builder.build_walls((900, 400, 200, 200, 90), (1400, 400, 200, 200, 120),
                                     (1900, 400, 200, 200, 150), (1800, 1300, 200, 200, 30))
            # border walls
            self.builder.build_walls((100, 0, 1300, 100, 50), (1600, 0, 1300, 100, 50),
                                     (1400, 0, 200, 100, 200), (0, 0, 100, 2000, 50),
                                     (0, 1900, 3000, 150, 50), (2900, 0, 100, 2000, 50))
            self.builder.build_player((400, 300))

            return self.builder.get_result()
        if number == 2:
            self.builder.set_level_number(number)
            self.builder.set_pain(painful)
            self.builder.set_level_size(*const.RESOLUTION)
            self.builder.set_title('BLOOD{} MASTER'.format(painful * '&PAIN '))
            # TODO remove temp solution
            const.MUSIC_MUTED_VOLUME = 0.5
            const.MUSIC_NORMAL_VOLUME = 1
            if painful:
                self.builder.set_music('S87-168 Nightmare Grimm.wav')
            else:
                self.builder.set_music('S82-115 Grimm.wav')

            self.builder.game.enemy_factory.create_boss((const.RESOLUTION[0] / 2, const.RESOLUTION[1] / 2 - 200))

            self.builder.build_walls((100, 0, const.RESOLUTION[0] - 200, 100, 50),
                                     (100, const.RESOLUTION[1], const.RESOLUTION[0] - 200, 100, 50),
                                     (0, 0, 100, const.RESOLUTION[1] + 100, 50),
                                     (const.RESOLUTION[0] - 100, 0, 100, const.RESOLUTION[1] + 100, 50))
            self.builder.build_walls((300, 300, 100, 75, 75),
                                     (300, const.RESOLUTION[1] - 375, 100, 75, 75),
                                     (const.RESOLUTION[0] - 400, 300, 100, 75, 75),
                                     (const.RESOLUTION[0] - 400, const.RESOLUTION[1] - 375, 100, 75, 75))
            self.builder.build_spikes((400, 250), (400, 400), (250, 250), (250, 400),

                                      (400, const.RESOLUTION[1] - 375 - 50), (400, const.RESOLUTION[1] - 375 + 100),
                                      (250, const.RESOLUTION[1] - 375 - 50), (250, const.RESOLUTION[1] - 375 + 100),

                                      (const.RESOLUTION[0] - 400 + 100, 250), (const.RESOLUTION[0] - 400 + 100, 400),
                                      (const.RESOLUTION[0] - 400 - 50, 250), (const.RESOLUTION[0] - 400 - 50, 400),

                                      (const.RESOLUTION[0] - 400 + 100, const.RESOLUTION[1] - 375 - 50),
                                      (const.RESOLUTION[0] - 400 + 100, const.RESOLUTION[1] - 375 + 100),
                                      (const.RESOLUTION[0] - 400 - 50, const.RESOLUTION[1] - 375 - 50),
                                      (const.RESOLUTION[0] - 400 - 50, const.RESOLUTION[1] - 375 + 100),

                                      (const.RESOLUTION[0] / 2 - 250, const.RESOLUTION[1] / 2),
                                      (const.RESOLUTION[0] / 2 - 250, const.RESOLUTION[1] / 2 + 200),
                                      (const.RESOLUTION[0] / 2 - 250, const.RESOLUTION[1] / 2 - 200),
                                      (const.RESOLUTION[0] / 2 + 200, const.RESOLUTION[1] / 2),
                                      (const.RESOLUTION[0] / 2 + 200, const.RESOLUTION[1] / 2 + 200),
                                      (const.RESOLUTION[0] / 2 + 200, const.RESOLUTION[1] / 2 - 200),

                                      )
            self.builder.build_player((const.RESOLUTION[0] / 2, const.RESOLUTION[1] - 300))
            return self.builder.get_result()
