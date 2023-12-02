class Welford:
    def __init__(self):
        self.currentXBar = 0
        self.currentV = 0
        self.i = 0

    def update(self, x):
        self.i += 1
        self.lastXBar = self.currentXBar
        self.lastV = self.currentV

        self.currentXBar = self.lastXBar + (1 / self.i) * (x - self.lastXBar)
        self.currentV = self.lastV + ((self.i - 1) / self.i) * (
            (x - self.lastXBar) ** 2
        )

    def mean(self):
        return self.currentXBar

    def variance(self):
        return self.currentV / self.i
