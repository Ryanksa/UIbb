import pygame as pg

from header import *
from bb_items import *
from blackboard import BlackBoard

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
                args = ("ChalkText,," + item.text + ",," + str(item.x) + ",," + str(item.y)
                        + ",," + str(item.fontsize) + ",," + str(item.color_idx) + "\n")
                f.write(args)
            elif isinstance(item, ChalkLine):
                # this is a valid ChalkLine instance, write its arguments to save file
                args = ("ChalkLine,," + str(item.start_pos[0]) + ",," + str(item.start_pos[1])
                        + ",," + str(item.end_pos[0]) + ",," + str(item.end_pos[1]) + ",," +
                        str(item.width) + ",," + str(item.color_idx) + "\n")
                f.write(args)
            elif isinstance(item, App):
                # this is a valid App instance, write its arguments to save file
                args = ("App,," + str(item.path) + ",," + str(item.x) + ",," +
                        str(item.y) + ",," + str(item.color_idx) + ",," + item.name + "\n")
                f.write(args)


if __name__ == '__main__':
    # app window
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
    screen_border = pg.Rect(0, 0, WIDTH, HEIGHT)
    screen.fill(BACKGROUND_COLOR)
    pg.draw.rect(screen, BORDER_COLOR, screen_border, BORDER_WIDTH)
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
                bb.searchbar.move(BORDER_WIDTH, event.h-BORDER_WIDTH-CHALK_FONTSIZE)
            # {CTRL}+{S} to save
            elif (event.type == pg.KEYDOWN and event.key == pg.K_s and
                  pg.key.get_mods() & pg.KMOD_CTRL):
                save_bb(SAVEFILE, bb.items)
            else:
                bb.handle_event(event)
                
        # re-draw blackboard
        screen.fill(BACKGROUND_COLOR)
        bb.draw(screen)
        pg.draw.rect(screen, BORDER_COLOR, screen_border, BORDER_WIDTH)
        # update display
        pg.display.update()
        clock.tick(FPS)

    # program exit, save blackboard
    save_bb(SAVEFILE, bb.items)
    pg.quit()
