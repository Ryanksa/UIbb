import pygame as pg

from header import *
from widget import *

def load_bb(file):
    ret = []
    with open(file, "r") as f:
        for line in f:
            args = line.split(',,')
            ret.append(args)
    return ret

def save_bb(file, items):
    with open(file, "w") as f:
        for item in items:
            if isinstance(item, ChalkText) and item.text != '':
                # this is a valid ChalkText instance, write its arguments to save file
                args = ("ChalkText,," + item.text + ",," + str(item.x) + ",," +
                        str(item.y) + "\n")
                f.write(args)
            elif isinstance(item, ChalkLine):
                # this is a valid ChalkLine instance, write its arguments to save file
                args = ("ChalkLine,," + str(item.start_pos[0]) + ",," + 
                        str(item.start_pos[1]) + ",," + str(item.end_pos[0]) +
                        ",," + str(item.end_pos[1]) + "\n")
                f.write(args)
            elif isinstance(item, App):
                # this is a valid App instance, write its arguments to save file
                args = ("App,," + str(item.path) + ",," + str(item.x) + ",," +
                        str(item.y) + ",," + item.name + "\n")
                f.write(args)


if __name__ == '__main__':
    # app window
    pg.init()
    screen = pg.display.set_mode((WIDTH+25, HEIGHT+25), pg.RESIZABLE)
    screen_border = pg.Rect(0, 0, WIDTH+25, HEIGHT+25)
    screen.fill(BACKGROUND_COLOR)
    pg.draw.rect(screen, BORDER_COLOR, screen_border, 25)
    pg.display.set_caption("UIbb")
    
    # instantiate objects
    clock = pg.time.Clock()
    bb = BlackBoard(load_bb(SAVEFILE))

    # program loop
    running = True
    while running:
        for event in pg.event.get():
            # [X] to close UIbb
            if event.type == pg.QUIT:
                running = False
            # resizing window
            elif event.type == pg.VIDEORESIZE:
                screen = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)
                screen_border = pg.Rect(0, 0, event.w, event.h)
            # {CTRL}+{S} to save
            elif (event.type == pg.KEYDOWN and event.key == pg.K_s and
                  pg.key.get_mods() & pg.KMOD_CTRL):
                save_bb(SAVEFILE, bb.items)
            else:
                bb.handle_event(event)
                
        # refresh screen
        screen.fill(BACKGROUND_COLOR)
        pg.draw.rect(screen, BORDER_COLOR, screen_border, 25)
        # re-draw blackboard
        bb.draw(screen)
        # update display
        pg.display.update()
        clock.tick(FPS)

    # program exit, save blackboard
    save_bb(SAVEFILE, bb.items)
    pg.quit()
