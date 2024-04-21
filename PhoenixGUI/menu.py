from .shape import Shape
from .util import flatten_list, is_button
import time

class Menu:
    def __init__(self, pos, size, layer=0, active=True, bg_color=None):
        self.pos = pos
        self.size = size
        self.objects = {}
        self.rendered_objects = {}
        self.outline_width = None
        self.outline_color = None
        self.layer = layer
        self.active = active
        self.bg_color = bg_color

        self.enable_scroll = False
        self.scroll = 0
        self.scroll_slidebar = None

    def add_object(self, id, _object):
        if id in ("_bg", "_outline"):
            raise Exception("Object id cannot be '_bg' or '_outline'")
        self.objects[id] = _object

    def render_all(self, screen, ui_size):
        time_stamp = time.time()
        if self.bg_color != None:
            rect = Shape((0, 0), self.size, self.bg_color, "rect")
            self.rendered_objects["_bg"] = rect.render(self.pos, self.size, ui_size)[0]

        if self.outline_width != None and self.outline_color != None:
            rect = Shape((0, 0), self.size, self.outline_color, "rect", width=self.outline_width)
            self.rendered_objects["_outline"] = rect.render(self.pos, self.size, ui_size)[0]

        for key, item in self.objects.items():
            if item.render_flag:
                rendered = item.render(self.pos, self.size, ui_size)
                self.rendered_objects[key] = rendered
                item.render_flag = False

        self.draw_all(screen)

    def draw_all(self, screen):
        items = flatten_list(self.rendered_objects.values())
        for item in items:
            item.draw(screen)

    def set_layer(self, layer):
        self.layer = layer

    def get_layer(self):
        return self.layer

    def set_outline(self, width, color):
        self.outline_width = width
        self.outline_color = color

    def reset_buttons(self):
        for obj in self.objects.values():
            if is_button(obj):
                obj.state = "none"

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def get_size_from_items(self):
        # gets the total size of the menu dependent on the items
        largest_x = 0
        largest_y = 0
        for obj in self.rendered_objects:
            size = obj.image.get_size()
            pos = obj.pos()
            if size[0] + pos[0] > largest_x:
                largest_x = size[0] + pos[0]
            if size[1] + pos[1] > largest_y:
                largest_y = size[1] + pos[1]
        
        return (largest_x, largest_y)
    