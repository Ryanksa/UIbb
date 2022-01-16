import pygame as pg
from PyQt5.QtWidgets import QApplication, QDialog, QListWidget, QVBoxLayout
from pathlib import Path
from threading import Thread
import sys, os

from header import *

class SearchBar:
    def __init__(self, x, y, text):
        # color, font, text, and various variables for this searchbar
        self.color = pg.Color(*COLOR_PAL[WHITE])
        self.font = pg.font.Font(CHALK_FONT, CHALK_FONTSIZE)
        self.default_text = text
        self.text = text
        self.active = False
        self.results = []
        # a text surface and a rectangle hitbox makes up a search bar
        self.text_surface = self.font.render(text, True, self.color)
        self.rect = pg.Rect(x, y, self.text_surface.get_width() + 10, CHALK_FONTSIZE + 5)
    
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
        self.rect = pg.Rect(x, y, self.text_surface.get_width() + 10, CHALK_FONTSIZE + 5)
    
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
        self.list_widget.setFixedHeight(600)
        self.list_widget.setMinimumWidth(400)
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
        self.p = parent
        self.options = []
        self.opt_rects = []
        self.rect_colors = []
    
    def setpos(self, x, y):
        h = OPTMENU_FONTSIZE + 10
        for i in range(len(self.options)):
            self.opt_rects[i].x, self.opt_rects[i].y = x, y + i*h

    def handle_event(self, event):
        # pressing any key closes the option menu
        if event.type == pg.KEYDOWN:
            self.p.options_opened = False
        # hovering over an option changes its color
        elif event.type == pg.MOUSEMOTION:
            for i in range(len(self.opt_rects)):
                if self.opt_rects[i].collidepoint(event.pos):
                    self.rect_colors[i] = OPTMENU_COLOR_HOVERED
                else:
                    self.rect_colors[i] = OPTMENU_COLOR

    def draw(self, screen):
        # draw the background of the options menu
        for i in range(len(self.opt_rects)):
            pg.Surface.fill(screen, self.rect_colors[i], self.opt_rects[i])
        # draw in the indivdual options
        for i in range(len(self.options)):
            screen.blit(self.options[i], (self.opt_rects[i].x + 2, self.opt_rects[i].y + 2))


class AppOptionsMenu(OptionsMenu):
    def __init__(self, app):
        super().__init__(app)
        # 4 options: launch, remove, rename, color
        self.options.append(
            pg.font.Font(OPTMENU_FONT, OPTMENU_FONTSIZE).render("Launch", True, OPTMENU_TEXT_COLOR))
        self.options.append(
            pg.font.Font(OPTMENU_FONT, OPTMENU_FONTSIZE).render("Remove", True, OPTMENU_TEXT_COLOR))
        self.options.append(
            pg.font.Font(OPTMENU_FONT, OPTMENU_FONTSIZE).render("Rename", True, OPTMENU_TEXT_COLOR))
        self.options.append(
            pg.font.Font(OPTMENU_FONT, OPTMENU_FONTSIZE).render("Color >>", True, pg.Color(*COLOR_PAL[self.p.color_idx])))
        # rectangles for the options
        w = self.options[3].get_width() + 10
        h = OPTMENU_FONTSIZE + 10
        for i in range(len(self.options)):
            self.opt_rects.append(pg.Rect(0, 0, w, h))
        # color of option rectangles (changes when hovered)
        self.rect_colors = [OPTMENU_COLOR] * len(self.opt_rects)

    def setpos(self, x, y):
        super().setpos(x, y)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            # click on launch option
            if self.opt_rects[0].collidepoint(event.pos):
                os.startfile(self.p.path)
                self.p.options_opened = False
            # click on remove option
            if self.opt_rects[1].collidepoint(event.pos):
                self.p.keep = False
                self.p.options_opened = False
            # click on rename option
            elif self.opt_rects[2].collidepoint(event.pos):
                self.p.text_color = pg.Color(*EDITING_COLOR)
                self.p.renaming = True
                self.p.text_surface = self.p.font.render(self.p.name, True, self.p.text_color)
                self.p.options_opened = False
            # click on color >>
            elif self.opt_rects[3].collidepoint(event.pos):
                self.p.color_idx = (self.p.color_idx + 1) % NUM_COLORS
                self.p.text_color = pg.Color(*COLOR_PAL[self.p.color_idx])
                self.options[3] = pg.font.Font(OPTMENU_FONT, OPTMENU_FONTSIZE).render("Color >>", True, self.p.text_color)
                self.p.text_surface = self.p.font.render(self.p.name, True, self.p.text_color)
            # clicking anywhere else closes this options menu
            else:
                self.p.options_opened = False
        super().handle_event(event)

    def draw(self, screen):
        super().draw(screen)


