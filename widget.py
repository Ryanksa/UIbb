import pygame as pg
from PyQt5.QtWidgets import QApplication, QDialog, QListWidget, QVBoxLayout
from pathlib import Path
from threading import Thread
import os, sys
import random as r

from header import *
from utils import get_icon

class SearchBar:
    def __init__(self, x, y, text):
        # color, font, text, and various variables for this searchbar
        self.color = pg.Color(*CHALK_COLOR)
        self.font = pg.font.Font(*CHALK_FONT)
        self.default_text = text
        self.text = text
        self.active = False
        self.results = []
        # a text surface and a rectangle hitbox makes up a search bar
        self.text_surface = self.font.render(text, True, self.color)
        self.rect = pg.Rect(x, y, self.text_surface.get_width() + 10, CHALK_FONT[1] + 5)
    
    def handle_event(self, event):
        interacted = False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            # click on search bar to activate it
            if self.rect.collidepoint(event.pos):
                interacted = True
                self.active = not self.active
            else:
                self.active = False
            # Change the current color and text of search bar
            self.text = '' if self.active else self.default_text
            self.text_surface = self.font.render(self.text, True, self.color)
        # keyboard input when active
        elif self.active and event.type == pg.KEYDOWN:
            interacted = True
            # {ENTER} searches
            if event.key == pg.K_RETURN:
                Thread(target=self._search, args=(self.text,), daemon=True).start()
            # {BACKSPACE} removes 1 char
            elif event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            # {ESC} clears the search bar
            elif event.key == pg.K_ESCAPE:
                self.text = ''
                self.active = False
            # typing char
            else:
                self.text += event.unicode
            # render new text
            self.text_surface = self.font.render(self.text, True, self.color)
        return interacted

    def _search(self, file):
        # internal method for searching: uses SearchGUI to display search results
        q = QApplication(sys.argv)
        window = SearchGUI(self.results)
        Thread(target=window.searchItems, args=(file,), daemon=True).start()
        window.show()
        q.exec_()

    def get_search_results(self):
        # extract search results out
        if len(self.results) == 0:
            return self.results
        else:
            temp = self.results
            self.results = []
            return temp
    
    def update(self):
        # update the rectangle hitbox wrt the current text size
        self.rect.w = self.text_surface.get_width() + 10

    def draw(self, screen):
        # draw the text (surface), rectangle hitbox is not drawn
        screen.blit(self.text_surface, (self.rect.x+5, self.rect.y+5))


class SearchGUI(QDialog):
    def __init__(self, results):
        # QDialog widget
        super(SearchGUI, self).__init__()
        self.setStyleSheet("background-color: rgb(30, 30, 30);")
        self.results = results
        # contains a list widget to display the search results
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("color: rgb(211, 211, 211);")
        self.list_widget.itemDoubleClicked.connect(self.addAndReturn)
        # list widget sits on top of layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)

    def searchItems(self, file):
        for path in Path('/').rglob(file):
            self.list_widget.addItem(str(path))

    def addAndReturn(self, item):
        # quits GUI after picking
        self.results.append(item.text())
        QApplication.quit()


