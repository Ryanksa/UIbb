import pygame as pg
from PyQt5.QtWidgets import QApplication, QDialog, QListWidget, QVBoxLayout
from pathlib import Path
from threading import Thread
import sys

from header import *

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
            # re-render the text for the search bar
            self.text = '' if self.active else self.default_text
            self.text_surface = self.font.render(self.text, True, self.color)
        # keyboard input when active
        elif self.active and event.type == pg.KEYDOWN:
            interacted = True
            # {ENTER} searches
            if event.key == pg.K_RETURN:
                Thread(target=self._search, args=(self.text,), daemon=True).start()
            # {BACKSPACE} removes 1 char, , or 1 word if {CTRL} is held down
            elif event.key == pg.K_BACKSPACE:
                keystates = pg.key.get_pressed()
                if keystates[pg.K_LCTRL]:
                    i = self.text.rstrip().rfind(" ")
                    self.text = self.text[:i+1] if i >= 0 else ''
                else:
                    self.text = self.text[:-1]
            # {ESC} clears the search bar
            elif event.key == pg.K_ESCAPE:
                if self.text == '':
                    self.active = False
                    self.text = self.default_text
                else:
                    self.text = ''
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
    
    def move(self, x, y):
        self.rect = pg.Rect(x, y, self.text_surface.get_width() + 10, CHALK_FONT[1] + 5)
    
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


class OptionsMenu():
    def __init__(self, parent):
        # reference to the parent item
        self.parent = parent
    
    def setpos(self, x, y):
        pass

    def handle_event(self, event):
        pass

    def draw(self, screen):
        pass


class AppOptionsMenu(OptionsMenu):
    def __init__(self, app):
        OptionsMenu.__init__(self, app)
        # 2 options so far: unpin and rename
        self.unpin_opt = pg.font.Font(*OPTMENU_TEXT_FONT).render("unpin", True, OPTMENU_TEXT_COLOR)
        self.rename_opt = pg.font.Font(*OPTMENU_TEXT_FONT).render("rename", True, OPTMENU_TEXT_COLOR)
        # rectangles for the 2 options
        w = max(self.unpin_opt.get_width(), self.rename_opt.get_width()) + 10
        h = OPTMENU_TEXT_FONT[1] + 10
        self.unpin_rect = pg.Rect(app.x, app.y, w, h)
        self.rename_rect = pg.Rect(app.x, app.y + h, w, h)
        # color of option rectangles (changes when hovered)
        self.unpin_rect_color = OPTMENU_COLOR
        self.rename_rect_color = OPTMENU_COLOR

    def setpos(self, x, y):
        h = OPTMENU_TEXT_FONT[1] + 10
        self.unpin_rect.x, self.unpin_rect.y = x, y
        self.rename_rect.x, self.rename_rect.y = x, y + h

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # left click on unpin option
            if event.button == 1 and self.unpin_rect.collidepoint(event.pos):
                self.parent.keep = False
            # left click on rename option
            elif event.button == 1 and self.rename_rect.collidepoint(event.pos):
                self.parent.text_color = pg.Color(*APP_EDITING_TEXT_COLOR)
                self.parent.renaming = True
            # left clicking anywhere else cancels the option menu
            self.parent.options_opened = False
        # {ESC} cancels the option menu
        elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.parent.options_opened = False
        # hovering over an option changes its color
        elif event.type == pg.MOUSEMOTION:
            if self.unpin_rect.collidepoint(event.pos):
                self.unpin_rect_color = OPTMENU_COLOR_HOVERED
                self.rename_rect_color = OPTMENU_COLOR
            elif self.rename_rect.collidepoint(event.pos):
                self.rename_rect_color = OPTMENU_COLOR_HOVERED
                self.unpin_rect_color = OPTMENU_COLOR
            else:
                self.unpin_rect_color = OPTMENU_COLOR
                self.rename_rect_color = OPTMENU_COLOR
    
    def draw(self, screen):
        # draw the background of the options menu
        pg.Surface.fill(screen, self.unpin_rect_color, self.unpin_rect)
        pg.Surface.fill(screen, self.rename_rect_color, self.rename_rect)
        # draw in the indivdual options
        screen.blit(self.unpin_opt, (self.unpin_rect.x + 2, self.unpin_rect.y + 2))
        screen.blit(self.rename_opt, (self.rename_rect.x + 2, self.rename_rect.y + 2))
