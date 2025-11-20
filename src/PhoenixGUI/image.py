from .menu_object import MenuObject
from .rendered_menu_object import RenderedMenuObject

class Image(MenuObject):
    def __init__(self, pos, image, max_size=None, anchor="nw", layer=0,
                 hover_text=None):
        super().__init__(pos, max_size, anchor, layer=layer,
                         hover_text=hover_text)
        self.image = image

    def render(self, menu_pos, menu_size, ui_size, scroll, font_path=None):
        image_size = [self.image.get_rect()[2], self.image.get_rect()[3]]

        crop, pos = self._adjust_pos_and_crop(self.pos, image_size, 
                                              menu_pos, menu_size, scroll)

        return RenderedMenuObject(self.image, pos, crop)

    def get_size(self):
        return self.image.get_rect()[2:]
