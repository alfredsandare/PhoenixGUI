from PhoenixGUI.button import Button
from PhoenixGUI.menu_object import MenuObject
from PhoenixGUI.rendered_menu_object import RenderedMenuObject
from PhoenixGUI.util import get_value_from_state
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
        self.hovered_option_index = None

    def render(self, menu_pos, menu_size, ui_size, scroll, font_path=None):
        first_button = self._render_first_button(menu_pos, menu_size, ui_size,
                                                 scroll, font_path)

        if not self.is_dropped_down:
            return first_button
    
        surface = pygame.Surface((self.box_size[0], self.box_size[1]*(len(self.options)+1)))
        surface.blit(first_button.image, (0, 0))

        self._render_dropdown(menu_pos, menu_size, ui_size, scroll, font_path, surface)

        crop, pos = self._adjust_pos_and_crop(self.pos, surface.get_size(), 
                                              menu_pos, menu_size, scroll)
        
        print("pos", pos)
        return RenderedMenuObject(surface, pos, crop)

    def _render_first_button(self, menu_pos, menu_size, ui_size, scroll, font_path):
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

            if i == self.hovered_option_index:
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
