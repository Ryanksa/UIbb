import pygame as pg
from PyQt5.QtWidgets import QApplication, QDialog, QListWidget, QVBoxLayout
from pathlib import Path
from threading import Thread
import os, sys
import random as r

from header import *
from utils import get_icon, pointOnLine

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


class App:
    def __init__(self, path, x, y, name):
        # path to app (file) and name of the app
        self.path = Path(path)
        self.name = self.path.name if name is None else name
        self.old_name = self.name
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
        self.icon = get_icon(path, "large")
        # instances that make up an App instance
        self.options_menu = OptionsMenu(self)
        self.rect = pg.Rect(x, y, 32, 32)
        self.text_surface = self.font.render(self.name, True, self.text_color)

    def handle_event(self, event):
        interacted = False
        if self.options_opened:
            # options menu open, events go there
            interacted = True
            self.options_menu.handle_event(event)
        elif self.renaming:
            # currently renaming this app
            interacted = True
            # clicking away, saves current name and stop renaming
            if event.type == pg.MOUSEBUTTONDOWN:
                self.old_name = self.name
                self.text_color = pg.Color(*APP_TEXT_COLOR)
                self.renaming = False
            # typign something while renaming
            if event.type == pg.KEYDOWN:
                # {ENTER} saves current name and stops renaming
                if event.key == pg.K_RETURN:
                    self.old_name = self.name
                    self.text_color = pg.Color(*APP_TEXT_COLOR)
                    self.renaming = False
                # {BACKSPACE} removes 1 char, or 1 word if {CTRL} is held down
                elif event.key == pg.K_BACKSPACE:
                    keystates = pg.key.get_pressed()
                    if keystates[pg.K_LCTRL]:
                        i = self.name.rstrip().rfind(" ")
                        self.name = self.name[:i+1] if i >= 0 else ''
                    else:
                        self.name = self.name[:-1]
                # {ESC} reverts back to the old name
                elif event.key == pg.K_ESCAPE:
                    self.name = self.old_name
                    self.text_color = pg.Color(*APP_TEXT_COLOR)
                    self.renaming = False
                # else typing a char
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

    def draw(self, screen):
        # draw the name centered just below the icon
        text_w = self.text_surface.get_width()
        x_offset = (text_w - 32)//2 if text_w > 32 else 0
        screen.blit(self.text_surface, (self.x - x_offset, self.y + 30))
        # draw the app icon
        screen.blit(self.icon, (self.x, self.y))
        # draw the options menu if its open
        if self.options_opened:
            self.options_menu.draw(screen)


class OptionsMenu():
    def __init__(self, app):
        # reference to the parent app
        self.app = app
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
                self.app.keep = False
            # left click on rename option
            elif event.button == 1 and self.rename_rect.collidepoint(event.pos):
                self.app.text_color = pg.Color(*APP_EDITING_TEXT_COLOR)
                self.app.renaming = True
            # left clicking anywhere else cancels the option menu
            self.app.options_opened = False
        # {ESC} cancels the option menu
        elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.app.options_opened = False
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


