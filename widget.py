import pygame as pg
from PyQt5.QtWidgets import QApplication, QDialog, QListWidget, QVBoxLayout
from pathlib import Path
from threading import Thread
import os, sys

from header import *
from utils import get_icon

class SearchBar:
    def __init__(self, x, y, text):
        self.color = pg.Color(*CHALK_COLOR)
        self.font = pg.font.Font(*CHALK_FONT)
        self.default_text = text
        self.text = text
        self.active = False
        self.results = []

        self.text_surface = self.font.render(text, True, self.color)
        self.rect = pg.Rect(x, y, self.text_surface.get_width() + 10, CHALK_FONT[1])
    
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            # click on search bar to activate it
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            # Change the current color and text of search bar
            self.text = '' if self.active else self.default_text
            self.text_surface = self.font.render(self.text, True, self.color)
        
        # keyboard input when active
        if self.active and event.type == pg.KEYDOWN:
            # {ENTER} searches
            if event.key == pg.K_RETURN:
                Thread(target=self._search, args=(self.text,)).start()
            # {BACKSPACE} removes 1 char
            elif event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            # {ESC} clears the search bar
            elif event.key == pg.K_ESCAPE:
                self.text = ''
            # typing char
            else:
                self.text += event.unicode
            # render new text
            self.text_surface = self.font.render(self.text, True, self.color)

    def _search(self, file):
        q = QApplication(sys.argv)
        window = SearchGUI(self.results)
        window.show()
        window.searchItems(file)
        q.exec_()

    def get_search_results(self):
        if len(self.results) == 0:
            return self.results
        else:
            temp = self.results
            self.results = []
            return temp
    
    def update(self):
        self.rect.w = self.text_surface.get_width() + 10

    def draw(self, screen):
        screen.blit(self.text_surface, (self.rect.x+5, self.rect.y+5))


class SearchGUI(QDialog):
    def __init__(self, results):
        super(SearchGUI, self).__init__()
        self.setStyleSheet("background-color: rgb(30, 30, 30);")
        self.results = results
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("color: rgb(211, 211, 211);")
        self.list_widget.itemDoubleClicked.connect(self.addAndReturn)

        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)

    def searchItems(self, file):
        for path in Path('/').rglob(file):
            self.list_widget.addItem(str(path))

    def addAndReturn(self, item):
        self.results.append(item.text())
        QApplication.quit()


class App:
    def __init__(self, path, x, y, w, h):
        self.path = Path(path)
        self.x, self.y, self.w, self.h = x, y, w, h
        self.old_x, self.old_y = x, y
        self.offset_x, self.offset_y = 0, 0
        self.dragging = False

        self.font = pg.font.Font(*APP_FONT)
        self.rect_color = pg.Color(*APP_COLOR)
        self.border_color = pg.Color(*APP_BORDER_COLOR)
        self.text_color = pg.Color(*APP_TEXT_COLOR)
        self.img = pg.image.load(APP_IMG)
        icon = get_icon(path, "large")
        raw = icon.tobytes("raw", "RGBA")
        self.icon = pg.image.frombuffer(raw, icon.size, "RGBA")

        self.rect = pg.Rect(x, y, w, h)
        self.border = pg.Rect(x-2, y-2, w, h)
        self.text_surface = self.font.render(self.path.name, True, self.text_color)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # start dragging
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.dragging = True
                self.old_x, self.old_y = self.x, self.y
                mouse_x, mouse_y = event.pos
                self.offset_x = self.x - mouse_x
                self.offset_y = self.y - mouse_y
            
            # right click to unpin
            if event.button == 3 and self.rect.collidepoint(event.pos):
                return False
        # continue dragging
        elif event.type == pg.MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = event.pos
                self.x = mouse_x + self.offset_x
                self.y = mouse_y + self.offset_y
        # drop
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.dragging = False
                # launch app if clicked (and not dragged)
                if self.x == self.old_x and self.y == self.old_y:
                    os.startfile(self.path)

        return True

    def update(self):
        # update position of rect
        self.rect = pg.Rect(self.x, self.y, self.w, self.h)

    def draw(self, screen):
        pg.Surface.fill(screen, self.rect_color, self.rect)
        pg.draw.rect(screen, self.border_color, self.rect, 2)
        screen.blit(self.icon, (self.x + APP_WIDTH//2.5, self.y + APP_HEIGHT//2.5))
        screen.blit(self.text_surface, (self.x+2, self.y + APP_HEIGHT - APP_FONT[1]))
        
    def draw_img(self, screen):
        screen.blit(self.img, (self.x + APP_WIDTH//2.5, self.y-25))


class Chalk():
    def __init__(self, x, y):
        self.font = pg.font.Font(*CHALK_FONT)
        self.color = pg.Color(*CHALK_COLOR)
        self.active = True
        self.text = ''

        self.text_surface = self.font.render(text, True, self.color)
        self.rect = pg.Rect(x, y, self.text_surface.get_width() + 10, CHALK_FONT[1])

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
        
        if self.active and event.type == pg.KEYDOWN:
            # {ENTER} to finish writing
            if event.key == pg.K_RETURN:
                self.active = False
            # {BACKSPACE} removes 1 char
            elif event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            # {ESC} erases the chalk
            elif event.key == pg.K_ESCAPE:
                self.text = ''
            # typing char
            else:
                self.text += event.unicode
            self.text_surface = self.font.render(self.text, True, self.color)

    def update(self):
        self.rect.width = self.text_surface.get_width() + 10

    def draw(self, screen):
        screen.blit(self.text_surface, (self.rect.x, self.rect.y))
