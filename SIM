#!/usr/bin/python3

# Author: Natasha Bailey
# CSCI423, Computer Simulation
# Colorado School of Mines, Fall 2023
#
# For this simulation I am using the approach of double arrivals only from east.
# The coordinate system I am using is all relative to the crosswalk button, with east
# and south being positive directions.

import sys
from enum import Enum
import heapq
import itertools
from src.fileRandom import FileRandom
from src.welford import Welford
from src.event import (
    Event,
    PedArrival,
    PedAtButton,
    PedImpatient,
    PedExit,
    AutoArrival,
    AutoExit,
    GreenExpires,
    YellowExpires,
    RedExpires,
)


CONSTANTS = {
    "B": 330,
    "w": 24,
    "S": 46,
    "RED": 18,
    "YELLOW": 8,
    "GREEN": 35,
    "lP": 3 / 60,
    "lA": 4 / 60,
    "L": 9,
    "a": 10,
    "vjLow": 25,
    "vjHigh": 35,
    "vkLow": 2.6,
    "vkHigh": 4.1,
    "X": 20,
}

PED_X_START = CONSTANTS["B"] + CONSTANTS["S"]
CAR_FRONT_X_START = CONSTANTS["B"] * 3.5 + CONSTANTS["S"] * 3


class WalkSignal(Enum):
    WALK = 1
    NO_WALK = 2


class TrafficSignal(Enum):
    GREEN = 1
    YELLOW = 2
    RED = 3


class SafetySignal:
    def __init__(self, t):
        self.setGreen(t)

    def setGreen(self, t):
        self.walkSignal = WalkSignal.NO_WALK
        self.trafficSignal = TrafficSignal.GREEN
        self.greenInit = t
        self.buttonPressed = False

    def setYellow(self, t):
        self.walkSignal = WalkSignal.NO_WALK
        self.trafficSignal = TrafficSignal.YELLOW
        self.buttonPressed = True
        self.yellowInit = t

    def setRed(self, t):
        self.walkSignal = WalkSignal.WALK
        self.trafficSignal = TrafficSignal.RED
        self.buttonPressed = True
        self.redInit = t

    def pressButton(self):
        self.buttonPressed = True


class Pedestrian:
    idIter = itertools.count()

    def __init__(self, speed):
        self.speed = speed
        self.id = next(Pedestrian.idIter)


class Automobile:
    idIter = itertools.count()

    def __init__(self, speed):
        self.speed = speed
        self.position = CAR_FRONT_X_START
        self.id = next(Automobile.idIter)


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
    autoDelay = Welford()
    pedDelay = Welford()

    # the real simulation stuff
    t = 0

    waitingPeds = []
    crossingPeds = []
    activeAutos = []
    safetySignal = SafetySignal(t)

    events = []
    heapq.heappush(events, nextPedArrival(t, pedRandom))
    pedsGenerated = 1
    heapq.heappush(events, nextAutoArrival(t, autoRandom))
    autosGenerated = 1

    while len(events) > 0:
        nextEvent = heapq.heappop(events)
        t = nextEvent.at
        if isinstance(nextEvent, PedArrival):
            print(f"{t}\tPedestrian {nextEvent.ped.id} arrived")

            # spawn next arrival and at button event
            if pedsGenerated < N:
                heapq.heappush(events, nextPedArrival(t, pedRandom))
                pedsGenerated += 1
            heapq.heappush(events, eventPedReachesButton(t, nextEvent.ped))
        elif isinstance(nextEvent, PedAtButton):
            handlePedReachesButton(
                nextEvent,
                t,
                safetySignal,
                waitingPeds,
                buttonRandom,
                events,
                crossingPeds,
            )
        elif isinstance(nextEvent, PedExit):
            print(f"{t}\tPedestrian {nextEvent.ped.id} exited")
        elif isinstance(nextEvent, AutoArrival):
            print(f"{t}\tAutomobile {nextEvent.auto.id} arrived")
            activeAutos.append(nextEvent.auto)

            if autosGenerated < N:
                heapq.heappush(events, nextAutoArrival(t, autoRandom))
                autosGenerated += 1
        elif isinstance(nextEvent, GreenExpires):
            print(f"{t}\tGreen expired")
            heapq.heappush(events, YellowExpires(t + CONSTANTS["YELLOW"]))
            safetySignal.setYellow(t)
        elif isinstance(nextEvent, YellowExpires):
            print(f"{t}\tYellow expired")
            heapq.heappush(events, RedExpires(t + CONSTANTS["RED"]))
            safetySignal.setRed(t)

            # Decide who gets to cross
            i = 0
            while len(crossingPeds) < CONSTANTS["X"] and len(waitingPeds) > i:
                ped = waitingPeds[i]
                if canPedMakeIt(ped, i):
                    waitingPeds.pop(i)
                    crossingPeds.append(ped)
                    heapq.heappush(events, PedExit(t + CONSTANTS["S"] / ped.speed, ped))
                else:
                    i += 1
        elif isinstance(nextEvent, RedExpires):
            print(f"{t}\tRed expired")
            safetySignal.setGreen(t)
            crossingPeds.clear()
            if buttonRandom.uniform() < 1 - ((1 - (15 / 16)) ** len(waitingPeds)):
                # We push a green expires event to happen whenever the green
                # timer expires
                heapq.heappush(
                    events,
                    GreenExpires(t + CONSTANTS["GREEN"]),
                )
                safetySignal.pressButton()
                print(f"{t}\tWaiting pedestrians pushed the button")

    for random in randomGenerators:
        random.close()


