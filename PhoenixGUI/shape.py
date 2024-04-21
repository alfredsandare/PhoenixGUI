from .menu_object import MenuObject
from .rendered_menu_shape import RenderedMenuShape
from .util import object_crop, update_pos_by_anchor
import pygame

class Shape(MenuObject):
    def __init__(self, 
                 pos, 
                 size, 
                 color,
                 type_,
                 outline_width=None, 
                 outline_color=None, 
                 border_radius=0,
                 width=0,
                 max_size=None, 
                 anchor="nw"):

        super().__init__(pos, max_size, anchor)
        self.size = size
        self.color = color
        self.type_ = type_
        self.outline_width = outline_width
        self.outline_color = outline_color
        self.border_radius = border_radius
        self.width = width

    def render(self, menu_pos, menu_size, ui_size, scroll):
        pos = [self.pos[0]+menu_pos[0], self.pos[1]+menu_pos[1]+scroll]
        pos = update_pos_by_anchor(pos, self.size, self.anchor)
        crop, pos_change = object_crop(self.size, pos, menu_size, menu_pos, self.max_size)
        pos = (pos[0]+pos_change[0], pos[1]+pos_change[1])

        return [RenderedMenuShape(pos, 
                                  self.size, 
                                  self.color,
                                  crop,
                                  self.type_,
                                  outline_width=self.outline_width,
                                  outline_color=self.outline_color,
                                  border_radius=self.border_radius,
                                  width=self.width)]