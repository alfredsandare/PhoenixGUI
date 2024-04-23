from .rendered_menu_object import RenderedMenuObject
from .shape import Shape
from .util import flatten_list, is_button, update_pos_by_anchor
import time

class Menu:
    def __init__(self, pos, size, layer=0, active=True, bg_color=None, enable_scroll=False, scroll_slidebar=None):
        self.pos = pos
        self.size = size
        self.objects = {}
        self.rendered_objects = {}
        self.outline_width = None
        self.outline_color = None
        self.layer = layer
        self.active = active
        self.bg_color = bg_color

        self.enable_scroll = enable_scroll
        self.scroll = 0
        self.scroll_slidebar = scroll_slidebar

    def add_object(self, id, _object):
        if id in ("_bg", "_outline"):
            raise Exception("Object id cannot be '_bg' or '_outline'")
        self.objects[id] = _object

    def render_all(self, screen, ui_size):
        if self.bg_color != None:
            rect = Shape((0, 0), self.size, self.bg_color, "rect")
            self.rendered_objects["_bg"] = rect.render(self.pos, self.size, ui_size, 0)[0]

        if self.outline_width != None and self.outline_color != None:
            rect = Shape((0, 0), self.size, self.outline_color, "rect", width=self.outline_width)
            self.rendered_objects["_outline"] = rect.render(self.pos, self.size, ui_size, 0)[0]

        for key, item in self.objects.items():
            if item.render_flag:
                if key == self.scroll_slidebar:
                    rendered = item.render(self.pos, self.size, ui_size, 0)
                else:
                    rendered = item.render(self.pos, self.size, ui_size, -self.scroll)
                self.rendered_objects[key] = rendered
                item.render_flag = False

        self.draw_all(screen)

    def draw_all(self, screen):
        if "_bg" in self.rendered_objects.keys():
            self.rendered_objects["_bg"].draw(screen)

        for key, items in self.rendered_objects.items():
            if key not in ("_bg", "_outline"):
                for item in items:
                    item.draw(screen)

        if "_outline" in self.rendered_objects.keys():
            self.rendered_objects["_outline"].draw(screen)
        
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
        pairs = []
        for key, objs in self.rendered_objects.items():
            if key in ("_bg", "_outline", self.scroll_slidebar):
                continue
            for obj in objs:
                pairs.append([key, obj])

        for key, obj in pairs:
            if isinstance(obj, RenderedMenuObject):
                size = obj.image.get_size()
            else:  # RenderedMenuShape
                size = obj.size
            pos = update_pos_by_anchor(self.objects[key].pos, size, self.objects[key].anchor)
            if size[0] + pos[0] > largest_x:
                largest_x = size[0] + pos[0]
            if size[1] + pos[1] > largest_y:
                largest_y = size[1] + pos[1]
        
        return (largest_x, largest_y)
    
    def set_render_flag_all(self):
        for obj in self.objects.values():
            obj.render_flag = True

    def scroll_event(self, scroll):
        self.scroll -= scroll

        max_scroll = self.get_size_from_items()[1] - self.size[1] \
            if self.get_size_from_items()[1] > 0 else 0
        
        if self.scroll < 0:
            self.scroll = 0
        if self.scroll > max_scroll:
            self.scroll = max_scroll

        if self.scroll_slidebar is not None:
            self.objects[self.scroll_slidebar].progress = self.scroll / max_scroll

        self.set_render_flag_all()
        
    def set_scroll_by_progress(self, progress):
        max_scroll = self.get_size_from_items()[1] - self.size[1] \
            if self.get_size_from_items()[1] > 0 else 0
        self.scroll = progress * max_scroll
        self.set_render_flag_all()