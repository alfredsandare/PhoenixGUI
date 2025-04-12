from .menu_object import MenuObject
from .rendered_menu_object import RenderedMenuObject
import pygame
from .util import flatten_list, get_font

pygame.font.init()


class Zone:
    def __init__(self, end_point, color, y_level, origin):
        self.end_point = end_point
        self.color = color
        self.y_level = y_level
        self.origin = origin

    def get_all(self):
        # returns all property values in a tuple, except origin
        return tuple(vars(self).values())[:3]


class Text(MenuObject):
    def __init__(self, 
                 pos, 
                 text, 
                 font, 
                 font_size, 
                 max_size=None, 
                 wrap_lines=False, 
                 color=(255, 255, 255), 
                 bg_color=None, 
                 anchor="nw",
                 layer=0,
                 hover_text=None):
        
        super().__init__(pos, max_size, anchor, hover_text=hover_text,
                         layer=layer)
        self.text = text
        self.font = font
        self.font_size = font_size
        self.wrap_lines = wrap_lines
        self.color = color
        self.bg_color = bg_color

        if type(text) is not str:
            raise TypeError(f"Text must be str, not {type(text)}")

    def get_size(self, menu_pos, menu_size, ui_size, scroll):
        object = self.render(menu_pos, menu_size, ui_size, scroll)
        return object.image.get_size()
    
    def get_font_height(self, font_path):
        font = get_font(font_path if font_path is not None else "", 
                        self.font, 
                        self.font_size)
        return font.size('H')[1]

    def render(self, menu_pos, menu_size, ui_size, scroll, font_path=None):
        if self.text == "":
            empty_surface = pygame.Surface((1, 1), pygame.SRCALPHA)
            return RenderedMenuObject(empty_surface, (0, 0))
        
        font = get_font(font_path if font_path is not None else "", 
                        self.font, 
                        self.font_size * ui_size)
        
        font_height = font.size('H')[1]

        original_text, zone_borders, colors = \
            self.decode_text(self.text, self.color)

        # split the text into lines where the user hardcoded linebreaks.
        text_pieces = original_text.split('\n')

        words = flatten_list([piece.split() for piece in text_pieces])
        longest_word_length = max([font.size(word)[0] for word in words])

        text_pieces = self.divide_text_into_lines(text_pieces, font, menu_size,
                                                  longest_word_length)

        zone_borders = self.consider_removed_chars(text_pieces, 
                                                   zone_borders, 
                                                   original_text)

        zones = self.apply_text_colour_insertion(text_pieces, zone_borders,
                                                 colors, self.color)

        joined_text = ''.join(text for text in text_pieces)
        text_pieces = self.apply_zones(zones, joined_text)

        longest_line = self.get_longest_line(zones, text_pieces, font)
        total_height = font_height * (zones[-1].y_level + 1)
        surface_size = (longest_line, total_height)
        surface = pygame.Surface(surface_size, pygame.SRCALPHA)

        for i, text in enumerate(text_pieces):
            pos = self.get_text_piece_pos(
                zones, font_height, i, text_pieces, font, longest_line)
            rendered_text = font.render(
                text, True, zones[i].color, self.bg_color)
            surface.blit(rendered_text, pos)

        crop, pos = self._adjust_pos_and_crop(self.pos, surface_size, 
                                              menu_pos, menu_size, scroll)

        return RenderedMenuObject(surface, pos, crop)

    def get_longest_line(self, zones, text_pieces, font):
        line_lengths = [font.size(text_pieces[0])[0]]
        for i, text in enumerate(text_pieces[1:]):
            if zones[i+1].y_level != zones[i].y_level:  # new line
                line_lengths.append(font.size(text)[0])
            else:
                line_lengths[-1] += font.size(text)[0]
        return max(line_lengths)

    def apply_zones(self, zones, joined_text):
        # splits the text into pieces at the zone borders.
        text_pieces = []
        prev_zone_end = 0
        for zone in zones:
            text_pieces.append(joined_text[prev_zone_end:zone.end_point])
            prev_zone_end = zone.end_point
        return text_pieces

    def get_text_piece_pos(self, 
                           zones, 
                           font_height, 
                           current_piece_index, 
                           text_pieces, 
                           font, 
                           longest_line):
        x_pos = 0

        for i in range(current_piece_index):
            if zones[i].y_level == zones[current_piece_index].y_level:
                x_pos += font.size(text_pieces[i])[0]
        
        y_level = zones[current_piece_index].y_level
        this_line_length = 0
        for i, zone in enumerate(zones):
            if zone.y_level == y_level:
                this_line_length += font.size(text_pieces[i])[0]

        if self.anchor in ["n", "c", "s"]:
            x_pos += (longest_line - this_line_length) / 2

        elif self.anchor in ["ne", "e", "se"]:
            x_pos += longest_line - this_line_length

        y_pos = zones[current_piece_index].y_level*font_height
        return (x_pos, y_pos)
            
    def divide_text_into_lines(self, text_pieces, font, 
                               menu_size, longest_word_length):
        # splits the text pieces where they exceed the max width.

        processed_text_pieces = []
        for text in text_pieces:
            if (self.max_size != None 
                and self.max_size[0] < menu_size[0] - self.pos[0]):
                max_width = self.max_size[0]
            elif self.anchor in ["n", "c", "s"]:
                distance_to_borders = [self.pos[0], menu_size[0] - self.pos[0]]
                max_width = 2 * min(distance_to_borders)
            elif self.anchor in ["nw", "w", "sw"]:
                max_width = menu_size[0] - self.pos[0]
            else:
                max_width = self.pos[0]

            if max_width < longest_word_length:
                max_width = longest_word_length

            if self.wrap_lines:
                processed_text_pieces.extend(self.wrap_line(text, font, max_width))
            else:
                processed_text_pieces.append(self.cut_line(text, font, max_width))

        return processed_text_pieces

    def decode_text(self, text: str, default_color):

        # decodes the text and returns the decoded text, zone borders and colors.
        # Remember: A color zone is formatted like this: %%255 255 255%text%.
        # First comes two % signs, then the color in RGB format, then % again,
        # then the text, then a conclusive %.

        # The algorithm iterates over every character in the text.
        # If two percent signs are found, a new zone is created.
        # The zone color and text is extracted and are added to decoded_text, zone_borders and colors.
        # Then all the chars' indexes from the first two % to the last % are added to to_skip,
        # so that the loop skips them when iterating over the text.
        # Between color zones, new zones are created with the default color. These are referred to as "no zones".

        decoded_text = ''  # the extracted text

        # a list of ints, where every int represents the end of a "zone". 
        # Example: the string "HelloThere" where both words are different colors
        # makes the zones variable: [5, 10].
        zone_borders = []

        colors = []  # a list of color tuples

        # the position of chars that are part of a zone, 
        # they are to be skipped while searching for zones.
        to_skip = []

        # the total number of chars that are not part of the actual text
        chars_to_be_ignored = 0

        # total amount of preventative backslashes
        amount_of_backslashes = 0

        for i, char in enumerate(text):
            if (char == '%' and i+1<len(text) 
                and text[i+1] == '%' 
                and i not in to_skip):  # found a zone

                # end previous nozone
                if i > 0 and i-1 not in to_skip:
                    zone_borders.append(len(decoded_text)-amount_of_backslashes)
                    colors.append(default_color)

                # color_text is the text that holds the RGB value.
                color_text_length = text.find('%', i+2)-i-1
                color_text = text[i+2:i+color_text_length+1]
                zone_color = tuple(int(color) for color in color_text.split())
                colors.append(zone_color)

                # zone_text is the actual text in the zone.
                zone_text_length = 1
                try:
                    while not (text[i+color_text_length+zone_text_length+1] == '%'
                               and text[i+color_text_length+zone_text_length] != "\\"):
                        zone_text_length += 1
                except IndexError:
                    raise Exception("Can't find closing % in text color insertion "\
                                    f"at this text: {self.text}")

                amount_of_backslashes += \
                    text[i:i+color_text_length+zone_text_length+1].count("\\%")
                zone_borders.append(i+zone_text_length-1-chars_to_be_ignored \
                                    -amount_of_backslashes)
                decoded_text += text[i+color_text_length+2: \
                                     i+color_text_length+zone_text_length+1]
                to_skip.extend(range(i, i+color_text_length+zone_text_length+2))
                chars_to_be_ignored += color_text_length+3

            elif i not in to_skip:  # no zone
                decoded_text += char

        # end last nozone
        if len(zone_borders) == 0 or \
            len(decoded_text)-amount_of_backslashes > zone_borders[-1]:
            zone_borders.append(len(decoded_text)-amount_of_backslashes)
            colors.append(default_color)

        # purge decoded_text of preventative backslashes
        decoded_text = "".join([c if c != "\\" 
                                or (c == "\\" and decoded_text[i+1] != "%")
                                else "" 
                                for i, c in enumerate(decoded_text)])

        return decoded_text, zone_borders, colors

    def consider_removed_chars(self, lines, zone_borders, original_text):
        # when the lines are wrapped up spaces are stripped away from the lines.
        # this function changes the zones' values according to the removed characters.
        joined_lines = ''.join(line for line in lines)

        removed_chars = []
        for i, c in enumerate(original_text):
            if c != joined_lines[i-len(removed_chars)]:
                removed_chars.append(i)

        for i, border in enumerate(zone_borders):
            for char_index in removed_chars:
                if char_index >= border:
                    break
                zone_borders[i] -= 1

        return zone_borders

    def apply_text_colour_insertion(self, lines, zone_borders, 
                                    colors, default_color) -> list[Zone]:
        zones = []
        for i, line in enumerate(lines):
            length = len(line) + (0 if i==0 else zones[-1].end_point)
            zones.append(Zone(length, default_color, i, 'line_split'))

        for border, color in zip(zone_borders, colors):
            for i, zone in enumerate(zones):
                if zone.end_point >= border:
                    zones.insert(i, Zone(border, color, zone.y_level, 'zone'))
                    break
            
            # When adding a new zone, colour of previous 
            # zones from line zones' colors need to be changed
            zone_type = 'zone' if i==0 else zones[i-1].origin
            j=0
            while zone_type == 'line_split':
                zones[i-j-1].color = zones[i].color
                zone_type = zones[i-j-2].origin
                j+=1

        # remove duplicates
        zones_copy = zones.copy()
        deleted = 0
        for i, zone in enumerate(zones_copy):
            prev_zone_end_point = 0 if i==0 else zones_copy[i-1].end_point
            if zone.end_point == prev_zone_end_point:
                del zones[i-deleted]
                deleted += 1

        return zones

    def get_words(self, text):
        """ Splits given at single spaces without keeping the single spaces
        but keeps all spaces that occur in groups """

        words = []
        prev_split = 0
        for i, char in enumerate(text):
            prev_char = None if i==0 else text[i-1]
            next_char = None if i==len(text)-1 else text[i+1]
            if prev_char != " " and char == " " and next_char != " ":
                words.append(text[prev_split:i])
                prev_split = i+1
            elif i==len(text)-1:
                words.append(text[prev_split:i+1])

        words = [word for word in words if word]

        # Now words can contain multiple spaces.
        # We want to transform all words like: "H  G" -> "H", "  G"
        words_split = []
        for word in words:
            prev_split = 0
            for i, c in enumerate(word):
                prev_char = None if i==0 else word[i-1]
                if c == " " and prev_char != " ":
                    words_split.append(word[prev_split:i])
                    prev_split = i
                elif i==len(word)-1:
                    words_split.append(word[prev_split:i+1])

        return [word for word in words_split if word]

    def wrap_line(self, text, font: pygame.font.Font, max_width):
        if any(font.size(c)[0] > max_width for c in text):
            # If any of the chars don't fit in a line by itself, just give up
            raise ValueError(f"Max width ({max_width}) is too "
                             f"small for a char to fit in")

        words = self.get_words(text)
        lines = [""]
        for word in words:
            if font.size(word)[0] > max_width:
                lines = self.split_word(word, font, max_width, lines)
                continue

            if font.size(lines[-1]+word)[0] < max_width:
                lines[-1] += word + " "
            else:
                lines[-1] = lines[-1][:-1]
                lines.append(word + " ")

        lines[-1] = lines[-1][:-1]
        return lines

    def split_word(self, word, font: pygame.font.Font, max_width, lines: list):
        """ Splits a word so that it fits within max_width"""

        prev_split = 0
        for i in range(len(word)):
            if font.size(lines[-1] + word[prev_split:i])[0] > max_width:
                lines[-1] += word[prev_split:i-1]
                lines.append("")
                prev_split = i-1
            elif i==len(word)-1:
                lines[-1] += word[prev_split:i+1]

        lines[-1] += " "
        return lines

    def cut_line(self, text, font, max_width):
        '''Returns shorted version of given text so that it fits within the max_width'''
        cut_text = ""
        i=0
        while True:
            if i == 0:
                cut_text = text
            else:
                cut_text = text[:-i]+".."
            text_size = font.size(cut_text)[0]
            if text_size <= max_width or cut_text == "":
                return cut_text
            i+=1
