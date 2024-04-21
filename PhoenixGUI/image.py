from .menu_object import MenuObject
from .rendered_menu_object import RenderedMenuObject
from .util import object_crop, update_pos_by_anchor

class Image(MenuObject):
    def __init__(self, pos, image, max_size=None, anchor="nw"):
        super().__init__(pos, max_size, anchor)
        self.image = image

    def render(self, menu_pos, menu_size, ui_size=1):
        image_size = [self.image.get_rect()[2], self.image.get_rect()[3]]

        pos = [self.pos[0]+menu_pos[0], self.pos[1]+menu_pos[1]]
        pos = update_pos_by_anchor(pos, image_size, self.anchor)
        crop, pos_change = object_crop(image_size, pos, menu_size, menu_pos, self.max_size)
        pos = (pos[0]+pos_change[0], pos[1]+pos_change[1])
        return [RenderedMenuObject(self.image, pos, crop)]

    def get_size(self):
        return self.image.get_rect()[2:]
