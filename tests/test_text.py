from PhoenixGUI import text
import pygame
import unittest

pygame.font.init()
#font = pygame.font.SysFont("arial", 20)
a_text = text.Text((0, 0), "t", "arial", 20)

DEFAULT_COLOR = (255, 255, 255)

def test_text_general():
    t = text.Text((0, 0), "hello", "arial", 20)
    assert t.text == "hello"
    assert t.pos == (0, 0)

def test_decode_text_none():
    _text = "Hello There"
    decoded_dext, zones, colors = a_text.decode_text(_text, (255, 255, 255))
    assert decoded_dext == "Hello There"
    assert zones == [11]
    assert colors == [(255, 255, 255)]

def test_decode_text_empty():
    _text = ""
    decoded_dext, zones, colors = a_text.decode_text(_text, DEFAULT_COLOR)
    assert decoded_dext == ""
    assert zones == [0]
    assert colors == [DEFAULT_COLOR]

def test_decode_text_zone():
    _text = "Hello %%100 100 0%There% General"
    decoded_text, zones, colors = a_text.decode_text(_text, DEFAULT_COLOR)
    assert decoded_text == "Hello There General"
    assert zones == [6, 11, 19]
    assert colors == [DEFAULT_COLOR, (100, 100, 0), DEFAULT_COLOR]

def test_decode_text_two_zones():
    _text = "%%255 0 0%Hello% %%0 255 0%There%"
    decoded_dext, zones, colors = a_text.decode_text(_text, DEFAULT_COLOR)
    assert decoded_dext == "Hello There"
    assert zones == [5, 6, 11]
    assert colors == [(255, 0, 0), DEFAULT_COLOR, (0, 255, 0)]

def test_decode_text_adjacent_zones():
    _text = "%%255 0 0%Hello%%%0 255 0%There%"
    decoded_dext, zones, colors = a_text.decode_text(_text, DEFAULT_COLOR)
    assert decoded_dext == "HelloThere"
    assert zones == [5, 10]
    assert colors == [(255, 0, 0), (0, 255, 0)]

def test_decode_text_backslash():
    _text = "%%255 0 0%N\\%N%"
    decoded_dext, zones, colors = a_text.decode_text(_text, DEFAULT_COLOR)
    assert decoded_dext == "N%N"

def test_consider_removed_chars_no_change():
    lines = ["Hello There"]
    zones = [6, 11]
    original_text = "Hello There"
    zones = a_text.consider_removed_chars(lines, zones, original_text)
    assert zones == [6, 11]

def test_consider_removed_chars():
    lines = ["Hello", "There", "General", "Kenobi"]
    zones = [6, 12, 20, 26]
    original_text = "Hello There General Kenobi"
    zones = a_text.consider_removed_chars(lines, zones, original_text)
    assert zones == [5, 10, 17, 23]

def test_apply_text_color_insertion_empty():
    lines = []
    zones = []
    colors = []
    zones = a_text.apply_text_colour_insertion(lines, zones, colors, DEFAULT_COLOR)
    assert zones == []

def test_apply_text_color_insertion_one_line():
    lines = ["hellothere hellothere"]
    zones = [21]
    colors = [DEFAULT_COLOR, DEFAULT_COLOR]
    zones = a_text.apply_text_colour_insertion(lines, zones, colors, DEFAULT_COLOR)
    expected = [(21, DEFAULT_COLOR, 0)]
    for e, zone in zip(expected, zones):
        assert zone.get_all() == e

def test_apply_text_color_insertion_two_lines():
    lines = ["hellothere", "hellothere"]
    zones = [10, 20]
    colors = [DEFAULT_COLOR, DEFAULT_COLOR]
    zones = a_text.apply_text_colour_insertion(lines, zones, colors, DEFAULT_COLOR)
    expected = [(10, DEFAULT_COLOR, 0), (20, DEFAULT_COLOR, 1)]
    for e, zone in zip(expected, zones):
        assert zone.get_all() == e

def test_apply_text_color_insertion_multiple_colors_on_same_line():
    lines = ["hellothere hellothere"]
    zones = [11, 21]
    colors = [DEFAULT_COLOR, DEFAULT_COLOR]
    zones = a_text.apply_text_colour_insertion(lines, zones, colors, DEFAULT_COLOR)
    expected = [(11, DEFAULT_COLOR, 0), (21, DEFAULT_COLOR, 0)]
    for e, zone in zip(expected, zones):
        assert zone.get_all() == e

def test_apply_text_color_insertion_multi_colors_multi_lines():
    lines = ["hellothere", "hellothere"]
    zones = [5, 10, 15, 20]
    colors = [(0, 0, 0), (100, 0, 0), (0, 100, 0), (100, 100, 0)]
    zones = a_text.apply_text_colour_insertion(lines, zones, colors, DEFAULT_COLOR)
    expected = [
        (5, (0, 0, 0), 0),
        (10, (100, 0, 0), 0),
        (15, (0, 100, 0), 1),
        (20, (100, 100, 0), 1)
    ]
    for e, zone in zip(expected, zones):
        assert zone.get_all() == e

def test_get_words_1():
    assert a_text.get_words("Hello") == ["Hello"]
    
def test_get_words_single_space():
    assert a_text.get_words("Hello There General Kenobi") == ["Hello", "There", "General", "Kenobi"]

def test_get_words_double_space():
    assert a_text.get_words("Hello  There") == ["Hello  There"]

def test_get_words_mixed():
    assert a_text.get_words("Hello There  General Kenobi") == ["Hello", "There  General", "Kenobi"]
    
def test_get_words_mixed_edge1():
    assert a_text.get_words("Hello There  General Kenobi  ") == ["Hello", "There  General", "Kenobi  "]
    
def test_get_words_mixed_edge2():
    assert a_text.get_words("  Hello There  General Kenobi") == ["  Hello", "There  General", "Kenobi"]
    
def test_get_words_mixed_edge3():
    assert a_text.get_words(" Hello There  General Kenobi  ") == ["Hello", "There  General", "Kenobi  "]
    
def test_get_words_mixed_edge4():
    assert a_text.get_words("  Hello There  General Kenobi ") == ["  Hello", "There  General", "Kenobi"]