def nextPedArrival(t, pedRandom):
    ped = Pedestrian(pedRandom.uniform(CONSTANTS["vkLow"], CONSTANTS["vkHigh"]))
    return PedArrival(t + pedRandom.exponential(1 / (2 * CONSTANTS["lP"])), ped)


def eventPedReachesButton(t, ped):
    return PedAtButton(t + PED_X_START / ped.speed, ped)


def handlePedReachesButton(
    nextEvent, t, safetySignal, waitingPeds, buttonRandom, events, crossingPeds
):
    print(f"{t}\tPedestrian {nextEvent.ped.id} reached button", end="")
    if safetySignal.walkSignal != WalkSignal.WALK:
        n = len(waitingPeds)
        p = 1 / (n + 1)
        if n == 0:
            p = 15 / 16

        if buttonRandom.uniform() <= p:
            if not safetySignal.buttonPressed:
                # If this is the first time the button has been pressed in this
                # cycle, then we push a green expires event to happen either now
                # if the green timer is already expired or to be at whenever the
                # green timer does expire.
                heapq.heappush(
                    events,
                    GreenExpires(
                        t + max(CONSTANTS["GREEN"] - (t - safetySignal.greenInit), 0)
                    ),
                )
            safetySignal.pressButton()
            print(" and pushed button")
        else:
            print("")
        waitingPeds.append(nextEvent.ped)
    else:
        if len(crossingPeds) < CONSTANTS["X"]:
            if canPedMakeIt(nextEvent.ped, t - safetySignal.redInit):
                crossingPeds.append(nextEvent.ped)
                heapq.heappush(
                    events,
                    PedExit(t + CONSTANTS["S"] / nextEvent.ped.speed, nextEvent.ped),
                )
                print(" and crossed")
            else:
                waitingPeds.append(nextEvent.ped)
                print(" and could not make it in time")
        else:
            waitingPeds.append(nextEvent.ped)
            print(" and couldn't cross since there were too many people crossing")


def canPedMakeIt(ped, redTimeSoFar):
    return CONSTANTS["S"] / ped.speed <= CONSTANTS["RED"] - redTimeSoFar


def nextAutoArrival(t, autoRandom):
    auto = Automobile(autoRandom.uniform(CONSTANTS["vjLow"], CONSTANTS["vjHigh"]))
    return AutoArrival(t + autoRandom.exponential(1 / (2 * CONSTANTS["lA"])), auto)


if __name__ == "__main__":
    main()
