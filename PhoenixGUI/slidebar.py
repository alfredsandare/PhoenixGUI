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

    def set_progress(self, progress):
        if progress < 0 or progress > 1:
            raise Exception("Progress cannot be less than zero or more than one")
        self.progress = progress

    def get_progress(self):
        return self.progress

    def render(self, menu_pos, menu_size, ui_size, scroll):
        color_to_use = self.circle_color
        if self.circle_hover_color != None and self.state == "hover":
            color_to_use = self.circle_hover_color
        elif self.circle_click_color != None and self.state == "click":
            color_to_use = self.circle_click_color

        pos = list(self.pos)
        if self.orientation == "horizontal":
            pos[0] += self.length * self.progress
        else:
            pos[1] += self.length * self.progress
        circle = Shape(pos, [self.circle_size, self.circle_size], color_to_use, 'circle', anchor="c")
        return circle.render(menu_pos, menu_size, ui_size, scroll)

    def event(self, event, menu_pos, menu_scroll):
        if event.type == pygame.MOUSEMOTION:
            if self.state == "none" and self.is_hovering(event, menu_pos):
                self.state = "hover"
                self.render_flag = True

            elif self.state == "hover" and not self.is_hovering(event, menu_pos):
                self.state = "none"
                self.render_flag = True

            elif self.state == "click" and self.orientation == "horizontal" \
                and (self.pos[0] + menu_pos[0] <= event.pos[0] <= self.pos[0] + self.length + menu_pos[0] \
                or self.progress not in (0, 1)):
                self.progress += event.rel[0] / self.length
                self.set_progress_in_limits()
                self.render_flag = True

            elif self.state == "click" and self.orientation == "vertical" \
                and (self.pos[1] + menu_pos[1] <= event.pos[1] <= self.pos[1] + self.length + menu_pos[1] \
                or self.progress not in (0, 1)):
                self.progress += event.rel[1] / self.length
                self.set_progress_in_limits()
                self.render_flag = True

        elif event.type == pygame.MOUSEBUTTONDOWN and self.state == "hover":
            self.state = "click"
            self.render_flag = True

            if self.orientation == "horizontal":
                self.progress = (event.pos[0] - menu_pos[0] - self.pos[0]) / self.length
            else:
                self.progress = (event.pos[1] - menu_pos[1] - self.pos[1] + menu_scroll) / self.length

        elif event.type == pygame.MOUSEBUTTONUP and self.state == "click":
            self.state = "hover"
            self.render_flag = True

    def is_hovering(self, event, menu_pos):
        if self.orientation == "horizontal":
            return self.pos[0] + menu_pos[0] - self.circle_size/2 <= event.pos[0] <= self.pos[0] + self.length + self.circle_size/2 + menu_pos[0] and \
                self.pos[1] - self.circle_size/2 + menu_pos[1] <= event.pos[1] <= self.pos[1] + self.circle_size/2 + menu_pos[1]
        return self.pos[0] - self.circle_size/2 + menu_pos[0] <= event.pos[0] <= self.pos[0] + self.circle_size/2 + menu_pos[0] and \
            self.pos[1] + menu_pos[1] - self.circle_size/2 <= event.pos[1] <= self.pos[1] + self.length + self.circle_size/2 + menu_pos[1]

    def set_progress_in_limits(self):
        if self.progress > 1:
            self.progress = 1
        elif self.progress < 0:
            self.progress = 0