from .menu_object import MenuObject
from .rendered_menu_object import RenderedMenuObject
from .util import get_value_from_state, object_crop, get_font, flatten_list, update_pos_by_anchor
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
                 hitbox_padding=0,
                 command=None,

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
                 rect_outline_click_color=None):

        super().__init__(pos, max_size, anchor)
        self.image = image
        self.hover_image = hover_image
        self.click_image = click_image
        self.text = text
        self.font = font
        self.font_size = font_size
        self.text_color = text_color
        self.text_hover_color = text_hover_color
        self.text_click_color = text_click_color
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

        self.state = "none"
        self.is_selected = False  # becomes true when clicked on, and only becomes false when LMB is released
        self.enabled = True

        if self.text == None and self.image == None:
            raise Exception("Cannot instanstiate button with neither text nor image.")
        
        if self.image is not None and self.enable_rect:
            raise Exception("Cannot instaniate button with both image and rect.")

    def render(self, menu_pos, menu_size, ui_size, scroll):
        if self.image is not None:
            image_to_use = get_value_from_state(self.state,
                                                self.image,
                                                self.hover_image,
                                                self.click_image)

            menu_image = Image((0, 0), 
                               image_to_use, 
                               max_size=self.max_size, 
                               anchor=self.anchor)
            rendered_menu_image = menu_image.render(menu_pos, menu_size, 
                                                    ui_size, scroll)

        if self.text:
            text_color_to_use = get_value_from_state(self.state,
                                                     self.text_color,
                                                     self.text_hover_color,
                                                     self.text_click_color)
            
            pos = (0, 0)
            if self.enable_rect:
                pos = (self.rect_padx, self.rect_pady)

            menu_text = Text(pos, 
                             self.text, 
                             self.font, 
                             self.font_size, 
                             max_size=self.max_size,
                             wrap_lines=False,
                             color=text_color_to_use)
            rendered_menu_text = menu_text.render(menu_pos, menu_size, ui_size, scroll)

        if self.enable_rect:
            text_size = rendered_menu_text.get_image_size()
            rect_size = (text_size[0] + 2*self.rect_padx, text_size[1] + 2*self.rect_pady)

            rect_color = get_value_from_state(self.state,
                                              self.rect_color,
                                              self.rect_hover_color,
                                              self.rect_click_color)

            rect_outline_color = get_value_from_state(self.state,
                                                      self.rect_outline_color,
                                                      self.rect_outline_hover_color,
                                                      self.rect_outline_click_color)

            menu_rect = Shape((0, 0),
                             rect_size,
                             rect_color,
                             "rect",
                             outline_width=self.rect_outline_width,
                             outline_color=rect_outline_color,
                             border_radius=self.rect_border_radius,
                             max_size=self.max_size)
            rendered_menu_rect = menu_rect.render(menu_pos, menu_size, ui_size, scroll)
            
        surface_size = (0, 0)
        if self.image is not None:
            surface_size = rendered_menu_image.get_image_size()
        elif self.enable_rect:
            surface_size = rendered_menu_rect.get_image_size()
        else:
            surface_size = rendered_menu_text.get_image_size()
            
        surface = pygame.Surface(surface_size, pygame.SRCALPHA)
            
        if self.image is not None:
            surface.blit(rendered_menu_image.image, (0, 0))
        if self.enable_rect:
            surface.blit(rendered_menu_rect.image, (0, 0))
        if self.text:
           surface.blit(rendered_menu_text.image, (self.rect_padx, self.rect_pady))

        pos = [self.pos[0] + menu_pos[0], self.pos[1] + menu_pos[1] + scroll]
        pos = update_pos_by_anchor(pos, surface_size, self.anchor)
        crop, pos = object_crop(surface_size, pos, 
                                       menu_size, menu_pos, self.max_size)
        
        return RenderedMenuObject(surface, pos, crop)

    def exec_command(self):
        if self.command is not None and self.enabled:
            self.command()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False