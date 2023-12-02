import math


class FileRandom:
    def __init__(self, file):
        self.file = file

    def uniform(self, a=1, b=0):
        low = min(a, b)
        high = max(a, b)

        r = float(self.file.readline())
        return low + (high - low) * r

    def exponential(self, mu):
        return -mu * math.log(1 - self.uniform())

    def close(self):
        self.file.close()
