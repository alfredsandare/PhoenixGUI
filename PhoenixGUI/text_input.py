import pygame
from .rendered_menu_object import RenderedMenuObject
from .util import get_font, object_crop, update_pos_by_anchor
from .menu_object import MenuObject


class TextInput(MenuObject):
    def __init__(self,
                 pos,
                 length,
                 font,
                 font_size,
                 text_color,
                 max_size=None,
                 anchor="nw",
                 layer=0,
                 active=True):
        super().__init__(pos, max_size, anchor, layer, active)

        self.length = length
        self.font = font
        self.font_size = font_size
        self.text_color = text_color

        self.text_left = ""
        self.text_right = ""
        self.is_selected = False
        self.offset = 0

    def render(self, menu_pos, menu_size, ui_size, scroll):
        font = get_font("", self.font, self.font_size)

        surface = pygame.Surface((self.length, font.size(" ")[1]), pygame.SRCALPHA)

        surface.blit(font.render(self._get_text(), True, self.text_color), (-self.offset, 0))

        if self.is_selected:
            x_pos, height = font.size(self.text_left)
            x_pos -= self.offset
            pygame.draw.line(surface, self.text_color, (x_pos, 0), (x_pos, height), 2)

        surface_size = surface.get_size()

        crop, pos = self._adjust_pos_and_crop(self.pos, surface_size, 
                                              menu_pos, menu_size, scroll)

        return RenderedMenuObject(surface, pos, crop)
    
    def add_text(self, text):
        self.text_left += text

        font = get_font("", self.font, self.font_size)
        if font.size(self.text_left)[0] - self.offset > self.length:
            self.offset += font.size(text)[0]

    def remove_text(self):
        if not self.text_left:
            return

        font = get_font("", self.font, self.font_size)
        if (font.size(self._get_text())[0] - self.offset <= self.length):
            self.offset -= font.size(self.text_left[-1])[0]
        
        if self.offset < 0:
            self.offset = 0
            
        self.text_left = self.text_left[:-1]

        self.render_flag = True

    def step_right(self):
        if not self.text_right:
            return
        
        self.text_left += self.text_right[0]
        self.text_right = self.text_right[1:]

        font = get_font("", self.font, self.font_size)
        if font.size(self.text_left)[0] - self.offset > self.length:
            self.offset += font.size(self.text_left[-1])[0]

        self.render_flag = True

    def step_left(self):
        if not self.text_left:
            return

        self.text_right = self.text_left[-1] + self.text_right
        self.text_left = self.text_left[:-1]

        font = get_font("", self.font, self.font_size)
        if font.size(self.text_left)[0] - self.offset < 0:
            self.offset -= font.size(self.text_right[0])[0]

        if self.offset < 0:
            self.offset = 0

        self.render_flag = True

    def _get_text(self):
        return self.text_left + self.text_right
