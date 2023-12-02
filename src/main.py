#!/usr/bin/python3
import sys
from src.fileRandom import FileRandom
from src.welford import Welford


def main():
    ARGC = 4
    if len(sys.argv) - 1 != ARGC:
        print(f"error: program expected {ARGC} arguments, got {len(sys.argv) - 1}")
        sys.exit(1)

    N = None
    try:
        N = int(sys.argv[1])
        if N <= 0:
            raise ValueError()
    except:
        print(f"error: expected an int > 0 for argument 1, instead got {sys.argv[1]}")
        sys.exit(1)

    AUTO_RANDOM, PED_RANDOM, BUTTON_RANDOM = sys.argv[2:]
    randomGenerators = []

    for fileName in [AUTO_RANDOM, PED_RANDOM, BUTTON_RANDOM]:
        try:
            file = open(fileName, "r")
            randomGenerators.append(FileRandom(file))
        except:
            print(f"error opening file {fileName} for reading")
            sys.exit(1)

    autoRandom, pedRandom, buttonRandom = randomGenerators

    for random in randomGenerators:
        random.close()


if __name__ == "__main__":
    main()