class ChalkText():
    def __init__(self, text, x, y, new):
        self.text = text
        self.old_text = text
        # class variables for font and color
        self.font = pg.font.Font(*CHALK_FONT)
        self.color = pg.Color(*CHALK_EDITING_COLOR) if new else pg.Color(*CHALK_COLOR)
        # class variables for state of this ChalkText
        self.keep = True
        self.active = True if new else False
        self.dragging = False
        # class variables for position and movement
        self.x, self.y = x, y
        self.old_x, self.old_y = x, y
        self.offset_x, self.offset_y = 0, 0
        # instances that make up a ChalkText instance
        self.text_surface = self.font.render(text, True, self.color)
        self.rect = pg.Rect(self.x, self.y, self.text_surface.get_width() + 10, CHALK_FONT[1])

    def handle_event(self, event):
        interacted = False
        # active and typing
        if self.active and event.type == pg.KEYDOWN:
            interacted = True
            # {ENTER} to finish writing
            if event.key == pg.K_RETURN:
                self.old_text = self.text
                self.active = False
                self.color = pg.Color(*CHALK_COLOR)
                self.keep = False if self.text == '' else True
            # {BACKSPACE} removes 1 char, or 1 word if {CTRL} is held down
            elif event.key == pg.K_BACKSPACE:
                keystates = pg.key.get_pressed()
                if keystates[pg.K_LCTRL]:
                    i = self.text.rstrip().rfind(" ")
                    self.text = self.text[:i+1] if i >= 0 else ''
                else:
                    self.text = self.text[:-1]
            # {ESC} reverts the ChalkText, or erases it altogether if its new
            elif event.key == pg.K_ESCAPE:
                self.text = self.old_text
                self.active = False
                self.color = pg.Color(*CHALK_COLOR)
                self.keep = False if self.text == '' else True
            # typing char
            else:
                self.text += event.unicode
            self.text_surface = self.font.render(self.text, True, self.color)
        elif event.type == pg.MOUSEBUTTONDOWN:
            # start dragging
            if event.button == 1 and self.rect.collidepoint(event.pos):
                interacted = True
                self.dragging = True
                self.old_x, self.old_y = self.x, self.y
                mouse_x, mouse_y = event.pos
                self.offset_x = self.x - mouse_x
                self.offset_y = self.y - mouse_y
            # right click to erase this ChalkText
            if event.button == 3 and self.rect.collidepoint(event.pos):
                interacted = True
                self.keep = False
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
                # activate if clicked (and not dragged)
                if self.x == self.old_x and self.y == self.old_y:
                    self.active = True
                    self.color = pg.Color(*CHALK_EDITING_COLOR)
            # left click off ChalkText de-activates it
            elif event.button == 1 and not self.rect.collidepoint(event.pos):
                self.active = False
                self.color = pg.Color(*CHALK_COLOR)
            self.text_surface = self.font.render(self.text, True, self.color)
        return interacted

    def update(self):
        self.rect.x, self.rect.y = self.x, self.y
        self.rect.width = self.text_surface.get_width() + 10

    def draw(self, screen):
        screen.blit(self.text_surface, (self.x, self.y))


class ChalkLine:
    def __init__(self, s_x, s_y, e_x, e_y, drawn):
        # class variable for line position
        self.start_pos = (s_x, s_y)
        self.end_pos = (e_x, e_y)
        # class variable for color and various states
        self.color = pg.Color(*CHALK_COLOR) if drawn else pg.Color(*CHALK_EDITING_COLOR)
        self.drawn = drawn
        self.keep = True
        # class variables used for drag and drop
        self.dragging = False
        self.start_offset = (0, 0)
        self.end_offset = (0, 0)

    def handle_event(self, event):
        interacted = False
        # if this ChalkLine is still not drawn yet
        if not self.drawn:
            # moving mouse to determine final position
            if event.type == pg.MOUSEMOTION:
                interacted = True
                self.end_pos = event.pos
            # releasing mouse to draw
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                # if starting point is too close to ending point, no line is drawn
                if (abs(self.start_pos[0] - self.end_pos[0]) < 5 and
                    abs(self.start_pos[1] - self.end_pos[1]) < 5):
                    self.keep = False
                else:
                    interacted = True
                    self.drawn = True
                    self.color = pg.Color(*CHALK_COLOR)
        # ChalkLine drawn, user click
        elif event.type == pg.MOUSEBUTTONDOWN:
            # right click to erase
            if event.button == 3 and pointOnLine(event.pos, self.start_pos, self.end_pos):
                interacted = True
                self.keep = False
            # left click to start dragging
            elif event.button == 1 and pointOnLine(event.pos, self.start_pos, self.end_pos):
                interacted = True
                self.dragging = True
                mouse_x, mouse_y = event.pos
                self.start_offset = (self.start_pos[0] - mouse_x, self.start_pos[1] - mouse_y)
                self.end_offset = (self.end_pos[0] - mouse_x, self.end_pos[1] - mouse_y)
        # user continues dragging
        elif event.type == pg.MOUSEMOTION and self.dragging:
            mouse_x, mouse_y = event.pos
            self.start_pos = (mouse_x + self.start_offset[0], mouse_y + self.start_offset[1])
            self.end_pos = (mouse_x + self.end_offset[0], mouse_y + self.end_offset[1])
        # user drops
        elif event.type == pg.MOUSEBUTTONUP and self.dragging:
            interacted = True
            self.dragging = False
        return interacted

    def update(self):
        pass

    def draw(self, screen):
        pg.draw.line(screen, self.color, self.start_pos, self.end_pos, 6)


