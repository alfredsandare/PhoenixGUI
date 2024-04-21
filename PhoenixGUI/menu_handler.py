import pygame
import os
from .menu import Menu
from .rendered_menu_object import RenderedMenuObject
from .button import Button
from .checkbutton import Checkbutton
from .util import is_button
from .radiobutton import Radiobutton
from .slidebar import Slidebar

class MenuHandler:
    def __init__(self, screen, ui_size):
        self.screen = screen
        self.ui_size = ui_size
        self.menues = {}
        self.current_menu = None
        self.scroll_strength_multiplier = 0

    def update(self, events, screen):

        # sort the menues by layer
        sorted_menues = sorted(self.menues.items(), key=lambda menu: menu[1].layer, reverse=True)
        mouse_pos = pygame.mouse.get_pos()
        current_menu = None
        for key, menu in sorted_menues:
            if menu.pos[0] <= mouse_pos[0] <= menu.pos[0] + menu.size[0] and \
                menu.pos[1] <= mouse_pos[1] <= menu.pos[1] + menu.size[1] and menu.active:
                current_menu = key
                break

        if self.current_menu != current_menu and self.current_menu != None:  # mouse is hovering over a different menu
            self.menues[self.current_menu].reset_buttons()
        self.current_menu = current_menu

        sorted_menues.reverse()
        for key, menu in sorted_menues:
            if not menu.active:
                continue
            menu.render_all(screen, self.ui_size)

        if current_menu == None:
            return

        menu_pos = self.menues[current_menu].pos
        sorted_objects = sorted(self.menues[current_menu].objects.items(), key=lambda obj: obj[1].layer)
        current_button = None
        current_button_key = None
        for key, obj in self.menues[current_menu].objects.items():
            if is_button(obj) and self.compare_coords(obj.hitbox, menu_pos, mouse_pos):
                current_button = obj
                current_button_key = key

        for event in events:
            #print(event)

            if event.type == pygame.MOUSEMOTION and current_button is not None \
                and current_button.is_selected and current_button.state != "click":
                current_button.state = "click"
                current_button.render_flag = True

            elif event.type == pygame.MOUSEMOTION and current_button is not None \
                and not current_button.is_selected and current_button.state != "hover":
                current_button.state = "hover"
                current_button.render_flag = True

            elif event.type == pygame.MOUSEBUTTONDOWN and current_button is not None:
                current_button.state = "click"
                current_button.is_selected = True
                current_button.render_flag = True

            elif event.type == pygame.MOUSEBUTTONUP and current_button is not None:
                current_button.state = "hover"
                current_button.is_selected = False
                current_button.render_flag = True
                if isinstance(current_button, Radiobutton):
                    self.update_radiobuttons(current_menu, current_button.group, current_button_key)
                current_button.exec_command()

            elif event.type == pygame.MOUSEWHEEL:
                self.menues[current_menu].scroll += event.y * self.scroll_strength_multiplier
                self.menues[current_menu].set_render_flag_all()

            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                for key, obj in self.menues[current_menu].objects.items():
                    if is_button(obj) and key != current_button_key and event.type == pygame.MOUSEMOTION and obj.state != "none":
                        obj.state = "none"
                        obj.render_flag = True
                    if is_button(obj) and key != current_button_key and event.type == pygame.MOUSEBUTTONUP:
                        obj.is_selected = False

                for obj in self.menues[current_menu].objects.values():
                    if isinstance(obj, Slidebar):
                        obj.event(event, menu_pos)

    def add_object(self, menu_id, object_id, _object):
        self.menues[menu_id].add_object(object_id, _object)

    def render_object(self, menu_id, object_id):
        self.menues[menu_id].render_object(object_id, self.ui_size)

    def add_menu(self, id, menu):
        self.menues[id] = menu

    def update_menu(self, id):
        self.menues[id].render_all(self.ui_size)

    def compare_coords(self, hitbox, menu_pos, mouse_pos):
        return hitbox[0] + menu_pos[0] <= mouse_pos[0] <= hitbox[2] + menu_pos[0] and \
               hitbox[1] + menu_pos[1] <= mouse_pos[1] <= hitbox[3] + menu_pos[1]

    def update_radiobuttons(self, current_menu, group, btn_key):
        for key, obj in self.menues[current_menu].objects.items():
            if isinstance(obj, Radiobutton) and obj.group == group:
                obj.is_checked = False

    def set_scroll_strength_multiplier(self, strength):
        self.scroll_strength_multiplier = strength
        
    def get_scroll_strength_multiplier(self):
        return self.scroll_strength_multiplier