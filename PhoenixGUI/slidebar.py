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
        self.IS_SLIDEBAR = True

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

        pos = self._update_pos_by_progress(pos)

        circle = Shape(pos, 
                       [self.circle_size, self.circle_size], 
                       color, 
                       'circle')
        return circle.render(menu_pos, menu_size, ui_size, scroll)

    def act_on_motion(self, event):
        if ((self.orientation == "vertical" and event.pos[1] > self.hitbox.bottom)
            or (self.orientation == "horizontal" and event.pos[0] > self.hitbox.right)):
            self.progress = 1
            self.render_flag = True
            return
        
        elif ((self.orientation == "vertical" and event.pos[1] < self.hitbox.top)
            or (self.orientation == "horizontal" and event.pos[0] < self.hitbox.left)):
            self.progress = 0
            self.render_flag = True
            return

        relative_mouse_pos = (event.pos[1] - self.hitbox.top
            if self.orientation == "vertical" else 
                event.pos[0] - self.hitbox.left) - self.circle_size/2

        self.progress = relative_mouse_pos / self.length
        self.set_progress_in_limits()
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

    def _update_pos_by_progress(self, pos):
        if self.orientation == "horizontal":
            pos[0] += (self.length - self.circle_size) * self.progress
        else:  # horizontal
            pos[1] += (self.length - self.circle_size) * self.progress
        return pos