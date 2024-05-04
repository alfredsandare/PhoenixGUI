from .hitbox import Hitbox
from .util import object_crop, sum_two_vectors, update_pos_by_anchor

class MenuObject:
    def __init__(self, pos, max_size, anchor, layer=0, active=True):
        self.pos = pos
        self.max_size = max_size
        self.anchor = anchor
        self.layer = layer
        self.active = active
        self.render_flag = True
        self.light_render_flag = True
        self.rendered_object = None
        self.hitbox = None
        self.IS_SLIDEBAR = False

    def render_and_store(self, menu_pos, menu_size, ui_size, scroll):
        self.rendered_object = self.render(menu_pos, menu_size, ui_size, scroll)
        self.update_hitbox()

    def light_render_and_store(self, menu_pos, menu_size, ui_size, scroll):
        obj = self.rendered_object
        image_size = obj.image.get_size()

        pos = [self.pos[0]+menu_pos[0], self.pos[1]+menu_pos[1]+scroll]

        if self.IS_SLIDEBAR:
            pos = self._update_pos_by_progress(pos)

        pos = update_pos_by_anchor(pos, image_size, self.anchor)
        crop, pos = object_crop(image_size, pos, menu_size, menu_pos, self.max_size)

        obj.pos = pos
        obj.crop = crop
        
        self.update_hitbox()

    def update_hitbox(self):
        if self.IS_SLIDEBAR:
            self.hitbox = self.get_hitbox(self.rendered_object.pos, self.rendered_object.get_image_size())
            return
        
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