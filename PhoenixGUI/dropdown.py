from PhoenixGUI.button import Button
from PhoenixGUI.hitbox import Hitbox
from PhoenixGUI.menu_object import MenuObject
from PhoenixGUI.rendered_menu_object import RenderedMenuObject
from PhoenixGUI.util import get_value_from_state, sum_two_vectors
import pygame


class Dropdown(MenuObject):
    def __init__(self, 
                 pos, 
                 box_size,
                 font,
                 font_size,
                 options,
                 selected_option,
                 max_size=None,
                 anchor="nw",

                 box_bg_color=None,
                 box_bg_hover_color=None,
                 box_bg_click_color=None,
                 box_outline_color=None,
                 box_outline_hover_color=None,
                 box_outline_click_color=None):

        super().__init__(pos, max_size, anchor)

        self.box_size = box_size
        self.font = font
        self.font_size = font_size
        self.options = options
        self.selected_option = selected_option

        self.box_bg_color = box_bg_color
        self.box_bg_hover_color = box_bg_hover_color
        self.box_bg_click_color = box_bg_click_color
        self.box_outline_color = box_outline_color
        self.box_outline_hover_color = box_outline_hover_color
        self.box_outline_click_color = box_outline_click_color

        self.is_dropped_down = False
        self.state = "none"
        self.hovered_option_index = None  # 0 is the first button, 1 is the first option, 2 is the second option, etc.
        self.is_selected = False

    def render(self, menu_pos, menu_size, ui_size, scroll, font_path=None):
        first_button = self._render_first_button(menu_pos, menu_size, ui_size,
                                                 scroll, font_path)
    
        surface = pygame.Surface((self.box_size[0], self.box_size[1]*(len(self.options)+1)))
        surface.blit(first_button.image, (0, 0))

        if self.is_dropped_down:
            self._render_dropdown(menu_pos, menu_size, ui_size, scroll, font_path, surface)

        crop, pos = self._adjust_pos_and_crop(self.pos, surface.get_size(), 
                                              menu_pos, menu_size, scroll)

        return RenderedMenuObject(surface, pos, crop)

    def _render_first_button(self, menu_pos, menu_size, ui_size, scroll, font_path):
        bg_color = self.box_bg_color
        outline_color = self.box_outline_color
        if self.hovered_option_index == 0:        
            bg_color = get_value_from_state(self.state, 
                                            self.box_bg_color, 
                                            self.box_bg_hover_color, 
                                            self.box_bg_click_color)

            outline_color = get_value_from_state(self.state, 
                                                    self.box_outline_color, 
                                                    self.box_outline_hover_color, 
                                                    self.box_outline_click_color)

        button = Button((0, 0),
                        enable_rect=True,
                        rect_length=self.box_size[0],
                        rect_height=self.box_size[1],
                        text=self.selected_option,
                        font=self.font,
                        font_size=self.font_size,
                        rect_color=bg_color,
                        rect_outline_color=outline_color)

        return button.render(menu_pos, menu_size, ui_size, scroll, font_path)

    def _render_dropdown(self, menu_pos, menu_size, ui_size, scroll, font_path, surface):
        for i, option in enumerate(self.options):
            bg_color = self.box_bg_color
            outline_color = self.box_outline_color

            if i+1 == self.hovered_option_index:
                bg_color = get_value_from_state(self.state, 
                                                self.box_bg_color, 
                                                self.box_bg_hover_color, 
                                                self.box_bg_click_color)

                outline_color = get_value_from_state(self.state, 
                                                    self.box_outline_color, 
                                                    self.box_outline_hover_color, 
                                                    self.box_outline_click_color)

            button = Button((0, 0),
                            enable_rect=True,
                            rect_length=self.box_size[0],
                            rect_height=self.box_size[1],
                            text=option,
                            font=self.font,
                            font_size=self.font_size,
                            rect_color=bg_color,
                            rect_outline_color=outline_color)

            rendered_button = button.render(menu_pos, menu_size, ui_size, scroll, font_path)
            surface.blit(rendered_button.image, (0, (i+1)*self.box_size[1]))

    def handle_mousebuttonup(self, mouse_pos):
        if self.is_mouse_on_first_button(mouse_pos):
            self.is_dropped_down = not self.is_dropped_down
            return
        
        # now the mouse was not hovering over the first button.

        self.selected_option = self.options[self.hovered_option_index-1]
        self.is_dropped_down = False

    def handle_mousemotion(self, mouse_pos):
        # because this function is called, the mouse is hovering over this object.

        old_index = self.hovered_option_index

        if not self.is_dropped_down or \
            (self.is_dropped_down and self.is_mouse_on_first_button(mouse_pos)):
            self.hovered_option_index = 0

        for i, option in enumerate(self.options):
            option_pos = (self.rendered_object.pos[0], 
                          self.rendered_object.pos[1]+self.box_size[1]*(i+1))
            option_hitbox = Hitbox(*option_pos, 
                                   *sum_two_vectors(option_pos, self.box_size))

            if option_hitbox.is_pos_inside(*mouse_pos):
                self.hovered_option_index = i+1
                break

        if old_index != self.hovered_option_index:
            self.render_flag = True

    def is_mouse_on_first_button(self, mouse_pos):
        relative_right_bottom = (self.rendered_object.image.get_size()[0], 
                                 self.box_size[1])

        first_button_hitbox = Hitbox(*self.rendered_object.pos, 
                                     *sum_two_vectors(self.rendered_object.pos, 
                                                      relative_right_bottom))
        
        return first_button_hitbox.is_pos_inside(*mouse_pos)
