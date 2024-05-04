from .menu_object import MenuObject
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
        self.menues: dict[str, MenuObject] = {}
        self.prev_menu_key = None
        self.prev_button_key = None
        self.scroll_strength_multiplier = 0
        self.selected_slidebar = None
        self.selected_slidebar_menu = None

    def update(self, events, screen):
        # sort the menues by layer
        sorted_menues = sorted(self.menues.items(), 
                               key=lambda menu: menu[1].layer, 
                               reverse=True)
        
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

        events = self._delete_unnecessary_events(events)

        for event in events:
            #print(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mousebuttondown_event(current_button, event, current_menu)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.mousebuttonup_event(current_button, current_menu)

            elif event.type == pygame.MOUSEMOTION:
                self.mousemotion_event(event)

            elif event.type == pygame.MOUSEWHEEL and current_menu.enable_scroll:
                current_menu.scroll_event(event.y * self.scroll_strength_multiplier)
        
        self.check_button_states(current_button, current_button_key, 
                                 prev_button, prev_button_key)

        self.prev_menu_key = current_menu_key
        self.prev_button_key = current_button_key

        sorted_menues.reverse()
        for key, menu in sorted_menues:
            if menu.active:
                menu.render_all(screen, self.ui_size)

    def mousebuttondown_event(self, current_button, event, current_menu):
        if current_button is not None:
            current_button.state = "click"
            current_button.is_selected = True
            current_button.render_flag = True
            if isinstance(current_button, Slidebar):
                current_button.act_on_motion(event)
                self.selected_slidebar = current_button
                self.selected_slidebar_menu = current_menu
                if current_button.is_scroll_slidebar:
                    current_menu.set_scroll_by_progress(current_button.progress)

    def mousebuttonup_event(self, current_button, current_menu):
        if current_button is not None and current_button.state == "click":
            current_button.state = "hover"
            current_button.is_selected = False
            current_button.render_flag = True
            if isinstance(current_button, Radiobutton):
                self.reset_radiobuttons(current_menu, current_button.group)
            if not isinstance(current_button, Slidebar):
                current_button.exec_command()

        elif current_button is None:
            self.deselect_all_buttons()
            
        if self.selected_slidebar is not None:
            self.selected_slidebar.state = "none"
            self.selected_slidebar.is_selected = False
            self.selected_slidebar.render_flag = True
            self.selected_slidebar = None
            self.selected_slidebar_menu = None

    def mousemotion_event(self, event):
        if self.selected_slidebar is not None:
            self.selected_slidebar.act_on_motion(event)
            if self.selected_slidebar.is_scroll_slidebar:
                self.selected_slidebar_menu.set_scroll_by_progress(
                    self.selected_slidebar.progress)

    def check_button_states(self, current_button, current_button_key, 
                            prev_button, prev_button_key):
                            
        if current_button is not None:
            if not current_button.is_selected and current_button.state == "none" and \
                self.selected_slidebar == None:
                current_button.state = "hover"
                current_button.render_flag = True

            if (current_button_key != prev_button_key and prev_button is not None 
                and not (isinstance(prev_button, Slidebar) 
                         and prev_button.is_selected)
                and self.selected_slidebar == None):
                current_button.state = "hover"
                current_button.render_flag = True
                prev_button.state = "none"
                prev_button.render_flag = True

        else:
            if (prev_button is not None 
                and not (isinstance(prev_button, Slidebar) 
                         and prev_button.is_selected)):
                prev_button.state = "none"
                prev_button.render_flag = True

    def deselect_all_buttons(self):
        for menu in self.menues.values():
            menu.deselect_all_buttons()

    def add_object(self, menu_id, object_id, _object):
        self.menues[menu_id].add_object(object_id, _object)

    def render_object(self, menu_id, object_id):
        self.menues[menu_id].render_object(object_id, self.ui_size)

    def add_menu(self, id, menu):
        self.menues[id] = menu

    def update_menu(self, id):
        self.menues[id].render_all(self.ui_size)

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
            instatiated_menu.objects = objs
            self.add_menu(menu_key, instatiated_menu)

    def add_font_path(self, path: str):
        # adds an absolute path where the menu handler will search for fonts.
        # this function should be called after all menu objects have been loaded.
        for menu in self.menues.values():
            for obj in menu.objects.values():
                if isinstance(obj, Text):
                    obj.font_path = path

    def _delete_unnecessary_events(self, events):
        # A mousewheel event also comes with a mousedown and mouseup before.
        # This deletes the two unnecessary and stupid events.
        for i, event in enumerate(events):
            if event.type == pygame.MOUSEWHEEL:
                del events[i-2:i]
        return events
    
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