class App:
    def __init__(self, path, x, y, name):
        # randomly choose to be Left (0) or Right (1)
        self.lr = r.randint(0, 1)
        # path to app (file) and name of the app
        self.path = Path(path)
        self.name = self.path.name if name is None else name
        # class variables for position and movement
        self.x, self.y = x, y
        self.old_x, self.old_y = x, y
        self.offset_x, self.offset_y = 0, 0
        # class variables for state of this app
        self.keep = True
        self.dragging = False
        self.options_opened = False
        self.renaming = False
        # class variables for various font, color, and special effects
        self.font = pg.font.Font(*APP_FONT)
        self.text_color = pg.Color(*APP_TEXT_COLOR)
        self.img = pg.image.load(APP_IMG_L) if self.lr == 0 else pg.image.load(APP_IMG_R)
        self.img_offset = LR_OFFSET[self.lr]
        self.icon = get_icon(path, "large")
        # instances that make up an App instance
        self.options_menu = OptionsMenu(self)
        self.rect = pg.Rect(x, y, 32, 32)
        self.text_surface = self.font.render(self.name, True, self.text_color)

    def handle_event(self, event):
        interacted = False
        if self.options_opened:
            # options menu open, events go there
            interacted = self.options_menu.handle_event(event)
        elif self.renaming:
            # currently renaming this app
            interacted = True
            if event.type == pg.MOUSEBUTTONDOWN:
                self.renaming = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.text_color = pg.Color(*APP_TEXT_COLOR)
                    self.renaming = False
                elif event.key == pg.K_BACKSPACE:
                    self.name = self.name[:-1]
                elif event.key == pg.K_ESCAPE:
                    self.name = ''
                else:
                    self.name += event.unicode
            self.text_surface = self.font.render(self.name, True, self.text_color)
        # neither the options menu is open, nor currently renaming
        elif event.type == pg.MOUSEBUTTONDOWN:
            # start dragging
            if event.button == 1 and self.rect.collidepoint(event.pos):
                interacted = True
                self.dragging = True
                self.old_x, self.old_y = self.x, self.y
                mouse_x, mouse_y = event.pos
                self.offset_x = self.x - mouse_x
                self.offset_y = self.y - mouse_y
            # right click to open options
            if event.button == 3 and self.rect.collidepoint(event.pos):
                interacted = True
                self.options_menu.setpos(*event.pos)
                self.options_opened = True
        # continue dragging
        elif event.type == pg.MOUSEMOTION:
            if self.dragging:
                interacted = True
                mouse_x, mouse_y = event.pos
                self.x = mouse_x + self.offset_x
                self.y = mouse_y + self.offset_y
        # drop
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                interacted = True
                self.dragging = False
                # launch app if clicked (and not dragged)
                if self.x == self.old_x and self.y == self.old_y:
                    os.startfile(self.path)
        return interacted

    def update(self):
        # update position of rect
        self.rect.x, self.rect.y = self.x, self.y

    def draw1(self, screen):
        """
        draw1 draws the first layer of the app
        First layer of one instance can be beneath/above the first layer of another instance
        """
        # draw the name centered just below the icon
        text_w = self.text_surface.get_width()
        x_offset = (text_w - 32)//2 if text_w > 32 else 0
        screen.blit(self.text_surface, (self.x - x_offset, self.y + 27))
        # draw the app icon
        screen.blit(self.icon, (self.x, self.y))
        # draw the options menu if its open
        if self.options_opened:
            self.options_menu.draw(screen)
        
    def draw2(self, screen):
        """
        draw2 draws the second layer of the app
        Second layer is always on top of the first layer, but can be beneath/above the second layer of another
        """
        # draw the pin image
        screen.blit(self.img, (self.x + self.img_offset[0], self.y + self.img_offset[1]))


class OptionsMenu():
    def __init__(self, app):
        # reference to the parent app
        self.app = app
        # 2 options so far: unpin and rename
        self.unpin_opt = pg.font.Font(*OPTMENU_TEXT_FONT).render("unpin", True, OPTMENU_TEXT_COLOR)
        self.rename_opt = pg.font.Font(*OPTMENU_TEXT_FONT).render("rename", True, OPTMENU_TEXT_COLOR)
        # rectangles for the 2 options
        w = max(self.unpin_opt.get_width(), self.rename_opt.get_width()) + 10
        h = OPTMENU_TEXT_FONT[1]
        self.unpin_rect = pg.Rect(app.x, app.y, w, h)
        self.rename_rect = pg.Rect(app.x, app.y + h, w, h)
    
    def setpos(self, x, y):
        h = OPTMENU_TEXT_FONT[1]
        self.unpin_rect.x, self.unpin_rect.y = x, y
        self.rename_rect.x, self.rename_rect.y = x, y + h

    def handle_event(self, event):
        interacted = False
        if event.type == pg.MOUSEBUTTONDOWN:
            interacted = True
            # left click on unpin option
            if event.button == 1 and self.unpin_rect.collidepoint(event.pos):
                self.app.keep = False
            # left click on rename option
            elif event.button == 1 and self.rename_rect.collidepoint(event.pos):
                self.app.text_color = pg.Color(*APP_HIGHLIGHTED_TEXT_COLOR)
                self.app.renaming = True
            # left clicking anywhere else cancels the option menu
            self.app.options_opened = False
        # typing cancels the option menu
        elif event.type == pg.KEYDOWN:
            interacted = True
            self.app.options_opened = False
        return interacted       

    def draw(self, screen):
        # draw the background of the options menu
        pg.Surface.fill(screen, OPTMENU_COLOR, self.unpin_rect)
        pg.Surface.fill(screen, OPTMENU_COLOR, self.rename_rect)
        # draw in the indivdual options
        screen.blit(self.unpin_opt, (self.unpin_rect.x + 2, self.unpin_rect.y + 2))
        screen.blit(self.rename_opt, (self.rename_rect.x + 2, self.rename_rect.y + 2))


