import pygame

from src.framework.const import Button, Axis


class Controller:
    def __init__(self):
        self.dash_pressed = False
        self.back_dash_pressed = False
        self.swing_pressed = False
        self.interact_pressed = False

    def check(self, obj):
        obj.look_away = self.check_look() * 300
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
        pass

    def check_dash(self):
        pass

    def check_back_dash(self):
        pass

    def check_movement(self):
        pass

    def check_swing(self):
        pass

    def check_look(self):
        pass

    # TODO move game reseting (and then calling menu) to controller?


class Joystick(Controller):

    def __init__(self):
        super().__init__()
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
        if abs(x) < 0.1:
            return 0
        return x


class Keyboard(Controller):
    def __init__(self):
        super().__init__()

    def check_movement(self):
        pressed = pygame.key.get_pressed()
        return pygame.Vector2(pressed[pygame.K_RIGHT] - pressed[pygame.K_LEFT],
                              pressed[pygame.K_DOWN] - pressed[pygame.K_UP])

    def check_look(self):
        return pygame.Vector2(0, 0)

    def check_dash(self):
        return pygame.key.get_pressed()[pygame.K_d]

    def check_swing(self):
        return pygame.key.get_pressed()[pygame.K_s]

    def check_back_dash(self):
        return pygame.key.get_pressed()[pygame.K_a]
