from .menu_object import MenuObject
from .rendered_menu_object import RenderedMenuObject
from .util import object_crop, update_pos_by_anchor

class Image(MenuObject):
    def __init__(self, pos, image, max_size=None, anchor="nw"):
        super().__init__(pos, max_size, anchor)
        self.image = image

    def render(self, menu_pos, menu_size, ui_size, scroll):
        image_size = [self.image.get_rect()[2], self.image.get_rect()[3]]

        crop, pos = self._adjust_pos_and_crop(self.pos, image_size, 
                                              menu_pos, menu_size, scroll)

        return RenderedMenuObject(self.image, pos, crop)

    def get_size(self):
        return self.image.get_rect()[2:]
