import random as r

from bb_items import *

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
