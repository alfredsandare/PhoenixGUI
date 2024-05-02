from .menu_object import MenuObject
import pygame
import importlib
from .menu import Menu
from .rendered_menu_object import RenderedMenuObject
from .util import is_button
from .radiobutton import Radiobutton
from .slidebar import Slidebar
from .text import Text


class MenuHandler:
    def __init__(self, ui_size=1):
        self.ui_size = ui_size
        self.menues: dict[str, MenuObject] = {}
        self.current_menu_key = None
        self.scroll_strength_multiplier = 0

    def update(self, events, screen):
        # sort the menues by layer
        sorted_menues = sorted(self.menues.items(), 
                               key=lambda menu: menu[1].layer, 
                               reverse=True)
        
        mouse_pos = pygame.mouse.get_pos()
        current_menu_key = None
        for key, menu in sorted_menues:
            if menu.hitbox.is_pos_inside(*mouse_pos) and menu.active:
                current_menu_key = key
                break

        if (self.current_menu_key != current_menu_key 
            and self.current_menu_key != None):
            # mouse is hovering over a different menu
            self.menues[self.current_menu_key].reset_buttons()

        sorted_menues.reverse()
        for key, menu in sorted_menues:
            if not menu.active:
                continue
            menu.render_all(screen, self.ui_size)

        self.current_menu_key = current_menu_key
        if current_menu_key == None:
            return
        current_menu = self.menues[current_menu_key]

        menu_pos = current_menu.pos
        #sorted_objects = sorted(current_menu.objects.items(), 
        #                        key=lambda obj: obj[1].layer)
        current_button = None
        current_button_key = None
        for key, obj in current_menu.objects.items():
            if is_button(obj) and obj.hitbox.is_pos_inside(*mouse_pos):
                current_button = obj
                current_button_key = key

        for event in events:
            #print(event)

            if (event.type == pygame.MOUSEMOTION and current_button is not None
                and current_button.is_selected
                and current_button.state != "click"):
                current_button.state = "click"
                current_button.render_flag = True

            elif (event.type == pygame.MOUSEMOTION and current_button is not None
                  and not current_button.is_selected 
                  and current_button.state != "hover"):
                current_button.state = "hover"
                current_button.render_flag = True

            elif (event.type == pygame.MOUSEBUTTONDOWN 
                  and current_button is not None and event.button == 1):
                current_button.state = "click"
                current_button.is_selected = True
                current_button.render_flag = True

            elif (event.type == pygame.MOUSEBUTTONUP 
                and current_button is not None and event.button == 1):
                current_button.state = "hover"
                current_button.is_selected = False
                current_button.render_flag = True
                if isinstance(current_button, Radiobutton):
                    self.update_radiobuttons(current_menu, current_button.group)
                current_button.exec_command()

            elif event.type == pygame.MOUSEWHEEL and current_menu.enable_scroll:
                current_menu.scroll_event(event.y * self.scroll_strength_multiplier)

            if (event.type == pygame.MOUSEMOTION 
                or (event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) 
                    and event.button == 1)):
                
                for key, obj in current_menu.objects.items():
                    if (is_button(obj) and key != current_button_key 
                        and event.type == pygame.MOUSEMOTION 
                        and obj.state != "none"):

                        obj.state = "none"
                        obj.render_flag = True

                    if (is_button(obj) and key != current_button_key 
                        and event.type == pygame.MOUSEBUTTONUP):
                        obj.is_selected = False

                for key, obj in current_menu.objects.items():
                    if not isinstance(obj, Slidebar):
                        continue

                    if (current_menu.scroll_slidebar == key 
                        and current_menu.enable_scroll 
                        and obj.state == "click"):

                        current_menu.set_scroll_by_progress(obj.progress)
                        obj.event(event, menu_pos, 0)

                    else:
                        obj.event(event, menu_pos, current_menu.scroll)

    def add_object(self, menu_id, object_id, _object):
        self.menues[menu_id].add_object(object_id, _object)

    def render_object(self, menu_id, object_id):
        self.menues[menu_id].render_object(object_id, self.ui_size)

    def add_menu(self, id, menu):
        self.menues[id] = menu

    def update_menu(self, id):
        self.menues[id].render_all(self.ui_size)

    def update_radiobuttons(self, current_menu, group):
        for obj in current_menu.objects.values():
            if isinstance(obj, Radiobutton) and obj.group == group:
                obj.is_checked = False
                obj.render_flag = True

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