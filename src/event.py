class Event:
    def __init__(self, at):
        self.at = at

    def __lt__(self, other):
        return self.at < other.at


class PedArrival(Event):
    def __init__(self, at, ped):
        self.ped = ped
        super().__init__(at)


class PedAtButton(Event):
    def __init__(self, at, ped):
        self.ped = ped
        super().__init__(at)


class PedImpatient(Event):
    def __init__(self, at, ped):
        self.ped = ped
        super().__init__(at)


class PedExit(Event):
    def __init__(self, at, ped):
        self.ped = ped
        super().__init__(at)


class AutoArrival(Event):
    def __init__(self, at, auto):
        self.auto = auto
        super().__init__(at)


class AutoExit(Event):
    pass


class GreenExpires(Event):
    pass


class YellowExpires(Event):
    pass


class RedExpires(Event):
    pass
