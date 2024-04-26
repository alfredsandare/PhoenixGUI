from .menu_object import MenuObject
from .rendered_menu_object import RenderedMenuObject
from .util import object_crop, get_font, flatten_list
from .image import Image
from .text import Text
from .shape import Shape

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
                 text_color=None,
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
        self.hitbox = []
        self.is_selected = False  # becomes true when clicked on, and only becomes false when LMB is released
        self.enabled = True

        if self.text == None and self.image == None:
            raise Exception("Cannot instanstiate button with neither text nor image.")

    def render(self, menu_pos, menu_size, ui_size, scroll):
        rendered_objects = []
        if self.image:
            image_to_use = self.image
            if self.state == "hover" and self.hover_image != None:
                image_to_use = self.hover_image
            elif self.state == "click" and self.click_image != None:
                image_to_use = self.click_image

            menu_image = Image(self.pos, 
                               image_to_use, 
                               max_size=self.max_size, 
                               anchor=self.anchor)
            rendered_menu_image = menu_image.render(menu_pos, menu_size, ui_size, scroll)

        if self.text:
            text_color_to_use = self.text_color
            if self.state == "hover" and self.text_hover_color != None:
                text_color_to_use = self.text_hover_color
            elif self.state == "click" and self.text_click_color != None:
                text_color_to_use = self.text_click_color

            pos = self.pos
            if self.enable_rect:
                pos = [self.pos[0] + self.rect_padx, self.pos[1] + self.rect_pady]

            menu_text = Text(pos, 
                             self.text, 
                             self.font, 
                             self.font_size, 
                             max_size=self.max_size,
                             anchor=self.anchor,
                             wrap_lines=True,
                             color=text_color_to_use)
            rendered_menu_text = menu_text.render(menu_pos, menu_size, ui_size, scroll)

        if self.enable_rect:
            text_size = menu_text.get_size(menu_pos, menu_size, ui_size, scroll)
            rect_size = (text_size[0] + 2*self.rect_padx, text_size[1] + 2*self.rect_pady)

            rect_color = self.rect_color
            if self.state == "hover" and self.rect_hover_color != None:
                rect_color = self.rect_hover_color
            elif self.state == "click" and self.rect_click_color != None:
                rect_color = self.rect_click_color

            rect_outline_color = self.rect_outline_color
            if self.state == "hover" and self.rect_outline_hover_color != None:
                rect_outline_color = self.rect_outline_hover_color
            elif self.state == "click" and self.rect_outline_click_color != None:
                rect_outline_color = self.rect_outline_click_color

            menu_rect = Shape(self.pos,
                             rect_size,
                             rect_color,
                             "rect",
                             outline_width=self.rect_outline_width,
                             outline_color=rect_outline_color,
                             border_radius=self.rect_border_radius,
                             max_size=self.max_size,
                             anchor=self.anchor)
            rendered_menu_rect = menu_rect.render(menu_pos, menu_size, ui_size, scroll)

        largest_x = max([menu_text.get_size(menu_pos, menu_size, ui_size, scroll)[0] if self.text else 0,
                         menu_image.get_size()[0] if self.image else 0,
                         menu_rect.size[0] if self.enable_rect else 0])

        largest_y = max([menu_text.get_size(menu_pos, menu_size, ui_size, scroll)[1] if self.text else 0,
                         menu_image.get_size()[1] if self.image else 0,
                         menu_rect.size[1] if self.enable_rect else 0])

        self.hitbox = [
            self.pos[0] - self.hitbox_padding,
            self.pos[1] - self.hitbox_padding + scroll,
            self.pos[0] + largest_x + self.hitbox_padding,
            self.pos[1] + largest_y + self.hitbox_padding + scroll
        ]

        to_return = []
        if self.enable_rect:
            to_return.append(rendered_menu_rect)
        if self.image:
            to_return.append(rendered_menu_image)
        if self.text:
            to_return.append(rendered_menu_text)
        return flatten_list(to_return)

    def exec_command(self):
        if self.command is not None and self.enabled:
            self.command()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False