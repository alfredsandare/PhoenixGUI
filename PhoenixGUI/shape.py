from .rendered_menu_object import RenderedMenuObject
from .menu_object import MenuObject
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
        crop, pos = object_crop(self.size, pos, menu_size, menu_pos, self.max_size)

        surface = pygame.Surface(self.size, pygame.SRCALPHA)
        if self.type_ == "rect":
            pygame.draw.rect(surface,
                             self.color,
                             pygame.Rect((0, 0), self.size),
                             border_radius=self.border_radius,
                             width=self.width)
            
            if self.outline_width is not None and self.outline_color is not None:
                pygame.draw.rect(surface,
                                 self.outline_color,
                                 pygame.Rect((0, 0), self.size),
                                 border_radius=self.border_radius,
                                 width=self.outline_width)
                
        else:
            pygame.draw.ellipse(surface,
                                self.color,
                                pygame.Rect((0, 0), self.size),
                                width=self.width)
            
            if self.outline_width is not None and self.outline_color is not None:
                pygame.draw.ellipse(surface,
                                    self.outline_color,
                                    pygame.Rect((0, 0), self.size),
                                    width=self.outline_width)
                
        return RenderedMenuObject(surface, pos, crop)
