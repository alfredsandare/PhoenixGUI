from .image import Image
from .text import Text
from .util import update_pos_by_anchor, flatten_list
from .shape import Shape
from .menu_object import MenuObject 

class Checkbutton(MenuObject):
    def __init__(self,
                 pos,
                 text,
                 font,
                 font_size,
                 max_size=None,
                 anchor="nw",

                 text_color=(255, 255, 255),
                 text_hover_color=None,
                 text_click_color=None,
                 square_color=(255, 255, 255),
                 square_hover_color=None,
                 square_click_color=None,
                 square_size=1,
                 image=None,
                 hover_image=None,
                 click_image=None,

                 text_offset=10,

                 hitbox_padding=0,
                 command=None):

        super().__init__(pos, max_size, anchor)
        self.text = text
        self.font = font
        self.font_size = font_size
        self.text_offset = text_offset

        self.text_color = text_color
        self.text_hover_color = text_hover_color
        self.text_click_color = text_click_color
        self.square_color = square_color
        self.square_hover_color = square_hover_color
        self.square_click_color = square_click_color
        self.square_size = square_size
        self.image = image
        self.hover_image = hover_image
        self.click_image = click_image

        self.hitbox_padding = hitbox_padding
        self.command = command

        self.is_checked = False
        self.state = "none"
        self.hitbox = []
        self.is_selected = False  # becomes true when clicked on, and only becomes false when LMB is released
        self.enabled = True

        if (square_color != None) == (image != None) == True:
            raise Exception("Cannot instantiate checkbutton with both image and square.")
        elif (square_color != None) == (image != None) == False:
            raise Exception("Cannot instantiate checkbutton with neither image nor square.")

    def set_checked(self, checked):
        self.is_checked = checked

    def get_checked(self):
        return self.is_checked

    def switch(self):
        self.is_checked = not self.is_checked

    def render(self, menu_pos, menu_size, ui_size, scroll):
        rendered_objects = []

        text_color = self.text_color
        if self.state == "hover" and self.text_hover_color != None:
            text_color = self.text_hover_color
        elif self.state == "click" and self.text_click_color != None:
            text_color = self.text_click_color

        square_color = self.square_color
        if self.state == "hover" and self.square_hover_color != None:
            square_color = self.square_hover_color
        elif self.state == "click" and self.square_click_color != None:
            square_color = self.square_click_color

        image = self.image
        if self.state == "hover" and self.hover_image != None:
            image = self.hover_image
        elif self.state == "click" and self.click_image != None:
            image = self.click_image

        menu_text = Text(self.pos, self.text, self.font, self.font_size, color=text_color)
        text_size = menu_text.get_size(menu_pos, menu_size, ui_size, scroll)

        if self.image != None:
            menu_image = Image(self.pos, image)
            rendered_objects.append(menu_image.render(menu_pos, menu_size, ui_size, scroll))
            menu_text.pos = self._update_text_pos(menu_image.get_size(), text_size)
            total_x_size = menu_image.get_size()[0] + self.text_offset + text_size[0]
            total_y_size = max([menu_image.get_size()[1], text_size[1]])

        else:  # square
            square_size = text_size[1]*self.square_size
            menu_square_1 = Shape(self.pos, (square_size, square_size), square_color, "rect", width=round(0.1*square_size))
            rendered_objects.append(menu_square_1.render(menu_pos, menu_size, ui_size, scroll))

            if self.is_checked:  # only render the middle square when the button is checked
                square_2_pos = (round(self.pos[0]+0.2*square_size), round(self.pos[1]+0.2*square_size))
                menu_square_2 = Shape(square_2_pos, (0.6*square_size, 0.6*square_size), square_color, "rect")
                rendered_objects.append(menu_square_2.render(menu_pos, menu_size, ui_size, scroll))
  
            menu_text.pos = self._update_text_pos((square_size, square_size), text_size)
            total_x_size = square_size + self.text_offset + text_size[0]
            total_y_size = max([square_size, text_size[1]])

        rendered_objects.append(menu_text.render(menu_pos, menu_size, ui_size, scroll))

        rendered_objects = flatten_list(rendered_objects)
        for obj in rendered_objects:
            obj.pos = update_pos_by_anchor(obj.pos, (total_x_size, total_y_size), self.anchor)

        self.hitbox = [
            rendered_objects[0].pos[0] - self.hitbox_padding - menu_pos[0],
            rendered_objects[0].pos[1] - self.hitbox_padding - menu_pos[1],
            rendered_objects[0].pos[0] + total_x_size + self.hitbox_padding - menu_pos[0],
            rendered_objects[0].pos[1] + total_y_size + self.hitbox_padding - menu_pos[1]
        ]

        return rendered_objects
            
    def _update_text_pos(self, obj_size, text_size):
        x_pos = self.pos[0] + obj_size[0] + self.text_offset
        y_pos = int(self.pos[1] + obj_size[1]/2 - text_size[1]/2)
        return (x_pos, y_pos)

    def exec_command(self):
        if not self.enabled:
            return
        self.switch()
        if self.command is not None:
            self.command()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False