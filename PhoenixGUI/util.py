import pygame

VALID_ANCHORS = ["nw", "n", "ne", "w", "c", "e", "sw", "s", "se"]

def get_font(path, font, size):
    if type(size) is not int:
        raise SyntaxError(f"Font size needs to be int, not {type(size)}")
    try:
        return pygame.font.Font(path+font+".ttf", size)
    except:
        return pygame.font.SysFont(font, size)


def object_crop(obj_size, obj_pos, menu_size, menu_pos, object_max_size):
    ''' crops the object if it is partly outside the menu borders '''
    crop = [0, 0, obj_size[0], obj_size[1]] #left, top, right, down

    if obj_pos[0] < menu_pos[0]:
        crop[0] = menu_pos[0] - obj_pos[0]

    if obj_pos[1] < menu_pos[1]:
        crop[1] = menu_pos[1] - obj_pos[1]

    if obj_pos[0] + obj_size[0] > menu_pos[0] + menu_size[0]:
        crop[2] = obj_size[0] - ((obj_pos[0] + obj_size[0]) - (menu_pos[0] + menu_size[0]))

    if obj_pos[1] + obj_size[1] > menu_pos[1] + menu_size[1]:
        crop[3] = obj_size[1] - ((obj_pos[1] + obj_size[1]) - (menu_pos[1] + menu_size[1]))

    if object_max_size != None and crop[2] > object_max_size[0]:
        crop[2] = object_max_size[0]

    if object_max_size != None and crop[3] > object_max_size[1]:
        crop[3] = object_max_size[1]

    pos_change = [crop[0], crop[1]]
    pos = sum_two_vectors(obj_pos, pos_change)

    return crop, pos

def update_pos_by_anchor(object_pos, object_size, anchor):
    object_pos = list(object_pos)
    if anchor not in VALID_ANCHORS:
        raise Exception(f"{anchor} is not a valid anchor. See docs for valid anchors.")

    if anchor in ["n", "c", "s"]:
        object_pos[0] -= round(object_size[0]/2)
    elif "e" in anchor:
        object_pos[0] -= object_size[0]

    if anchor in ["w", "c", "e"]:
        object_pos[1] -= round(object_size[1]/2)
    elif "s" in anchor:
        object_pos[1] -= object_size[1]

    return tuple(object_pos)

def flatten_list(mixed_list):
    out = []
    for i in mixed_list:
        if type(i) is list or type(i) is tuple:
            for j in i:
                out.append(j)
        else:
            out.append(i)
    return out

def is_button(obj, include_slidebars=True):
    from .button import Button
    from .checkbutton import Checkbutton
    from .radiobutton import Radiobutton
    from .slidebar import Slidebar
    from .dropdown import Dropdown
    return any([
        isinstance(obj, Button),
        isinstance(obj, Checkbutton),
        isinstance(obj, Radiobutton),
        isinstance(obj, Slidebar) if include_slidebars else False,
        isinstance(obj, Dropdown)
    ])

def compare_objects(a, b):
    for attr1, attr2 in zip(vars(a).values(), vars(b).values()):
        if not attr1 == attr2:
            return False
    return True

def get_value_from_state(state, standard, hover, click):
    if state == "hover" and hover != None:
        return hover
    elif state == "click" and click != None:
        return click
    return standard

def sum_two_vectors(v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1]]

def sum_multiple_vectors(*vectors):
    return [sum(i) for i in zip(*vectors)]

def snake_case_to_pascal_case(snake_case):
    return ''.join(word.capitalize() for word in snake_case.split('_'))
