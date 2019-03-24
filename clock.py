# love this class
class Clock:
    def __init__(self, when_end, start_time=0):
        self.time = -1
        if when_end is None:
            self.when_end = lambda: True  # plug
        else:
            self.when_end = when_end
        self.start_time = start_time

    # TODO add support for when_end() with args
    def tick(self):
        if self.time >= 0:
            if self.time == 0:
                self.when_end()
            self.time -= 1

    def wind_up(self, start_time=None):
        if start_time is None:
            self.time = self.start_time
        else:
            self.time = start_time

    def is_not_running(self):
        return self.time == -1

    def is_running(self):
        return self.time >= 0

    def stop(self):
        self.time = -1

    def how_much_is_left(self):
        return self.time


class ClockTicker:
    def __init__(self, o):
        self.clocks = [getattr(o, attr) for attr in dir(o) if '_clock' in attr]

    def tick_all(self):
        for clock in self.clocks:
            clock.tick()

    def add_clock(self, *clock):
        self.clocks += [*clock]
