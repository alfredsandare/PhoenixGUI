from .hitbox import Hitbox
from .util import sum_two_vectors

class MenuObject:
    def __init__(self, pos, max_size, anchor, layer=0, active=True):
        self.pos = pos
        self.max_size = max_size
        self.anchor = anchor
        self.layer = layer
        self.active = active
        self.render_flag = True
        self.rendered_object = None
        self.hitbox = None

    def render_and_store(self, menu_pos, menu_size, ui_size, scroll):
        self.rendered_object = self.render(menu_pos, menu_size, ui_size, scroll)
        self.hitbox = Hitbox(*self.rendered_object.pos, 
                             *sum_two_vectors(self.rendered_object.pos, 
                                              self.rendered_object.image.get_size()))
        
    def draw(self, screen):
        self.rendered_object.draw(screen)
    
    def is_rendered(self):
        return self.rendered_object is not None

    def set_layer(self, layer):
        self.layer = layer

    def get_layer(self):
        return self.layer

    def set_pos(self, pos):
        self.pos = pos

    def get_pos(self):
        return self.pos

    def set_max_size(self, max_size):
        self.max_size = max_size

    def get_max_size(self):
        return self.max_size

    def set_anchor(self, anchor):
        self.anchor = anchor

    def get_anchor(self):
        return self.anchor

    def get_active(self):
        return self.active

    def activate(self):
        self.active = True
        self.render_flag = True

    def deactivate(self):
        self.active = False
        self.render_flag = True

    def switch_active(self):
        self.active = not self.active
        self.render_flag = True