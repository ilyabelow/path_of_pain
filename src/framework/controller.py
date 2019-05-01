"""Module with different implementations of player controlling. Btw needs to be rewritten"""
import pygame

from src.framework.const import Button, Axis


class Controller:
    """
    Base class for input method
    """

    def __init__(self):
        # just button states here
        self.dash_pressed = False
        self.back_dash_pressed = False
        self.swing_pressed = False
        self.interact_pressed = False

    def check(self, obj):
        """
        Check for current conroller state
        Performs player actions (dash/interact/...) if corresponding buttons are pushed.
        Player methods are called right from here, which is bad

        :param obj: Who to controll
        :return: None
        """
        obj.look_away = self.check_look() * 300  # 300 because why not
        face_vector = self.check_movement()
        obj.moving = bool(face_vector)
        if face_vector:
            obj.face = face_vector.normalize()  # normalize 0 => error

        # TODO make simple common interface for a button
        if self.check_swing():
            if not self.swing_pressed:
                obj.sword.swing()
            self.swing_pressed = True
        else:
            self.swing_pressed = False

        if self.check_dash():
            if not self.dash_pressed:
                obj.try_to_dash()
            self.dash_pressed = True
        else:
            self.dash_pressed = False

        if self.check_back_dash():
            if not self.back_dash_pressed:
                obj.try_to_back_dash()
            self.back_dash_pressed = True
        else:
            self.back_dash_pressed = False

        if self.check_interact():
            if not self.interact_pressed:
                obj.try_to_interact()
            self.interact_pressed = True
        else:
            self.interact_pressed = False

    def check_interact(self):
        """
        Check if interaction button is pressed

        :return: If player should perform interaction
        """
        pass

    def check_dash(self):
        """
        Check if dash button is pressed

        :return: If player should perform dash
        """
        pass

    def check_back_dash(self):
        """
        Check if back dash button is pressed

        :return: If player should perform back dash
        """
        pass

    def check_swing(self):
        """
        Check if interaction swing is pressed

        :return: If player should perform swing
        """
        pass

    def check_movement(self):
        """
        Get vector of direction in which player should look to

        :return: Direction vector
        """
        pass

    def check_look(self):
        """
        Get vector of window offset

        :return: Direction vector
        """
        pass

    # TODO move game reseting (and then calling menu) to controller?


class Joystick(Controller):
    """
    Controller realization using joystick
    """
    def __init__(self):
        Controller.__init__(self)
        self.joystick = pygame.joystick.Joystick(0)

    def check_movement(self):
        offset = Joystick.dead_zone(self.joystick.get_axis(Axis.LS_H.value)), \
                 Joystick.dead_zone(self.joystick.get_axis(Axis.LS_V.value))
        return pygame.Vector2(offset)

    def check_look(self):
        offset = Joystick.dead_zone(self.joystick.get_axis(Axis.RS_H.value)), \
                 Joystick.dead_zone(self.joystick.get_axis(Axis.RS_V.value))
        return pygame.Vector2(offset)

    def check_dash(self):
        return self.joystick.get_button(Button.A.value)

    def check_swing(self):
        return self.joystick.get_button(Button.X.value)

    def check_back_dash(self):
        return self.joystick.get_button(Button.B.value)

    def check_interact(self):
        return self.joystick.get_button(Button.Y.value)

    def dead_zone(x):
        """
        Sets dead zone for sticks

        :return: 0 if stick is in deadzone and true value otherwise
        """
        if abs(x) < 0.1:
            return 0
        return x


class Keyboard(Controller):
    """
    Controller realisation using keyboard. Inferior to joystick version
    """
    def __init__(self):
        Controller.__init__(self)

    def check_movement(self):
        pressed = pygame.key.get_pressed()
        return pygame.Vector2(pressed[pygame.K_RIGHT] - pressed[pygame.K_LEFT],
                              pressed[pygame.K_DOWN] - pressed[pygame.K_UP])

    def check_look(self):
        # TODO support
        return pygame.Vector2(0, 0)

    def check_dash(self):
        return pygame.key.get_pressed()[pygame.K_d]

    def check_swing(self):
        return pygame.key.get_pressed()[pygame.K_s]

    def check_back_dash(self):
        return pygame.key.get_pressed()[pygame.K_a]

    def check_interact(self):
        return pygame.key.get_pressed()[pygame.K_f]
