import pygame
from .rendered_menu_object import RenderedMenuObject
from .util import get_font
from .menu_object import MenuObject

class validity_check:
    NATURAL = 100  # 0, 1, 2, 3, ...
    INTEGERS = 101 # -3, -2, -1, 0, 1, 2, 3, ...
    ALL_NUMBERS_COMMA = 102 # -3, -2, -1, 0, 1, 2, 3, ..., 0.1, 0.2, 0.3, ... using comma signs to indicate decimals
    ALL_NUMBERS_DOTS = 103 # -3, -2, -1, 0, 1, 2, 3, ..., 0.1, 0.2, 0.3, ... using dots to indicate decimals
    ALL_NUMBERS_DOTS_COMMA = 104 # -3, -2, -1, 0, 1, 2, 3, ..., 0.1, 0.2, 0.3, ... using dots or comma signs to indicate decimals

class TextInput(MenuObject):
    def __init__(self,
                 pos,
                 length,
                 font,
                 font_size,
                 text_color=(255, 255, 255),
                 validity_check=None,
                 invalid_text_color=(255, 0, 0),
                 max_size=None,
                 anchor="nw",
                 layer=0,
                 active=True,
                 command=None):

        super().__init__(pos, max_size, anchor, layer, active)

        self.length = length
        self.font = font
        self.font_size = font_size
        self.text_color = text_color
        self.validity_check = validity_check
        self.invalid_text_color = invalid_text_color
        self.command = command

        self.text_left = ""
        self.text_right = ""
        self.is_selected = False
        self.offset = 0
        self.is_valid = True

    def render(self, menu_pos, menu_size, ui_size, scroll, font_path=None):
        font = get_font(font_path, self.font, self.font_size)

        surface_size = (self.length, font.size(" ")[1])
        surface = pygame.Surface(surface_size, pygame.SRCALPHA)

        text_color = self.text_color if self.is_valid else self.invalid_text_color
        rendered_text = font.render(self.get_text(), True, text_color)
        surface.blit(rendered_text, (-self.offset, 0))

        if self.is_selected:
            x_pos, height = font.size(self.text_left)
            x_pos -= self.offset
            pygame.draw.line(surface, self.text_color, 
                             (x_pos, 0), (x_pos, height), 2)

        crop, pos = self._adjust_pos_and_crop(self.pos, surface_size, 
                                              menu_pos, menu_size, scroll)

        return RenderedMenuObject(surface, pos, crop)
    
    def add_text(self, text):
        self.text_left += text

        font = get_font("", self.font, self.font_size)
        if font.size(self.text_left)[0] - self.offset > self.length:
            self.offset += font.size(text)[0]

        self.render_flag = True
        self.check_validity()
        self.exec_command()

    def remove_text(self):
        if not self.text_left:
            return

        font = get_font("", self.font, self.font_size)
        if (font.size(self.get_text())[0] - self.offset <= self.length):
            self.offset -= font.size(self.text_left[-1])[0]
        
        if self.offset < 0:
            self.offset = 0
            
        self.text_left = self.text_left[:-1]

        self.render_flag = True
        self.check_validity()
        self.exec_command()

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

    def get_text(self):
        return (self.text_left + self.text_right).strip()
    
    def get_text_raw(self):
        return self.text_left + self.text_right

    def check_validity(self):
        if self.validity_check == validity_check.NATURAL:
            self.is_valid = self.get_text().isdigit()

        elif self.validity_check == validity_check.INTEGERS:
            self.is_valid = self.get_text().lstrip("-").isdigit()
            
        elif self.validity_check == validity_check.ALL_NUMBERS_COMMA:
            self.is_valid = self.get_text().replace(".", "").lstrip("-").replace(",", "", 1).isdigit()

        elif self.validity_check == validity_check.ALL_NUMBERS_DOTS:
            self.is_valid = self.get_text().replace(",", "").lstrip("-").replace(".", "", 1).isdigit()

        elif self.validity_check == validity_check.ALL_NUMBERS_DOTS_COMMA:
            # disallow more than one dot or comma
            text = self.get_text()
            self.is_valid = text.replace(",", "").replace(".", "").lstrip("-").isdigit() \
                            and text.count(".") + text.count(",") <= 1
            
    def get_validity(self):
        return self.is_valid

    def exec_command(self):
        if self.command is not None and callable(self.command):
            self.command()
        elif type(self.command) is tuple:
            command, args, kwargs = self.command
            command(*args, **kwargs)

    def set_text(self, text):
        self.text_left = text
        self.text_right = ""
        self.offset = 0
        self.render_flag = True
        self.check_validity()