class Chalk():
    def __init__(self, text, x, y):
        self.text = text
        # class variables for font and color
        self.font = pg.font.Font(*CHALK_FONT)
        self.color = pg.Color(*CHALK_COLOR)
        # class variables for state of this Chalk
        self.keep = True
        self.active = True
        # class variables for position
        self.x, self.y = x, y
        # instances that make up a Chalk instance
        self.text_surface = self.font.render(text, True, self.color)
        self.rect = pg.Rect(self.x, self.y, self.text_surface.get_width() + 10, CHALK_FONT[1])

    def handle_event(self, event):
        interacted = False
        if event.type == pg.MOUSEBUTTONDOWN:
            # left click on chalk activates it
            if event.button == 1 and self.rect.collidepoint(event.pos):
                interacted = True
                self.active = not self.active
            # left click off chalk unactivates it
            elif event.button == 1 and not self.rect.collidepoint(event.pos):
                self.active = False
            # right click on chalk removes it
            elif event.button == 3 and self.rect.collidepoint(event.pos):
                self.keep = False
                interacted = True
        elif self.active and event.type == pg.KEYDOWN:
            interacted = True
            # {ENTER} to finish writing
            if event.key == pg.K_RETURN:
                self.active = False
            # {BACKSPACE} removes 1 char
            elif event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            # {ESC} erases the chalk
            elif event.key == pg.K_ESCAPE:
                self.text = ''
                self.active = False
                self.keep = False
            # typing char
            else:
                self.text += event.unicode
            self.text_surface = self.font.render(self.text, True, self.color)
        return interacted

    def update(self):
        self.rect.width = self.text_surface.get_width() + 10

    def draw(self, screen):
        screen.blit(self.text_surface, (self.x, self.y))


class BlackBoard():
    def __init__(self, args_list):
        self.searchbar = SearchBar(20, 15, "Search Here...")
        self.items = []
        for args in args_list:
            if len(args) == 3:
                self.items.append(Chalk(*args))
            elif len(args) == 4:
                self.items.append(App(*args))
        
    def handle_event(self, event):
        interacted = False
        # handle event for search bar
        interacted = self.searchbar.handle_event(event)
        # handle event for all the items on the blackboard
        remove_idx = []
        for i in range(len(self.items)):
            curr_interacted = self.items[i].handle_event(event)
            if not self.items[i].keep:
                remove_idx.append(i)
            if curr_interacted:
                interacted = True 
        for i in sorted(remove_idx, reverse=True):
            del self.items[i]
        # if nothing interacted with event, and the event is a left click, add new chalk
        if not interacted and event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            self.add(('', x, y - CHALK_FONT[1]//2))
        # instantiate any new pinned apps
        new_apps = self.searchbar.get_search_results()
        for path in new_apps:
            randx = r.randint(10, WIDTH//1.5)
            randy = r.randint(10, HEIGHT//1.5)
            self.add((path, randx, randy, None))

    def add(self, args):
        if len(args) == 3:
            self.items.append(Chalk(*args))
        elif len(args) == 4:
            self.items.append(App(*args))

    def draw(self, screen):
        # draw search bar
        self.searchbar.update()
        self.searchbar.draw(screen)
        # draw all the chalks first
        apps = []
        for item in self.items:
            item.update()
            if isinstance(item, Chalk):
                item.draw(screen)
            else:
                apps.append(item)
        # then draw the apps
        for app in apps:
            app.draw1(screen)
        for app in apps:
            app.draw2(screen)
