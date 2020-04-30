import pygame as pg

from header import *
from widget import *
from utils import load_state, save_state

if __name__ == '__main__':
    # app window
    pg.init()
    screen = pg.display.set_mode((WIDTH+25, HEIGHT+25))
    screen_border = pg.Rect(0, 0, WIDTH+25, HEIGHT+25)
    screen.fill(BACKGROUND_COLOR)
    pg.draw.rect(screen, BORDER_COLOR, screen_border, 25)
    pg.display.set_caption("UIbb")
    
    # instantiate objects
    clock = pg.time.Clock()
    searchbar = SearchBar(20, 15, "Search Here...")
    pin_se = pg.mixer.Sound(APP_SOUND_EFFECT)

    pinned = load_state(SAVEFILE)
    running = True
    while running:
        for event in pg.event.get():
            # [X] to close UIbb
            if event.type == pg.QUIT:
                running = False

            # pinned apps events
            remove_idx = []
            for i in range(len(pinned)):
                keep = pinned[i].handle_event(event)
                if not keep:
                    remove_idx.append(i)
            for i in sorted(remove_idx, reverse=True):
                del pinned[i]
            # search bar events
            searchbar.handle_event(event)
        
        # instantiate any newly pinned apps
        new = searchbar.get_search_results()
        for path in new:
            pin_se.play()
            new_pin = App(path, 50, 50, APP_WIDTH, APP_HEIGHT)
            pinned.append(new_pin)
        
        # refresh screen
        screen.fill(BACKGROUND_COLOR)
        pg.draw.rect(screen, BORDER_COLOR, screen_border, 25)
        # update and re-draw pinned apps
        for app in pinned:
            app.update()
            app.draw(screen)
        for app in pinned:
            app.draw_img(screen)
        # update and re-draw search bar
        searchbar.update()
        searchbar.draw(screen)
        # update display
        pg.display.update()
        clock.tick(FPS)

    save_state(SAVEFILE, pinned)
    pg.quit()
