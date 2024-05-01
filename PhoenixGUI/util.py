import pygame

VALID_ANCHORS = ["nw", "n", "ne", "w", "c", "e", "sw", "s", "se"]

def get_font(path, font, size):
    if type(size) is not int:
        raise SyntaxError(f"Font size needs to be int, not {type(size)}")
    try:
        return pygame.font.Font(path+font+".ttf", size)
    except:
        return pygame.font.SysFont(font, size)

def trunc_line(text, font, max_width):
    '''Internal function for WrapLine'''
    real = len(text)
    stext=text
    l=font.size(text)[0]
    cut=0
    a=0
    done=1
    old=None
    while l > max_width:
        a+=1
        n = text.rsplit(None, a)[0]
        if stext == n:
            cut+=1
            stext = n[:-cut]
        else:
            stext = n
        l=font.size(stext)[0]
        real = len(stext)
        done = 0
    return real, done, stext


def wrap_line(text, font, max_width):
    '''Returns given text in a list of strings divided so that no line exceeds the maxWidth'''
    '''text is text, font is the pygame font and maxWidth is the maximum width in pixels'''
    done = 0
    wrapped = []
    while not done:
        nl, done, stext = trunc_line(text, font, max_width)
        wrapped.append(stext.strip())
        text=text[nl:]
    return wrapped


def cut_line(text, font, max_width):
    '''Returns shorted version of given text so that it fits within the maxWidth'''
    done = False
    i=0
    while not done:
        if i == 0: #för att str[:0] returnar ''
            cut_text = text
        else:
            cut_text = text[:-i]+'..'
        text_size = font.size(cut_text)[0]
        if text_size <= max_width or cut_text == '': #sluta när den passar eller om den inte passar alls
            done = True
        i+=1

    return cut_text

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

    return crop, pos_change

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

def is_button(obj):
    from .button import Button
    from .checkbutton import Checkbutton
    from .radiobutton import Radiobutton
    return any([
        isinstance(obj, Button),
        isinstance(obj, Checkbutton),
        isinstance(obj, Radiobutton)
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