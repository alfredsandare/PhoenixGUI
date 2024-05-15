import pygame
import importlib
from .menu import Menu
from .util import is_button
from .radiobutton import Radiobutton
from .slidebar import Slidebar
from .text import Text


class MenuHandler:
    def __init__(self, ui_size=1):
        self.ui_size = ui_size
        self.menues: dict[str, Menu] = {}
        self.prev_menu_key = None
        self.prev_button_key = None
        self.scroll_strength_multiplier = 0
        self.selected_slidebar = None
        self.selected_slidebar_menu = None
        self.font_path = None

    def update(self, events, screen):
        # sort the menues by layer
        sorted_menues = self._get_sorted_menues(reverse=True)
        mouse_pos = pygame.mouse.get_pos()
        current_menu_key = self._get_current_menu_key(mouse_pos, sorted_menues)

        if ((self.prev_menu_key != current_menu_key 
             and self.prev_menu_key != None)  # mouse is hovering over a different menu
            or (current_menu_key == None 
                and self.prev_menu_key != None)):  # mouse stopped hovering over any menu
            self.menues[self.prev_menu_key].reset_buttons()

        current_menu = None
        if current_menu_key != None:
            current_menu = self.menues[current_menu_key]

        current_button, current_button_key, prev_button, prev_button_key = \
            self._get_buttons_data(current_menu, mouse_pos)

        for event in events:
            #print(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._mousebuttondown_event(current_button, event, current_menu)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._mousebuttonup_event(current_button, current_menu)

            elif event.type == pygame.MOUSEMOTION:
                self._mousemotion_event(event)

            elif current_menu is not None and event.type == pygame.MOUSEWHEEL \
                and current_menu.enable_scroll:
                current_menu.scroll_event(event.y * self.scroll_strength_multiplier)
        
        self._update_button_states(current_button, current_button_key, 
                                 prev_button, prev_button_key)

        self.prev_menu_key = current_menu_key
        self.prev_button_key = current_button_key

        self._render_and_draw_menues(screen)

    def _mousebuttondown_event(self, current_button, event, current_menu):
        if current_button is None:
            return

        current_button.state = "click"
        current_button.is_selected = True
        current_button.render_flag = True

        if isinstance(current_button, Slidebar):
            current_button.act_on_motion(event)
            self.selected_slidebar = current_button
            self.selected_slidebar_menu = current_menu

        if isinstance(current_button, Slidebar) \
            and current_button.is_scroll_slidebar:
            current_menu.set_scroll_by_progress(current_button.progress)

    def _mousebuttonup_event(self, current_button, current_menu):
        if current_button is not None and current_button.state == "click":
            current_button.state = "hover"
            current_button.is_selected = False
            current_button.render_flag = True
            if isinstance(current_button, Radiobutton):
                self.reset_radiobuttons(current_menu, current_button.group)
            if not isinstance(current_button, Slidebar):
                current_button.exec_command()

        self.deselect_all_buttons()
            
        if self.selected_slidebar is not None:
            self.selected_slidebar.state = "none"
            self.selected_slidebar.is_selected = False
            self.selected_slidebar.render_flag = True
            self.selected_slidebar = None
            self.selected_slidebar_menu = None

    def _mousemotion_event(self, event):
        if self.selected_slidebar is None:
            return
        
        self.selected_slidebar.act_on_motion(event)
        if self.selected_slidebar.is_scroll_slidebar:
            self.selected_slidebar_menu.set_scroll_by_progress(
                self.selected_slidebar.progress)

    def _update_button_states(self, current_button, current_button_key, 
                            prev_button, prev_button_key):
                            
        if (current_button is not None 
            and self.selected_slidebar == None
            and current_button.state == "none" 
            and prev_button is None):

            # mouse started hovering over a button
            
            self._enable_button_by_hover(current_button)

        elif (current_button is not None 
              and self.selected_slidebar == None
              and current_button_key != prev_button_key 
              and prev_button is not None 
              and not (isinstance(prev_button, Slidebar) 
                       and prev_button.is_selected)):
            
            # mouse jumped straight from one button to another
            
            self._enable_button_by_hover(current_button)
            self._disable_button_by_hover(prev_button)

        elif (current_button is None
              and prev_button is not None 
              and not (isinstance(prev_button, Slidebar) 
                       and prev_button.is_selected)):
            
            # mouse stopped hovering over a button
            
            self._disable_button_by_hover(prev_button)

    def _enable_button_by_hover(self, button):
        if button.is_selected:
            button.state = "click"
        else:
            button.state = "hover"
        button.render_flag = True

    def _disable_button_by_hover(self, button):
        button.state = "none"
        button.render_flag = True

    def deselect_all_buttons(self):
        for menu in self.menues.values():
            menu.deselect_all_buttons()

    def add_object(self, menu_id, object_id, _object):
        self.menues[menu_id].add_object(object_id, _object)

        if isinstance(_object, Text) and self.font_path is not None:
            _object.font_path = self.font_path

    def add_menu(self, id, menu):
        self.menues[id] = menu

    def reset_radiobuttons(self, current_menu, group):
        for obj in current_menu.objects.values():
            if isinstance(obj, Radiobutton) and obj.group == group:
                if obj.is_checked:
                    obj.render_flag = True
                obj.is_checked = False

    def set_scroll_strength_multiplier(self, strength):
        self.scroll_strength_multiplier = strength
        
    def get_scroll_strength_multiplier(self):
        return self.scroll_strength_multiplier
    
    def load_data_from_dict(self, data: dict, images: dict):
        for menu_key, menu in data.items():
            objs = {}
            for obj_key, obj in menu["objects"].items():
                module = importlib.import_module("." + obj["type"], 
                                                 package=__package__)
                class_ = getattr(module, obj["type"].capitalize())

                image_keys = ["image", "hover_image", "click_image"]
                for image_key in image_keys:
                    if image_key in obj.keys():
                        obj[image_key] = images[obj[image_key]]

                del obj["type"]
                objs[obj_key] = class_(**obj)

            del menu["objects"]
            instatiated_menu = Menu(**menu)
            instatiated_menu.deactivate()
            instatiated_menu.objects.update(objs)
            self.add_menu(menu_key, instatiated_menu)

    def add_font_path(self, path: str):
        # adds an absolute path where the menu handler will search for fonts.
        self.font_path = path
        for menu in self.menues.values():
            for obj in menu.objects.values():
                if isinstance(obj, Text):
                    obj.font_path = path

    def _get_current_menu_key(self, mouse_pos, sorted_menues):
        for key, menu in sorted_menues:
            if menu.hitbox.is_pos_inside(*mouse_pos) and menu.active:
                return key
        return None
    
    def _get_buttons_data(self, current_menu, mouse_pos):
        current_button = None
        current_button_key = None
        if current_menu != None:
            for key, obj in current_menu.objects.items():
                if is_button(obj) and obj.hitbox.is_pos_inside(*mouse_pos):
                    current_button = obj
                    current_button_key = key

        prev_button_key = self.prev_button_key
        prev_button = None
        if prev_button_key is not None and self.prev_menu_key is not None:
            prev_button = self.menues[self.prev_menu_key].objects[prev_button_key]

        return current_button, current_button_key, prev_button, prev_button_key

    def _render_and_draw_menues(self, screen):
        for key, menu in self._get_sorted_menues():
            if menu.active:
                menu.render_all(screen, self.ui_size)

    def _get_sorted_menues(self, reverse=False):
        return sorted(self.menues.items(), 
                      key=lambda menu: menu[1].layer, 
                      reverse=reverse)
        