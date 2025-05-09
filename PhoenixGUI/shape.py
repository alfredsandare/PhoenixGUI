from .rendered_menu_object import RenderedMenuObject
from .menu_object import MenuObject
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
                 anchor="nw",
                 layer=0,
                 hover_text=None):

        super().__init__(pos, max_size, anchor, hover_text=hover_text,
                         layer=layer)
        self.size = size
        self.color = color
        self.type_ = type_
        self.outline_width = outline_width
        self.outline_color = outline_color
        self.border_radius = border_radius
        self.width = width

        if type_ not in ("rect", "circle"):
            raise Exception("Shape type must be either 'rect' or 'circle'")

    def render(self, menu_pos, menu_size, ui_size, scroll, font_path=None):
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
                                
        crop, pos = self._adjust_pos_and_crop(self.pos, self.size, 
                                              menu_pos, menu_size, scroll)
                
        return RenderedMenuObject(surface, pos, crop)