class BlackBoard():
    def __init__(self, args_list):
        # search bar and list of items (App/ChalkText/ChalkLine)
        self.searchbar = SearchBar(BORDER_WIDTH, HEIGHT-BORDER_WIDTH-CHALK_FONT[1], "Type here to search")
        self.items = []
        # class variables for instantiating ChalkText and ChalkLine
        self.clicked = False
        self.clicked_x, self.clicked_y = 0, 0
        # initialize any existing items
        for args in args_list:
            if args[0] == "ChalkText":
                self.add_chalktext(args[1], int(args[2]), int(args[3]), False)
            elif args[0] == "ChalkLine":
                self.add_chalkline(int(args[1]), int(args[2]), int(args[3]), int(args[4]), True)
            elif args[0] == "App":
                self.add_app(args[1], int(args[2]), int(args[3]), args[4].strip())

    def handle_event(self, event):
        # handle event for search bar
        interacted = self.searchbar.handle_event(event)
        # handle event for all the items on the blackboard
        remove_idx = []
        for i in range(len(self.items)):
            item_interacted = self.items[i].handle_event(event)
            if not self.items[i].keep:
                remove_idx.append(i)
            if item_interacted:
                interacted = True
        for i in sorted(remove_idx, reverse=True):
            del self.items[i]
        # if nothing interacted with event,
        if not interacted:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.clicked = True
                self.clicked_x, self.clicked_y = event.pos
                # and the event is a dragged left click, then add a new ChalkLine
                x, y = pg.mouse.get_pos()
                self.add_chalkline(self.clicked_x, self.clicked_y , x, y, False)
            # and the event is a left click, then add a new ChalkText
            elif event.type == pg.MOUSEBUTTONUP and self.clicked:
                x, y = event.pos
                if self.clicked_x == x and self.clicked_y == y:
                    self.add_chalktext('', x, y - CHALK_FONT[1]//2, True)
                self.clicked = False
                self.clicked_x, self.clicked_y = 0, 0
        # instantiate any new pinned apps
        new_apps = self.searchbar.get_search_results()
        for path in new_apps:
            randx = r.randint(10, WIDTH//1.5)
            randy = r.randint(10, HEIGHT//1.5)
            self.add_app(path, randx, randy, None)

    def add_app(self, path, x, y, name):
        self.items.append(App(path, x, y, name))

    def add_chalktext(self, text, x, y, new):
        self.items.append(ChalkText(text, x, y, new))

    def add_chalkline(self, s_x, s_y, e_x, e_y, drawn):
        self.items.append(ChalkLine(s_x, s_y, e_x, e_y, drawn))

    def draw(self, screen):
        # draw search bar
        self.searchbar.update()
        self.searchbar.draw(screen)
        # draw all the chalks first
        apps = []
        for item in self.items:
            item.update()
            if isinstance(item, ChalkText):
                item.draw(screen)
            else:
                apps.append(item)
        # then draw the apps
        for app in apps:
            app.draw(screen)
