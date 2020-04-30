from pathlib import Path
from widget import App


def load_state(file):
    pinned = []
    with open(file, "r") as f:
        for line in f:
            args = line.split(',')
            new = App(args[0], int(args[1]), int(args[2]), int(args[3]), int(args[4]))
            pinned.append(new)
    return pinned

def save_state(file, pinned):
    with open(file, "w") as f:
        for app in pinned:
            args = str(app.path) + "," + str(app.x) + "," + str(app.y) + "," + str(app.w) + "," + str(app.h) +"\n"
            f.write(args)
