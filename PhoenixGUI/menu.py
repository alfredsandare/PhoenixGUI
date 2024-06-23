from .text_input import TextInput
from .menu_object import MenuObject
from .hitbox import Hitbox
from .shape import Shape
from .util import is_button, sum_two_vectors, update_pos_by_anchor

class Menu:
    def __init__(self, 
                 pos, 
                 size, 
                 layer=0, 
                 active=True, 
                 bg_color=None, 
                 outline_width=None,
                 outline_color=None,
                 enable_scroll=False, 
                 scroll_slidebar=None,
                 max_scroll_offset=0):
        self.pos = pos
        self.size = size
        self.objects: dict[str, MenuObject] = {}
        self.outline_width = outline_width
        self.outline_color = outline_color
        self.layer = layer
        self.active = active
        self.bg_color = bg_color

        self.enable_scroll = enable_scroll
        self.scroll = 0
        self.scroll_slidebar = scroll_slidebar
        self.max_scroll_offset = max_scroll_offset

        self.calculate_hitbox()

        if self.bg_color is not None:
            self.objects["_bg"] = Shape((0, 0), self.size, 
                                        self.bg_color, "rect")
        
        if self.outline_width != None and self.outline_color != None:
            self.objects["_outline"] = Shape((0, 0), 
                                             self.size, 
                                             self.outline_color, 
                                             "rect", 
                                             width=self.outline_width)

    def calculate_hitbox(self):
        self.hitbox = Hitbox(*self.pos, *sum_two_vectors(self.pos, self.size))

    def add_object(self, id, object_):
        if id in ("_bg", "_outline"):
            raise Exception("Object id cannot be '_bg' or '_outline'")
        self.objects[id] = object_

        if id == self.scroll_slidebar:
            object_.is_scroll_slidebar = True

    def delete_object(self, id):
        if id in self.objects.keys():
            del self.objects[id]
            
    def render_all(self, screen, ui_size, font_path):
        # Re-renders items with render flag and then draws all items.
        if "_bg" in self.objects.keys() and \
            not self.objects["_bg"].is_rendered():
            self.objects["_bg"].render_and_store(self.pos, self.size, 
                                                 ui_size, 0, font_path)

        if "_outline" in self.objects.keys() and \
            not self.objects["_outline"].is_rendered():
            self.objects["_outline"].render_and_store(self.pos, self.size, 
                                                      ui_size, 0, font_path)

        for key, item in self.objects.items():
            if not (item.render_flag or item.light_render_flag) \
                or key in ("_bg", "_outline"):
                continue

            if key == self.scroll_slidebar and item.active:
                item.render_and_store(self.pos, self.size, 
                                      ui_size, 0, font_path)

            elif item.active and item.render_flag:
                item.render_and_store(self.pos, self.size, 
                                      ui_size, -self.scroll, font_path)

            elif item.active and item.light_render_flag:
                item.light_render_and_store(self.pos, self.size, 
                                            ui_size, -self.scroll)

            item.render_flag = False
            item.light_render_flag = False

        # draw all
        if "_bg" in self.objects.keys():
            self.objects["_bg"].draw(screen)

        for key, item in self.objects.items():
            if key not in ("_bg", "_outline") and \
                item is not None and item.active:
                item.draw(screen)

        if "_outline" in self.objects.keys():
            self.objects["_outline"].draw(screen)
        
    def set_layer(self, layer):
        self.layer = layer

    def get_layer(self):
        return self.layer

    def reset_buttons(self):
        for obj in self.objects.values():
            if is_button(obj, include_slidebars=False):
                if obj.state != "none":
                    obj.render_flag = True
                obj.state = "none"

    def deselect_all_buttons(self):
        for obj in self.objects.values():
            if is_button(obj) and obj.is_selected:
                obj.is_selected = False

    def deselect_all_text_inputs(self):
        for obj in self.objects.values():
            if isinstance(obj, TextInput):
                obj.is_selected = False
                obj.render_flag = True

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def switch_active(self):
        self.active = not self.active

    def get_size_from_items(self):
        # gets the total size of the menu dependent on the items
        largest_x = 0
        largest_y = 0
        for key, obj in self.objects.items():
            if key in ("_bg", "_outline", self.scroll_slidebar) or \
                obj.rendered_object is None:
                continue
            
            size = obj.rendered_object.image.get_size()
            pos = update_pos_by_anchor(self.objects[key].pos, size, 
                                       self.objects[key].anchor)
            if size[0] + pos[0] > largest_x:
                largest_x = size[0] + pos[0]
            if size[1] + pos[1] > largest_y:
                largest_y = size[1] + pos[1]
        
        return (largest_x, largest_y)
    
    def set_light_render_flag_all(self):
        for obj in self.objects.values():
            obj.light_render_flag = True

    def get_max_scroll(self):
        max_scroll = (self.get_size_from_items()[1] 
                      - self.size[1]
                      + self.max_scroll_offset)
        
        if max_scroll < 0:
            max_scroll = 0

        return max_scroll

    def scroll_event(self, scroll):
        self.scroll -= scroll

        max_scroll = self.get_max_scroll()
        
        if self.scroll < 0:
            self.scroll = 0
        if self.scroll > max_scroll:
            self.scroll = max_scroll

        if self.scroll_slidebar is not None and max_scroll != 0:
            self.objects[self.scroll_slidebar].progress = self.scroll / max_scroll
        elif self.scroll_slidebar is not None:
            self.objects[self.scroll_slidebar].progress = 0

        self.set_light_render_flag_all()
        
    def set_scroll_by_progress(self, progress):
        max_scroll = self.get_max_scroll()
        self.scroll = progress * max_scroll
        self.set_light_render_flag_all()

    def reset_scroll(self):
        self.scroll = 0
        if self.scroll_slidebar is not None:
            self.objects[self.scroll_slidebar].progress = 0
        self.set_light_render_flag_all()
