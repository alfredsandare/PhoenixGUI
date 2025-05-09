from .menu_object import MenuObject
from .rendered_menu_object import RenderedMenuObject
from .util import get_value_from_state
from .image import Image
from .text import Text
from .shape import Shape
import pygame

class Button(MenuObject):
    def __init__(self, 
                 pos, 
                 max_size=None, 
                 anchor="nw",
                 image=None, 
                 hover_image=None, 
                 click_image=None, 
                 text=None, 
                 font=None, 
                 font_size=None, 
                 text_color=(255, 255, 255),
                 text_hover_color=None,
                 text_click_color=None,
                 text_justify="center",  # left, right or center
                 hitbox_padding=0,
                 command=None,
                 layer=0,
                 hover_text=None,

                 enable_rect=False,
                 rect_padx=0,
                 rect_pady=0,
                 rect_border_radius=0,
                 rect_outline_width=1,
                 rect_color=(0, 0, 0),
                 rect_hover_color=None,
                 rect_click_color=None,
                 rect_outline_color=None,
                 rect_outline_hover_color=None,
                 rect_outline_click_color=None,
                 rect_length=None,
                 rect_height=None):

        super().__init__(pos, max_size, anchor, hover_text=hover_text,
                         layer=layer)
        self.image = image
        self.hover_image = hover_image
        self.click_image = click_image
        self.text = text
        self.font = font
        self.font_size = font_size
        self.text_color = text_color
        self.text_hover_color = text_hover_color
        self.text_click_color = text_click_color
        self.text_justify = text_justify
        self.hitbox_padding = hitbox_padding
        self.command = command

        self.enable_rect = enable_rect
        self.rect_padx = rect_padx
        self.rect_pady = rect_pady
        self.rect_border_radius = rect_border_radius
        self.rect_outline_width = rect_outline_width
        self.rect_color = rect_color
        self.rect_hover_color = rect_hover_color
        self.rect_click_color = rect_click_color
        self.rect_outline_color = rect_outline_color
        self.rect_outline_hover_color = rect_outline_hover_color
        self.rect_outline_click_color = rect_outline_click_color
        self.rect_length = rect_length
        self.rect_height = rect_height

        self.state = "none"
        self.is_selected = False  # becomes true when clicked on, and only becomes false when LMB is released
        self.enabled = True

        if self.text is None and self.image is None and not self.enable_rect:
            raise Exception("Cannot instanstiate button with neither text nor image nor rect.")
        
        if (self.text is None and self.image is None and self.enable_rect 
            and (self.rect_length is None or self.rect_height is None)):
            raise Exception("Cannot instanstiate button with rect without length and height")
        
        if self.image is not None and self.enable_rect:
            raise Exception("Cannot instaniate button with both image and rect.")
        
        if self.rect_length is not None and self.rect_padx != 0:
            raise Exception("Cannot instantiate button with both rect_length and rect_padx")
        
        if self.enable_rect and self.text is None and \
            (self.rect_length is None or self.rect_height is None):
            raise Exception("Button instantiated without text must have rect_length and rect_height.")

        if self.text_justify not in ["left", "center", "right"]:
            raise Exception(f"Invalid text_justify value: {self.text_justify}, must be 'left', 'center' or 'right'")

    def render(self, menu_pos, menu_size, ui_size, scroll, font_path=None):
        rendered_image = self._get_rendered_image(menu_pos, menu_size, 
                                                  ui_size, scroll)
        
        rendered_text = self._get_rendered_text(menu_pos, menu_size, 
                                                ui_size, scroll, font_path)
        
        text_size = None
        if rendered_text is not None:
            text_size = rendered_text.get_image_size()
        rect_size = self._get_rect_size(text_size)
        
        rendered_rect = self._get_rendered_rect(menu_pos, menu_size, 
                                                ui_size, scroll, rect_size)
        
        text_pos = self._get_text_pos(rendered_text, rendered_image, 
                                      rect_size, text_size)
        
        sizes = [rendered_image.get_image_size() if rendered_image is not None else (0, 0),
                 rendered_text.get_image_size() if rendered_text is not None else (0, 0),
                 rendered_rect.get_image_size() if rendered_rect is not None else (0, 0)]
        
        surface_size = (max([s[0] for s in sizes]), max([s[1] for s in sizes]))
        surface = pygame.Surface(surface_size, pygame.SRCALPHA)

        if rendered_image is not None:
            surface.blit(rendered_image.image, (0, 0))
        if rendered_rect is not None:
            surface.blit(rendered_rect.image, (0, 0))
        if rendered_text is not None:
            surface.blit(rendered_text.image, text_pos)

        crop, pos = self._adjust_pos_and_crop(self.pos, surface_size, 
                                              menu_pos, menu_size, scroll)
        
        return RenderedMenuObject(surface, pos, crop)

    def exec_command(self):
        if self.command is not None and self.enabled and callable(self.command):
            self.command()
        elif type(self.command) is tuple and self.enabled:
            command, args, kwargs = self.command
            command(*args, **kwargs)

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

        
    def _get_rendered_image(self, menu_pos, menu_size, ui_size, scroll):
        if self.image is None:
            return None
        
        image_to_use = get_value_from_state(self.state,
                                            self.image,
                                            self.hover_image,
                                            self.click_image)

        menu_image = Image((0, 0), 
                           image_to_use, 
                           max_size=self.max_size, 
                           anchor=self.anchor)
        
        return menu_image.render(menu_pos, menu_size, ui_size, scroll)
    
    def _get_rendered_text(self, menu_pos, menu_size, ui_size, scroll, font_path):
        if self.text is None:
            return None
        
        text_color_to_use = get_value_from_state(self.state,
                                                 self.text_color,
                                                 self.text_hover_color,
                                                 self.text_click_color)

        menu_text = Text((0, 0), 
                         self.text, 
                         self.font, 
                         self.font_size, 
                         max_size=self.max_size,
                         wrap_lines=False,
                         color=text_color_to_use)
        
        return menu_text.render(menu_pos, menu_size, ui_size, scroll, font_path)
    
    def _get_rendered_rect(self, menu_pos, menu_size, ui_size, scroll, size):
        if not self.enable_rect:
            return None

        rect_color = get_value_from_state(self.state,
                                          self.rect_color,
                                          self.rect_hover_color,
                                          self.rect_click_color)

        rect_outline_color = get_value_from_state(self.state,
                                                  self.rect_outline_color,
                                                  self.rect_outline_hover_color,
                                                  self.rect_outline_click_color)

        menu_rect = Shape((0, 0),
                          size,
                          rect_color,
                          "rect",
                          outline_width=self.rect_outline_width,
                          outline_color=rect_outline_color,
                          border_radius=self.rect_border_radius,
                          max_size=self.max_size)
        
        return menu_rect.render(menu_pos, menu_size, ui_size, scroll)
    
    def _get_rect_size(self, text_size):
        rect_size = [0, 0]

        if self.enable_rect and self.text is None:
            return [self.rect_length, self.rect_height]

        if self.enable_rect and self.text is not None:

            if self.rect_length is not None and self.rect_length >= text_size[0]:
                rect_size[0] = self.rect_length
            elif self.rect_length is not None:
                rect_size[0] = text_size[0]
            else:
                rect_size[0] = text_size[0] + self.rect_padx

            if self.rect_height is not None and self.rect_height >= text_size[1]:
                rect_size[1] = self.rect_height
            elif self.rect_height is not None:
                rect_size[1] = text_size[1]
            else:
                rect_size[1] = text_size[1] + self.rect_pady

        elif (self.enable_rect and self.text is not None
              and self.rect_length is None and self.rect_height is None):
            
            rect_size = [text_size[0] + self.rect_padx, 
                         text_size[1] + self.rect_pady]
            
        return rect_size

    def _get_text_pos(self, rendered_text, rendered_image,
                      rect_size, text_size):
        
        text_pos = (0, 0)
        if rendered_text is not None and self.enable_rect:
            text_pos = (self._get_text_x_pos(rect_size[0], text_size),
                        (rect_size[1] - text_size[1]) / 2)

        elif rendered_text is not None and self.image is not None:
            image_size = rendered_image.get_image_size()
            text_pos = (self._get_text_x_pos(image_size[0], text_size),
                        (image_size[1] - text_size[1]) / 2)

        return text_pos

    def _get_text_x_pos(self, rect_or_image_width, text_size):
        SIDE_OFFSET = 5
        if self.text_justify == "left":
            return SIDE_OFFSET
        elif self.text_justify == "center":
            return (rect_or_image_width - text_size[0]) / 2
        elif self.text_justify == "right":
            return rect_or_image_width - text_size[0] - SIDE_OFFSET
