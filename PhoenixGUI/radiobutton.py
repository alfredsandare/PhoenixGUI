from .text import Text
from .util import update_pos_by_anchor, flatten_list
from .shape import Shape
from .menu_object import MenuObject 

class Radiobutton(MenuObject):
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
                 circle_color=(255, 255, 255),
                 circle_hover_color=None,
                 circle_click_color=None,
                 circle_size=1,
                 image=None,
                 hover_image=None,
                 click_image=None,

                 text_offset=10,

                 hitbox_padding=0,
                 command=None,
                 group=None):

        super().__init__(pos, max_size, anchor)
        self.text = text
        self.font = font
        self.font_size = font_size
        self.text_offset = text_offset

        self.text_color = text_color
        self.text_hover_color = text_hover_color
        self.text_click_color = text_click_color
        self.circle_color = circle_color
        self.circle_hover_color = circle_hover_color
        self.circle_click_color = circle_click_color
        self.circle_size = circle_size
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
        self.group = group

        if (circle_color != None) == (image != None) == True:
            raise Exception("Cannot instantiate radiobutton with both image and circle.")
        elif (circle_color != None) == (image != None) == False:
            raise Exception("Cannot instantiate radiobutton with neither image nor circle.")

    def set_checked(self, checked):
        self.is_checked = checked

    def get_checked(self):
        return self.is_checked

    def switch(self):
        self.is_checked = not self.is_checked

    def render(self, menu_pos, menu_size, ui_size):
        rendered_objects = []

        text_color = self.text_color
        if self.state == "hover" and self.text_hover_color != None:
            text_color = self.text_hover_color
        elif self.state == "click" and self.text_click_color != None:
            text_color = self.text_click_color

        circle_color = self.circle_color
        if self.state == "hover" and self.circle_hover_color != None:
            circle_color = self.circle_hover_color
        elif self.state == "click" and self.circle_click_color != None:
            circle_color = self.circle_click_color

        image = self.image
        if self.state == "hover" and self.hover_image != None:
            image = self.hover_image
        elif self.state == "click" and self.click_image != None:
            image = self.click_image

        menu_text = Text(self.pos, self.text, self.font, self.font_size, color=text_color)
        text_size = menu_text.get_size(menu_pos, menu_size, ui_size)

        if self.image != None:
            menu_image = Image(self.pos, image)
            rendered_objects.append(menu_image.render(menu_pos, menu_size, ui_size))
            menu_text.pos = self._update_text_pos(menu_image.get_size(), text_size)
            total_x_size = menu_image.get_size()[0] + self.text_offset + text_size[0]
            total_y_size = max([menu_image.get_size()[1], text_size[1]])

        else:  # circle
            circle_size = text_size[1]*self.circle_size
            menu_circle_1 = Shape(self.pos, (circle_size, circle_size), circle_color, "ellipse", width=round(0.1*circle_size))
            rendered_objects.append(menu_circle_1.render(menu_pos, menu_size, ui_size))

            if self.is_checked:  # only render the middle circle when the button is checked
                circle_2_pos = (round(self.pos[0]+0.2*circle_size), round(self.pos[1]+0.2*circle_size))
                menu_circle_2 = Shape(circle_2_pos, (0.6*circle_size, 0.6*circle_size), circle_color, "ellipse")
                rendered_objects.append(menu_circle_2.render(menu_pos, menu_size, ui_size))
  
            menu_text.pos = self._update_text_pos((circle_size, circle_size), text_size)
            total_x_size = circle_size + self.text_offset + text_size[0]
            total_y_size = max([circle_size, text_size[1]])

        rendered_objects.append(menu_text.render(menu_pos, menu_size, ui_size))

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
        self.set_checked(True)
        if self.command is not None:
            self.command()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False