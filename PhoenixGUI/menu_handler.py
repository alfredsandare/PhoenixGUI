import copy
import pygame
import importlib

from .text_input import TextInput
from .menu import Menu
from .util import is_button, snake_case_to_pascal_case, sum_multiple_vectors
from .radiobutton import Radiobutton
from .slidebar import Slidebar
from .dropdown import Dropdown
from .text import Text

HOVER_MENU_ID = "_hover_menu"
HOVER_MENU_TEXT_OBJ_ID = "text"
HOVER_MENU_MAX_HEIGHT = 2000


class MenuHandler:
    def __init__(self,
                 ui_size=1,
                 hover_menu_bg_color=None,
                 hover_menu_outline_color=None,
                 hover_menu_outline_width=1,
                 hover_menu_text_color=None,
                 hover_menu_width=200,
                 hover_menu_text_font=None,
                 hover_menu_text_size=None,
                 hover_menu_text_offset=None):

        self.ui_size = ui_size
        self.menues: dict[str, Menu] = {}
        self.prev_menu_key = None
        self.prev_button_key = None
        self.scroll_strength_multiplier = 1
        self.selected_slidebar = None
        self.selected_slidebar_menu = None
        self.font_path = None
        self.selected_text_input: TextInput = None

        # keys are pygame.key keys. first float is time since pressed
        # and second float is time since last text addition.
        self.pressed_buttons: dict[int, list[float, float]] = {}

        menu = Menu((0, 0),
                    (hover_menu_width, HOVER_MENU_MAX_HEIGHT),
                    bg_color=hover_menu_bg_color,
                    outline_color=hover_menu_outline_color,
                    outline_width=hover_menu_outline_width)

        text_pos = [0, 0]
        if hover_menu_text_offset is not None:
            text_pos = hover_menu_text_offset

        max_size = None
        if hover_menu_text_offset is not None:
            max_size=[hover_menu_width-2*hover_menu_text_offset[0],
                      HOVER_MENU_MAX_HEIGHT]

        text_object = Text(text_pos, "", hover_menu_text_font, hover_menu_text_size,
                           wrap_lines=True, color=hover_menu_text_color,
                           max_size=max_size)
        menu.add_object(HOVER_MENU_TEXT_OBJ_ID, text_object)
        self.menues[HOVER_MENU_ID] = menu

    def update(self, events, screen, time_passed):
        mouse_pos = pygame.mouse.get_pos()
        current_menu_key = self._get_current_menu_key(mouse_pos)

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
                self._update_text_inputs_from_mousebuttondown(current_menu,
                                                              mouse_pos)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._mousebuttonup_event(current_button, current_menu)

            elif event.type == pygame.MOUSEMOTION:
                self._mousemotion_event(event, current_menu, current_button, mouse_pos)

            elif current_menu is not None and event.type == pygame.MOUSEWHEEL \
                and current_menu.enable_scroll:
                current_menu.scroll_event(event.y * self.scroll_strength_multiplier)

            elif event.type == pygame.TEXTINPUT \
                and self.selected_text_input is not None:
                self.selected_text_input.add_text(event.text)

            elif event.type == pygame.KEYDOWN \
                and self.selected_text_input is not None:
                self._keydown_event(event)
        
        self._update_button_states(current_button, current_button_key, 
                                   prev_button, prev_button_key)
        
        self._check_key_states(time_passed)

        self.prev_menu_key = current_menu_key
        self.prev_button_key = current_button_key

        self._render_and_draw_menues(screen)

    def _check_key_states(self, time_passed):
        # this is only used for TextInput objects.
        if self.selected_text_input is None:
            return

        # an action is one of the following: stepping left or right, 
        # inserting text or removing text.
        TIME_REQUIRED_FOR_ACTION = 400
        TIME_BETWEEN_ACTION = 40

        key_state = pygame.key.get_pressed()
        INTERESTING_BUTTONS = [
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_BACKSPACE
        ]

        for button in INTERESTING_BUTTONS:
            if key_state[button] and button not in self.pressed_buttons:
                self.pressed_buttons[button] = [0, 0]

            elif not key_state[button] and button in self.pressed_buttons:
                del self.pressed_buttons[button]

            elif key_state[button]:
                self.pressed_buttons[button][0] += time_passed

        for button, (time_since_pressed, time_since_last_text_addition) \
            in self.pressed_buttons.items():
            if (time_since_pressed >= TIME_REQUIRED_FOR_ACTION 
                and time_since_last_text_addition >= TIME_BETWEEN_ACTION):
                # this is the case when the user holds down a key
                # and actions are performed rapidly.

                if button == pygame.K_LEFT:
                    self.selected_text_input.step("left")
                elif button == pygame.K_RIGHT:
                    self.selected_text_input.step("right")
                elif button == pygame.K_BACKSPACE:
                    self.selected_text_input.remove_text()

                self.pressed_buttons[button][1] -= TIME_BETWEEN_ACTION
                self.pressed_buttons[button][1] += time_passed

            elif time_since_pressed >= TIME_REQUIRED_FOR_ACTION:
                # this is the case when the user just pressed a down a key
                # and actions have not yet started to be performed rapidly.
                self.pressed_buttons[button][1] += time_passed

    def _update_text_inputs_from_mousebuttondown(self, 
                                                 current_menu: Menu, 
                                                 mouse_pos):

        self.selected_text_input = None
        for menu in self.menues.values():
            menu.deselect_all_text_inputs()

        if current_menu is None:
            return

        for obj in current_menu.objects.values():
            if (isinstance(obj, TextInput)
                and obj.hitbox.is_pos_inside(*mouse_pos)):

                obj.is_selected = True
                obj.render_flag = True
                self.selected_text_input = obj
                return

    def _keydown_event(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.selected_text_input.remove_text()

        elif event.key == pygame.K_LEFT:
            self.selected_text_input.step("left")

        elif event.key == pygame.K_RIGHT:
            self.selected_text_input.step("right")

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

            if not isinstance(current_button, Slidebar) \
                and not isinstance(current_button, Dropdown):
                current_button.exec_command()

            if isinstance(current_button, Dropdown):
                current_button.handle_mousebuttonup(pygame.mouse.get_pos())

        self.deselect_all_buttons()
            
        if self.selected_slidebar is not None:
            self.selected_slidebar.state = "none"
            self.selected_slidebar.is_selected = False
            self.selected_slidebar.render_flag = True
            self.selected_slidebar = None
            self.selected_slidebar_menu = None

    def _mousemotion_event(self, event, current_menu, current_button, mouse_pos):
        if isinstance(current_button, Dropdown):
            current_button.handle_mousemotion(mouse_pos)

        if self.selected_slidebar is not None:
            self.selected_slidebar.act_on_motion(event)
            if self.selected_slidebar.is_scroll_slidebar:
                self.selected_slidebar_menu.set_scroll_by_progress(
                    self.selected_slidebar.progress)

        hovered_object = self._get_hovered_object(current_menu, mouse_pos)
        if hovered_object is not None and hovered_object.hover_text is not None:
            self.menues[HOVER_MENU_ID].activate()
            self._update_hover_menu(hovered_object.hover_text, mouse_pos)
        else:
            self.menues[HOVER_MENU_ID].deactivate()

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

    def add_object(self, menu_id, object_id, object_):
        self.menues[menu_id].add_object(object_id, object_)

    def delete_object(self, menu_id, object_id):
        self.menues[menu_id].delete_object(object_id)
        
    def delete_multiple_objects(self, menu_id: str, ids: list[str], ids_startswith: list[str]):
        # deletes all ids from the 'ids' parameter
        # and deletes all ids that starts with the ids from the 'ids_startswith' parameter

        for obj_key in copy.copy(list(self.menues[menu_id].objects.keys())):
            if obj_key in ids or \
                any([obj_key.startswith(id_) for id_ in ids_startswith]):

                self.delete_object(menu_id, obj_key)

    def add_menu(self, id_, menu):
        if id_ == HOVER_MENU_ID:
            raise Exception("Menu id may not be '_hover_menu'")
        self.menues[id_] = menu

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
                class_name = snake_case_to_pascal_case(obj["type"])
                class_ = getattr(module, class_name)

                image_keys = ["image", "hover_image", "click_image"]
                for image_key in image_keys:
                    if image_key in obj.keys():
                        obj[image_key] = images[obj[image_key]]

                del obj["type"]
                objs[obj_key] = class_(**obj)

            del menu["objects"]
            instatiated_menu = Menu(**menu)
            instatiated_menu.deactivate()

            for key, value in objs.items():
                instatiated_menu.add_object(key, value)

            self.add_menu(menu_key, instatiated_menu)

    def add_font_path(self, path: str):
        # adds an absolute path where the menu handler will search for fonts.
        self.font_path = path

    def deactivate_all_menues(self):
        for menu in self.menues.values():
            menu.deactivate()

    def _get_current_menu_key(self, mouse_pos):
        menues = {key: value for key, value in sorted(self.menues.items(),
                  key=lambda menu: menu[1].layer, reverse=True)
                  if key!=HOVER_MENU_ID}
        for key, menu in menues.items():
            if menu.hitbox.is_pos_inside(*mouse_pos) and menu.active:
                return key
        return None
    
    def _get_buttons_data(self, current_menu: Menu, mouse_pos):
        current_button = None
        current_button_key = None
        if current_menu != None:
            for key, obj in current_menu.get_items_sorted_by_layer().items():
                if is_button(obj) and obj.hitbox.is_pos_inside(*mouse_pos):
                    current_button = obj
                    current_button_key = key
                    break

        prev_button_key = self.prev_button_key
        prev_button = None
        if prev_button_key is not None and self.prev_menu_key is not None \
            and prev_button_key in self.menues[self.prev_menu_key].objects.keys():
            prev_button = self.menues[self.prev_menu_key].objects[prev_button_key]

        return current_button, current_button_key, prev_button, prev_button_key

    def _render_and_draw_menues(self, screen):
        menues = [menu for key, menu in self.menues.items() if key!=HOVER_MENU_ID]
        menues = sorted(menues, key=lambda menu: menu.layer)
        menues.append(self.menues[HOVER_MENU_ID])
        for menu in menues:
            if menu.active:
                menu.render_all(screen, self.ui_size, self.font_path)

    def is_mouse_inside_menu(self):
        return any([menu.hitbox.is_pos_inside(*pygame.mouse.get_pos()) \
                    and menu.active for menu in self.menues.values()])

    def _get_hovered_object(self, current_menu: Menu, mouse_pos):
        if current_menu == None:
            return None

        for key, obj in current_menu.objects.items():
            if obj.hitbox.is_pos_inside(*mouse_pos) \
                and key not in ["_bg", "_outline"]:
                return obj
        return None

    def _update_hover_menu(self, text, mouse_pos):
        hover_menu = self.menues[HOVER_MENU_ID]
        hover_menu.change_property("pos", mouse_pos)

        text_obj: Text = hover_menu.objects[HOVER_MENU_TEXT_OBJ_ID]
        if text_obj.text != text:
            text_obj.text = text
            text_obj.render_and_store(hover_menu.pos, (hover_menu.size[0], 2000),
                                      self.ui_size, 0, self.font_path)

            # Set the menu size to the size of the text
            text_size = text_obj.rendered_object.get_image_size()
            menu_size = sum_multiple_vectors(text_size, text_obj.pos, text_obj.pos)
            hover_menu.change_property("size", menu_size)