class ChalkTextOptionsMenu(OptionsMenu):
    def __init__(self, chalkText):
        super().__init__(chalkText)
        # 4 options: erase, edit, color, size
        self.options.append(
            pg.font.Font(OPTMENU_FONT, OPTMENU_FONTSIZE).render("Erase", True, OPTMENU_TEXT_COLOR))
        self.options.append(
            pg.font.Font(OPTMENU_FONT, OPTMENU_FONTSIZE).render("Edit", True, OPTMENU_TEXT_COLOR))
        self.options.append(
            pg.font.Font(OPTMENU_FONT, OPTMENU_FONTSIZE).render("Color >>", True, pg.Color(*COLOR_PAL[self.p.color_idx])))
        self.options.append(
            pg.font.Font(OPTMENU_FONT, OPTMENU_FONTSIZE).render("- Size +", True, OPTMENU_TEXT_COLOR))
        # rectangles for the options
        w = self.options[2].get_width() + 10
        h = OPTMENU_FONTSIZE + 10
        for i in range(len(self.options)):
            self.opt_rects.append(pg.Rect(0, 0, w, h))
        # special setup for size option
        self.opt_rects[-1].width = w//2
        self.opt_rects.append(pg.Rect(0, 0, w//2, h))
        self.w = w
        # color of option rectangles (changes when hovered)
        self.rect_colors = [OPTMENU_COLOR] * len(self.opt_rects)
    
    def setpos(self, x, y):
        super().setpos(x, y)
        # special setup for size option
        x, y = self.opt_rects[-2].x + self.w//2, self.opt_rects[-2].y
        self.opt_rects[-1].x, self.opt_rects[-1].y = x, y

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            # click on erase option
            if self.opt_rects[0].collidepoint(event.pos):
                self.p.keep = False
                self.p.options_opened = False
            # click on edit option
            elif self.opt_rects[1].collidepoint(event.pos):
                self.p.active = True
                self.p.color = pg.Color(*EDITING_COLOR)
                self.p.text_surface = self.p.font.render(self.p.text, True, self.p.color)
                self.p.options_opened = False
            # click on color >>
            elif self.opt_rects[2].collidepoint(event.pos):
                self.p.color_idx = (self.p.color_idx + 1) % NUM_COLORS
                self.p.color = pg.Color(*COLOR_PAL[self.p.color_idx])
                self.options[2] = pg.font.Font(OPTMENU_FONT, OPTMENU_FONTSIZE).render("Color >>", True, self.p.color)
                self.p.text_surface = self.p.font.render(self.p.text, True, self.p.color)                
            # click on size -
            elif self.opt_rects[3].collidepoint(event.pos):
                if self.p.fontsize > 2:
                    self.p.fontsize -= 2
                    self.p.font = pg.font.Font(CHALK_FONT, self.p.fontsize)
                    self.p.text_surface = self.p.font.render(self.p.text, True, self.p.color)
            # click on size +
            elif self.opt_rects[4].collidepoint(event.pos):
                self.p.fontsize += 2
                self.p.font = pg.font.Font(CHALK_FONT, self.p.fontsize)
                self.p.text_surface = self.p.font.render(self.p.text, True, self.p.color)
            # clicking anywhere else closes this options menu
            else:
                self.p.options_opened = False
        super().handle_event(event)

    def draw(self, screen):
        super().draw(screen)


class ChalkLineOptionsMenu(OptionsMenu):
    def __init__(self, chalkLine):
        super().__init__(chalkLine)
        # 4 options: erase, adjust, color, size
        self.options.append(
            pg.font.Font(OPTMENU_FONT, OPTMENU_FONTSIZE).render("Erase", True, OPTMENU_TEXT_COLOR))
        self.options.append(
            pg.font.Font(OPTMENU_FONT, OPTMENU_FONTSIZE).render("Adjust", True, OPTMENU_TEXT_COLOR))
        self.options.append(
            pg.font.Font(OPTMENU_FONT, OPTMENU_FONTSIZE).render("Color >>", True, pg.Color(*COLOR_PAL[self.p.color_idx])))
        self.options.append(
            pg.font.Font(OPTMENU_FONT, OPTMENU_FONTSIZE).render("- Size +", True, OPTMENU_TEXT_COLOR))
        # rectangles for the options
        w = self.options[2].get_width() + 10
        h = OPTMENU_FONTSIZE + 10
        for i in range(len(self.options)):
            self.opt_rects.append(pg.Rect(0, 0, w, h))
        # special setup for size option
        self.opt_rects[-1].width = w//2
        self.opt_rects.append(pg.Rect(0, 0, w//2, h))
        self.w = w
        # color of option rectangles (changes when hovered)
        self.rect_colors = [OPTMENU_COLOR] * len(self.opt_rects)

    def setpos(self, x, y):
        super().setpos(x, y)
        # special setup for size option
        x, y = self.opt_rects[-2].x + self.w//2, self.opt_rects[-2].y
        self.opt_rects[-1].x, self.opt_rects[-1].y = x, y

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            # click on erase option
            if self.opt_rects[0].collidepoint(event.pos):
                self.p.keep = False
                self.p.options_opened = False
            # click on adjust option
            elif self.opt_rects[1].collidepoint(event.pos):
                self.p.drawn = False
                self.p.color = pg.Color(*EDITING_COLOR)
                self.p.options_opened = False
            # click on color >>
            elif self.opt_rects[2].collidepoint(event.pos):
                self.p.color_idx = (self.p.color_idx + 1) % NUM_COLORS
                self.p.color = pg.Color(*COLOR_PAL[self.p.color_idx])
                self.options[2] = pg.font.Font(OPTMENU_FONT, OPTMENU_FONTSIZE).render("Color >>", True, self.p.color)
            # click on size -
            elif self.opt_rects[3].collidepoint(event.pos):
                if self.p.width > 1:
                    self.p.width -= 1
            # click on size +
            elif self.opt_rects[4].collidepoint(event.pos):
                self.p.width += 1
            # clicking anywhere else closes this options menu
            else:
                self.p.options_opened = False
        super().handle_event(event)

    def draw(self, screen):
        super().draw(screen)
