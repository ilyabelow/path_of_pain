import clock
import random
import particle
import constants


class Healthy:
    def __init__(self,
                 max_health,
                 heal_sounds=None,
                 hit_sounds=None,
                 death_sounds=None,
                 invulnerability=-1,
                 weak_health=0):
        self.max_health = max_health
        self.health = max_health
        self.weak_health = weak_health
        self.invulnerability_clock = clock.Clock(None, invulnerability)

        self.heal_sounds = heal_sounds
        self.hit_sounds = hit_sounds
        self.death_sounds = death_sounds

    def heal(self, amount, weak):
        if not weak:
            self.health = min(self.max_health, self.health + amount)
        else:
            self.weak_health += amount
        if self.death_sounds is not None:
            random.choice(self.heal_sounds).play()
        self.after_healing()

    def after_healing(self):
        pass

    def hit(self, amount, who):
        if self.invulnerability_clock.is_not_running():
            self.invulnerability_clock.wind_up()

            if self.weak_health != 0:
                self.weak_health -= amount
            else:
                self.health -= amount
            if self.hit_sounds is not None:
                random.choice(self.hit_sounds).play()
            self.on_any_health(who)

            if self.health + self.weak_health == 1:  # TODO generalize low health
                self.on_low_health(who)
            if self.health == 0:
                if self.death_sounds is not None:
                    random.choice(self.death_sounds).play()
                self.on_zero_health(who)
            else:
                self.on_ok_health(who)

    def on_any_health(self, direction):
        pass

    def on_ok_health(self, direction):
        pass

    def on_low_health(self, direction):
        pass

    def on_zero_health(self, direction):
        pass


# TODO research how to store common interface because creating so many ints for every box and enemy is madness
class Bleedable:
    def __init__(self, game,
                 all_direction_amount,
                 all_direction_speed,
                 all_direction_sizes,
                 all_direction_fade,

                 one_direction_amount,
                 one_direction_speed,
                 one_direction_sizes,
                 one_direction_fade,
                 one_direction_offset,
                 one_direction_splash,

                 color):
        self.game = game

        self.all_direction_speed = all_direction_speed
        self.all_direction_amount = all_direction_amount
        self.all_direction_sizes = all_direction_sizes
        self.all_direction_fade = all_direction_fade

        self.one_direction_amount = one_direction_amount
        self.one_direction_speed = one_direction_speed
        self.one_direction_sizes = one_direction_sizes
        self.one_direction_fade = one_direction_fade
        self.one_direction_offset = one_direction_offset
        self.one_direction_splash = one_direction_splash

        self.color = color

    def bleed_one_dir(self, pos, main_direction):
        for i in range(self.one_direction_amount):
            direction = main_direction.rotate(random.randint(-self.one_direction_splash, self.one_direction_splash))
            self.game.particle_group.add(particle.Blood(pos + direction * self.one_direction_offset,
                                                        direction * self.one_direction_speed,
                                                        random.randint(self.one_direction_sizes[0],
                                                                       self.one_direction_sizes[1]),
                                                        self.one_direction_fade,
                                                        self.color))

    def bleed_all_dir(self, pos):
        for i in range(self.all_direction_amount):
            direction = constants.V_LEFT.rotate(random.randint(-180, 180))
            self.game.particle_group.add(particle.Blood(pos + constants.V_ZERO,
                                                        direction * self.all_direction_speed,
                                                        random.randint(self.all_direction_sizes[0],
                                                                       self.all_direction_sizes[1]), 1,
                                                        self.color))
