from .rendered_menu_object import RenderedMenuObject
from .image import Image
from .text import Text
from .util import object_crop, update_pos_by_anchor, flatten_list, get_value_from_state
from .shape import Shape
from .menu_object import MenuObject
import pygame

class SelectionButton(MenuObject):
    def __init__(self,
                 shape,
                 pos,
                 text,
                 font,
                 font_size,
                 max_size=None,
                 anchor="nw",

                 text_color=(255, 255, 255),
                 text_hover_color=None,
                 text_click_color=None,
                 shape_color=(255, 255, 255),
                 shape_hover_color=None,
                 shape_click_color=None,
                 shape_size=1,
                 image=None,
                 hover_image=None,
                 click_image=None,

                 text_offset=10,

                 hitbox_padding=0,
                 command=None):

        super().__init__(pos, max_size, anchor)
        self.shape = shape
        self.text = text
        self.font = font
        self.font_size = font_size
        self.text_offset = text_offset

        self.text_color = text_color
        self.text_hover_color = text_hover_color
        self.text_click_color = text_click_color
        self.shape_color = shape_color
        self.shape_hover_color = shape_hover_color
        self.shape_click_color = shape_click_color
        self.shape_size = shape_size
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

        if (shape_color != None) == (image != None) == True:
            raise Exception("Cannot instantiate checkbutton with both image and shape.")
        elif (shape_color != None) == (image != None) == False:
            raise Exception("Cannot instantiate checkbutton with neither image nor shape.")

    def set_checked(self, checked):
        self.is_checked = checked

    def get_checked(self):
        return self.is_checked

    def switch(self):
        self.is_checked = not self.is_checked

    def render(self, menu_pos, menu_size, ui_size, scroll):
        rendered_objects = []

        text_color = get_value_from_state(self.state,
                                          self.text_color,
                                          self.text_hover_color,
                                          self.text_click_color)
        
        shape_color = get_value_from_state(self.state,
                                            self.shape_color,
                                            self.shape_hover_color,
                                            self.shape_click_color)
        
        image = get_value_from_state(self.state,
                                     self.image,
                                     self.hover_image,
                                     self.click_image)

        menu_text = Text((0, 0), self.text, self.font, 
                         self.font_size, color=text_color)
        
        font_height = menu_text.get_font_height()

        text_pos = (0, 0)
        if self.image is not None:
            menu_image = Image((0, 0), image)
            rendered_objects.append(menu_image.render((0, 0), menu_size, 
                                                      ui_size, 0))
            text_pos = self._get_text_pos(menu_image.get_size(), font_height)

        else:  # shape
            shape_size = font_height*self.shape_size
            menu_shape_1 = Shape((0, 0), 
                                  (shape_size, shape_size), 
                                  shape_color, 
                                  self.shape, 
                                  width=round(0.1*shape_size))
            rendered_objects.append(menu_shape_1.render((0, 0), menu_size, 
                                                         ui_size, 0))

            # only render the middle shape when the button is checked
            if self.is_checked:
                shape_2_pos = (round(0.2*shape_size), round(0.2*shape_size))
                menu_shape_2 = Shape(shape_2_pos, 
                                      (0.6*shape_size, 0.6*shape_size), 
                                      shape_color, self.shape)
                rendered_objects.append(menu_shape_2.render((0, 0), menu_size, 
                                                             ui_size, 0))
                
            text_pos = self._get_text_pos((shape_size, shape_size), 
                                            font_height)

        rendered_objects = flatten_list(rendered_objects)

        rendered_objects.append(menu_text.render((0, 0), menu_size, ui_size, 0)[0])
        rendered_objects[-1].pos = text_pos

        x_size = max([obj.pos[0] + obj.get_image_size()[0] 
                      for obj in rendered_objects])
        y_size = max([obj.pos[1] + obj.get_image_size()[1] 
                      for obj in rendered_objects])
        
        surface_size = (x_size, y_size)
        surface = pygame.Surface(surface_size, pygame.SRCALPHA)

        for obj in rendered_objects:
            obj.draw(surface)
        
        pos = [self.pos[0] + menu_pos[0], self.pos[1] + menu_pos[1] + scroll]
        pos = update_pos_by_anchor(pos, surface_size, self.anchor)
        crop, pos_change = object_crop(surface_size, pos, 
                                       menu_size, menu_pos, self.max_size)
        pos = (pos[0] + pos_change[0], pos[1] + pos_change[1])
        
        self.hitbox = [
            pos[0] - self.hitbox_padding - menu_pos[0],
            pos[1] - self.hitbox_padding - menu_pos[1],
            pos[0] + surface_size[0] + self.hitbox_padding - menu_pos[0],
            pos[1] + surface_size[1] + self.hitbox_padding - menu_pos[1]
        ]

        return [RenderedMenuObject(surface, pos, crop)]
            
    def _get_text_pos(self, obj_size, font_height):
        x_pos = obj_size[0] + self.text_offset
        y_pos = int(obj_size[1]/2 - font_height/2)
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