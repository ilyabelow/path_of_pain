"""
Module with Clock which helps countdown time
"""


class Clock:
    """
    Countdown time and perform an action after time is over
    """

    def __init__(self, when_end=None, start_time=0):
        """
        Pass start_time here if it is const

        :param when_end: Action that will be performed after the time is over
        :param start_time: Default time the clock will be wind up for
        """
        self.time = -1
        if when_end is None:
            def when_end(): return True
        self.when_end = when_end
        self.start_time = start_time

    # TODO add support for when_end() with args
    def tick(self):
        """
        Subtract one from time. Performs action when the time is over

        :return: None
        """
        if self.time >= 0:
            if self.time == 0:
                self.when_end()
            self.time -= 1

    def wind_up(self, start_time=None):
        """
        Start the clock
        If default value for start_time is stated in __init__, it will be used if nothing passed in this function

        :param start_time: Amount of ticks that the clock will run for
        :return: None
        """
        if start_time is None:
            self.time = self.start_time
        else:
            self.time = start_time

    def is_running(self):
        """
        Convenient shortcut

        :return: If clock is running
        """
        return self.time >= 0

    def is_not_running(self):
        """
        Convenient shortcut, use this instead of not Clock.is_running() for more readable code

        :return: If clock is not running
        """
        return self.time == -1

    def stop(self):
        """
        Reset time on the clock

        :return: None
        """
        self.time = -1

    def soft_stop(self):
        """
        Reset time on the clock AND perform its action (model normal end of time)

        :return: None
        """
        self.time = -1
        self.when_end()

    def how_much_is_left(self):
        return self.time


class ClockTicker:
    """
    Helper class for convenient clock storage
    """

    def __init__(self, o):
        """
        Adds to container all the clocks from object

        :param o: Object from which suck clocks
        """
        self.clocks = [getattr(o, attr) for attr in dir(o) if isinstance(getattr(o, attr), Clock)]

    def tick_all(self):
        """
        Click all the clocks in the container with one tick

        :return: None
        """
        for clock in self.clocks:
            clock.tick()

    def add_clock(self, *clock):
        """
        Add new clocks in the container

        :param clock: List of clocks to add
        :return: None
        """
        self.clocks += [*clock]
