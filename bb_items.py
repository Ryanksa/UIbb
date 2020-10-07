import pygame as pg
from pathlib import Path
import os

from header import *
from utils import get_icon, pointOnLine
from widgets import *

class App:
    def __init__(self, path, x, y, color, name):
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
        self.font = pg.font.Font(APP_FONT, APP_FONTSIZE)
        self.color_idx = color
        self.text_color = pg.Color(*COLOR_PAL[color])
        self.icon = get_icon(path, "large")
        # instances that make up an App instance
        self.options_menu = AppOptionsMenu(self)
        self.rect = pg.Rect(x, y, 32, 32)
        self.text_surface = self.font.render(self.name, True, self.text_color)

    def handle_event(self, event):
        interacted = False
        if self.options_opened:
            # options menu open, events go there
            interacted = True
            self.options_menu.handle_event(event)
        elif self.renaming:
            interacted = True
            # clicking away, saves current name and stop renaming
            if event.type == pg.MOUSEBUTTONDOWN:
                self.old_name = self.name
                self.text_color = pg.Color(*COLOR_PAL[self.color_idx])
                self.renaming = False
            # typing something while renaming
            if event.type == pg.KEYDOWN:
                # {ENTER} saves current name and stops renaming
                if event.key == pg.K_RETURN:
                    self.old_name = self.name
                    self.text_color = pg.Color(*COLOR_PAL[self.color_idx])
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
                    self.text_color = pg.Color(*COLOR_PAL[self.color_idx])
                    self.renaming = False
                # else typing a char
                else:
                    self.name += event.unicode
            self.text_surface = self.font.render(self.name, True, self.text_color)
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
        elif event.type == pg.MOUSEMOTION:
            # continue dragging
            if self.dragging:
                interacted = True
                mouse_x, mouse_y = event.pos
                self.x = mouse_x + self.offset_x
                self.y = mouse_y + self.offset_y
        elif event.type == pg.MOUSEBUTTONUP:
            # drop
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
        # draw options menu if opened
        if self.options_opened:
            self.options_menu.draw(screen)


class ChalkText():
    def __init__(self, text, x, y, fontsize, color, new):
        self.text = text
        self.old_text = text
        # class variables for font and color
        self.fontsize = fontsize
        self.font = pg.font.Font(CHALK_FONT, self.fontsize)
        self.color_idx = color
        self.color = pg.Color(*EDITING_COLOR) if new else pg.Color(*COLOR_PAL[color])
        # class variables for state of this ChalkText
        self.keep = True
        self.active = True if new else False
        self.dragging = False
        self.options_opened = False
        # class variables for position and movement
        self.x, self.y = x, y
        self.old_x, self.old_y = x, y
        self.offset_x, self.offset_y = 0, 0
        # instances that make up a ChalkText instance
        self.options_menu = ChalkTextOptionsMenu(self)
        self.text_surface = self.font.render(text, True, self.color)
        self.rect = pg.Rect(self.x, self.y, self.text_surface.get_width() + 10, self.fontsize)

    def handle_event(self, event):
        interacted = False
        # options menu open, events go there
        if self.options_opened:
            interacted = True
            self.options_menu.handle_event(event)
        # active and typing
        elif self.active and event.type == pg.KEYDOWN:
            interacted = True
            # {ENTER} to finish writing
            if event.key == pg.K_RETURN:
                self.old_text = self.text
                self.active = False
                self.color = pg.Color(*COLOR_PAL[self.color_idx])
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
                self.color = pg.Color(*COLOR_PAL[self.color_idx])
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
            # right click to open the options menu for this ChalkText
            if event.button == 3 and self.rect.collidepoint(event.pos):
                interacted = True
                self.options_menu.setpos(*event.pos)
                self.options_opened = True
        elif event.type == pg.MOUSEMOTION:
            # continue dragging
            if self.dragging:
                interacted = True
                mouse_x, mouse_y = event.pos
                self.x = mouse_x + self.offset_x
                self.y = mouse_y + self.offset_y
        elif event.type == pg.MOUSEBUTTONUP:
            # drop
            if event.button == 1 and self.rect.collidepoint(event.pos):
                interacted = True
                self.dragging = False
                # activate if clicked (and not dropped)
                if self.x == self.old_x and self.y == self.old_y:
                    self.active = True
                    self.color = pg.Color(*EDITING_COLOR)
            # left click off ChalkText de-activates it
            elif event.button == 1 and not self.rect.collidepoint(event.pos):
                self.active = False
                self.color = pg.Color(*COLOR_PAL[self.color_idx])
            self.text_surface = self.font.render(self.text, True, self.color)
        return interacted

    def update(self):
        self.rect.x, self.rect.y = self.x, self.y
        self.rect.width = self.text_surface.get_width() + 10
        self.rect.height = self.fontsize 

    def draw(self, screen):
        screen.blit(self.text_surface, (self.x, self.y))
        # draw options menu if opened
        if self.options_opened:
            self.options_menu.draw(screen)


class ChalkLine:
    def __init__(self, s_x, s_y, e_x, e_y, width, color, drawn):
        # class variable for line position
        self.start_pos = (s_x, s_y)
        self.end_pos = (e_x, e_y)
        # class variable for color and various states
        self.color_idx = color
        self.color = pg.Color(*COLOR_PAL[color]) if drawn else pg.Color(*EDITING_COLOR)
        self.drawn = drawn
        self.keep = True
        self.width = width
        # class variables used for drag and drop
        self.dragging = False
        self.start_offset = (0, 0)
        self.end_offset = (0, 0)
        # class variables for options menu
        self.options_menu = ChalkLineOptionsMenu(self)
        self.options_opened = False

    def handle_event(self, event):
        interacted = False
        # if this ChalkLine is already drawn
        if self.drawn:
            if self.options_opened:
                # options menu is open, handle events there
                interacted = True
                self.options_menu.handle_event(event)
            elif event.type == pg.MOUSEBUTTONDOWN:
                # right click to open options menu
                if event.button == 3 and pointOnLine(event.pos, self.start_pos, self.end_pos):
                    interacted = True
                    self.options_menu.setpos(*event.pos)
                    self.options_opened = True
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
        # if this ChalkLine is still not drawn yet
        else:
            interacted = True
            # moving mouse to determine final position
            if event.type == pg.MOUSEMOTION:
                self.end_pos = event.pos
            # releasing mouse click to draw
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                # if starting point is too close to ending point, no line is drawn
                if (abs(self.start_pos[0] - self.end_pos[0]) < 5 and
                    abs(self.start_pos[1] - self.end_pos[1]) < 5):
                    interacted = False
                    self.keep = False
                else:
                    self.drawn = True
                    self.color = pg.Color(*COLOR_PAL[self.color_idx])
        return interacted

    def update(self):
        # nothing to update
        pass

    def draw(self, screen):
        pg.draw.line(screen, self.color, self.start_pos, self.end_pos, self.width)
        # draw options menu if opened
        if self.options_opened:
            self.options_menu.draw(screen)
