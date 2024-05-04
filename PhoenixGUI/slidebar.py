from .util import get_value_from_state, update_pos_by_anchor
from .hitbox import Hitbox
import pygame
from .shape import Shape
from .menu_object import MenuObject

class Slidebar(MenuObject):
    def __init__(self,
                 pos,
                 length,
                 circle_size,
                 max_size=None,
                 anchor="nw",
                 orientation="horizontal",
                 circle_color=(255, 255, 255),
                 circle_hover_color=None,
                 circle_click_color=None
                 ):
        super().__init__(pos, max_size, anchor)
        self.length = length
        self.circle_size = circle_size
        self.circle_color = circle_color
        self.circle_hover_color = circle_hover_color
        self.circle_click_color = circle_click_color

        self.progress = 0
        self.state = "none"
        self.orientation = orientation
        self.is_scroll_slidebar = False
        self.is_selected = False

    def set_progress(self, progress):
        if progress < 0 or progress > 1:
            raise Exception("Progress cannot be less than zero or more than one")
        self.progress = progress

    def get_progress(self):
        return self.progress

    def render(self, menu_pos, menu_size, ui_size, scroll):
        color = get_value_from_state(self.state, self.circle_color, 
                                     self.circle_hover_color, 
                                     self.circle_click_color)

        if self.orientation == "horizontal":
            total_size = [self.length, self.circle_size]
        else:
            total_size = [self.circle_size, self.length]

        pos = list(update_pos_by_anchor(self.pos, total_size, self.anchor))

        if self.orientation == "horizontal":
            pos[0] += (self.length - self.circle_size) * self.progress
        else:
            pos[1] += (self.length - self.circle_size) * self.progress

        circle = Shape(pos, 
                       [self.circle_size, self.circle_size], 
                       color, 
                       'circle')
        return circle.render(menu_pos, menu_size, ui_size, scroll)

    def event(self, event, menu_pos, menu_scroll):
        if event.type == pygame.MOUSEMOTION:
            if self.state == "none" and self.is_hovering(event, menu_pos):
                self.state = "hover"
                self.render_flag = True

            elif self.state == "hover" and not self.is_hovering(event, menu_pos):
                self.state = "none"
                self.render_flag = True

            elif (self.state == "click" 
                  and self.orientation == "horizontal" 
                  and (self.pos[0] + menu_pos[0] 
                       <= event.pos[0] 
                       <= self.pos[0] + self.length + menu_pos[0] 
                       or self.progress not in (0, 1))):
                
                self.progress += event.rel[0] / self.length
                self.set_progress_in_limits()
                self.render_flag = True

            elif (self.state == "click" 
                  and self.orientation == "vertical" 
                  and (self.pos[1] + menu_pos[1] 
                       <= event.pos[1] 
                       <= self.pos[1] + self.length + menu_pos[1] 
                       or self.progress not in (0, 1))):
                
                self.progress += event.rel[1] / self.length
                self.set_progress_in_limits()
                self.render_flag = True

        elif event.type == pygame.MOUSEBUTTONDOWN and self.state == "hover":
            self.state = "click"
            self.render_flag = True

            if self.orientation == "horizontal":
                self.progress = (event.pos[0] 
                                 - menu_pos[0] 
                                 - self.pos[0]) / self.length
            else:
                self.progress = (event.pos[1] 
                                 - menu_pos[1] 
                                 - self.pos[1] 
                                 + menu_scroll) / self.length

        elif event.type == pygame.MOUSEBUTTONUP and self.state == "click":
            self.state = "hover"
            self.render_flag = True

    def get_hitbox(self, rendered_pos, rendered_size):
        length_from_progress = self.progress * self.length
        if self.orientation == "vertical":
            top = rendered_pos[1] - length_from_progress
            bottom = top + self.length + rendered_size[1]
            left = rendered_pos[0]
            right = rendered_pos[0] + rendered_size[0]

        else:
            top = rendered_pos[1]
            bottom = rendered_pos[1] + rendered_size[1]
            left = rendered_pos[0] - length_from_progress
            right = left + self.length + rendered_size[0]

        # might need to set the hitbox inside menu borders here

        return Hitbox(left, top, right, bottom)

    def set_progress_in_limits(self):
        if self.progress > 1:
            self.progress = 1
        elif self.progress < 0:
            self.progress = 0