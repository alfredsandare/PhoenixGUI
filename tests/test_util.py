from PhoenixGUI import util
import pygame
pygame.font.init()


def test_object_crop_fits():
    crop, pos = util.object_crop((200, 200), (0, 0), (300, 300), (0, 0), (1000, 1000))
    assert crop == [0, 0, 200, 200]

def test_object_crop_overflow_from_menu_size_right():
    crop, pos = util.object_crop((200, 200), (0, 0), (90, 300), (0, 0), (1000, 1000))
    assert crop == [0, 0, 90, 200]

def test_object_crop_overflow_from_menu_size_top():
    crop, pos = util.object_crop((200, 200), (0, -40), (300, 300), (0, 0), (1000, 1000))
    assert crop == [0, 40, 200, 200]
    assert pos == [0, 0]

def test_object_crop_overflow_from_menu_size_left():
    crop, pos = util.object_crop((200, 200), (-40, 0), (300, 300), (0, 0), (1000, 1000))
    assert crop == [40, 0, 200, 200]
    assert pos == [0, 0]

def test_object_crop_overflow_from_menu_size_down():
    crop, pos = util.object_crop((200, 200), (0, 0), (300, 80), (0, 0), (1000, 1000))
    assert crop == [0, 0, 200, 80]

def test_update_pos_by_anchor_nw():
    pos = util.update_pos_by_anchor((200, 200), (100, 100), 'nw')
    assert pos == (200, 200)
    
def test_update_pos_by_anchor_ne():
    pos = util.update_pos_by_anchor((200, 200), (100, 100), 'ne')
    assert pos == (100, 200)
    
def test_update_pos_by_anchor_sw():
    pos = util.update_pos_by_anchor((200, 200), (100, 100), 'sw')
    assert pos == (200, 100)
    
def test_update_pos_by_anchor_se():
    pos = util.update_pos_by_anchor((200, 200), (100, 100), 'se')
    assert pos == (100, 100)
    
def test_flatten_list():
    l = util.flatten_list([[1, 2], [3, 4]])
    assert l == [1, 2, 3, 4]

def test_flatten_list_mixed():
    l = util.flatten_list([1, 2, [3, 4]])
    assert l == [1, 2, 3, 4]
