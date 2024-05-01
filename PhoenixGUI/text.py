from .menu_object import MenuObject
from .rendered_menu_object import RenderedMenuObject
import pygame
from .util import flatten_list, get_font, cut_line, update_pos_by_anchor, wrap_line, object_crop

pygame.font.init()

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
                 anchor="nw"):
        
        super().__init__(pos, max_size, anchor)
        self.text = text
        self.font = font
        self.font_size = font_size
        self.wrap_lines = wrap_lines
        self.color = color
        self.bg_color = bg_color
        self.font_path = None

    def get_size(self, menu_pos, menu_size, ui_size, scroll):
        objects = self.render(menu_pos, menu_size, ui_size, scroll)
        return objects[0].image.get_size()
    
    def get_font_height(self):
        font = get_font(self.font_path if self.font_path is not None else "", 
                        self.font, 
                        self.font_size)
        return font.size('H')[1]


    def render(self, menu_pos, menu_size, ui_size, scroll):
        font = get_font(self.font_path if self.font_path is not None else "", 
                        self.font, 
                        self.font_size * ui_size)
        
        font_height = font.size('H')[1]

        original_text, zone_borders, colors = self.decode_text(self.text, 
                                                               self.color)
        text_pieces = original_text.split('\n')

        words = flatten_list([piece.split() for piece in text_pieces])
        longest_word_length = max([font.size(word)[0] for word in words])

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
                processed_text_pieces.extend(wrap_line(text, font, max_width))
            else:
                processed_text_pieces.append(cut_line(text, font, max_width))

        zone_borders = self.consider_removed_chars(processed_text_pieces, 
                                                   zone_borders, 
                                                   original_text)
        zones = self.apply_text_colour_insertion(processed_text_pieces, 
                                                 zone_borders, colors, 
                                                 self.color)

        #make lines out of the zones
        joined_lines = ''.join(line for line in processed_text_pieces)
        final_text_pieces = []
        prev_zone_end = 0
        for zone in zones:
            final_text_pieces.append(joined_lines[prev_zone_end:zone.end_point])
            prev_zone_end = zone.end_point

        line_lengths = [font.size(final_text_pieces[0])[0]]
        for i, text in enumerate(final_text_pieces[1:]):
            if zones[i+1].y_level != zones[i].y_level:  # new line
                line_lengths.append(font.size(text)[0])
            else:
                line_lengths[-1] += font.size(text)[0]
        
        longest_line = max(line_lengths)
        total_height = font_height * (zones[-1].y_level + 1)

        surface_size = (longest_line, total_height)
        surface = pygame.Surface(surface_size, pygame.SRCALPHA)
        for i, text in enumerate(final_text_pieces):
            pos = self.get_text_piece_pos(zones, 
                                          font_height, 
                                          i, 
                                          final_text_pieces, 
                                          font, 
                                          longest_line)
            rendered_text = font.render(text, 
                                        True, 
                                        zones[i].color, 
                                        self.bg_color)
            surface.blit(rendered_text, pos)

        pos = [self.pos[0] + menu_pos[0], self.pos[1] + menu_pos[1] + scroll]

        pos = update_pos_by_anchor(pos, surface_size, self.anchor)
        crop, pos_change = object_crop(surface_size, 
                                       pos, 
                                       menu_size, 
                                       menu_pos, 
                                       self.max_size)
        pos = (pos[0]+pos_change[0], pos[1]+pos_change[1])

        return [RenderedMenuObject(surface, pos, crop)]
    
    def get_text_piece_pos(self, 
                           zones, 
                           font_height, 
                           current_piece_index, 
                           final_text_pieces, 
                           font, 
                           longest_line):
        x_pos = 0

        for i in range(current_piece_index):
            if zones[i].y_level == zones[current_piece_index].y_level:
                x_pos += font.size(final_text_pieces[i])[0]
        
        y_level = zones[current_piece_index].y_level
        this_line_length = 0
        for i, zone in enumerate(zones):
            if zone.y_level == y_level:
                this_line_length += font.size(final_text_pieces[i])[0]

        if self.anchor in ["n", "c", "s"]:
            x_pos += (longest_line - this_line_length) / 2

        elif self.anchor in ["ne", "e", "se"]:
            x_pos += longest_line - this_line_length

        y_pos = zones[current_piece_index].y_level*font_height
        return (x_pos, y_pos)
            


    def decode_text(self, text, default_color):
        decoded_text = ''  # the extracted text
        ''' a list of ints, where every int represents the end of a "zone". 
        Example: the string "HelloThere" where both words are different colors
        makes the zones variable: [5, 10].'''
        zone_borders = []
        colours = []  # a list of color tuples
        '''the position of chars that are part of a zone, 
        they are to be skipped while searching for zones.'''
        to_skip = []
        # the total number of chars that are not part of the actual text
        chars_to_be_ignored = 0
        for i, char in enumerate(text):
            if (char == '%' and i+1<len(text) 
                and text[i+1] == '%' 
                and i not in to_skip):  # found a zone
                # end previous nozone
                if i > 0 and i-1 not in to_skip:
                    zone_borders.append(len(decoded_text))
                    colours.append(default_color)

                # get the colour
                j=1
                while text[i+j+1] != '%':
                    j+=1
                offset = j # save the offset of the actual text in this zone
                color_text = text[i+2:i+offset+1]
                zone_color = tuple(int(color_text.split()[j]) for j in range(3))

                # get the text
                j=1
                while not (text[i+offset+j+1] == '%' 
                           and text[i+offset+j] != "\\"):
                    j+=1
                zone_borders.append(i+j-1-chars_to_be_ignored)
                colours.append(zone_color)
                decoded_text += text[i+2+offset:i+offset+j+1]
                for k in range(i, i+offset+j+2):
                    to_skip.append(k)
                chars_to_be_ignored += offset+3

            elif i not in to_skip:  # no zone
                decoded_text += char

        if len(zone_borders) == 0 or len(decoded_text) > zone_borders[-1]:
            zone_borders.append(len(decoded_text))
            colours.append(default_color)

        # purge decoded_text of preventative backslashes
        decoded_text = "".join([c if c != "\\" 
                                or (c == "\\" and decoded_text[i+1] != "%")
                                else "" 
                                for i, c in enumerate(decoded_text)])

        return decoded_text, zone_borders, colours

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

    def apply_text_colour_insertion(self, lines, zone_borders, colours, default_color):
        zones = []
        for i, line in enumerate(lines):
            length = len(line) + (0 if i==0 else zones[-1].end_point)
            zones.append(Zone(length, default_color, i, 'line_split'))

        for border, color in zip(zone_borders, colours):
            for i, zone in enumerate(zones):
                if zone.end_point >= border:
                    zones.insert(i, Zone(border, color, zone.y_level, 'zone'))
                    break
            
            # When adding a new zone, colour of previous 
            # zones from line zones' colours need to be changed
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
            prev_zone_pos = 0
            if i > 0:
                prev_zone_pos = zones_copy[i-1].end_point
            if zone.end_point == prev_zone_pos:
                del zones[i-deleted]
                deleted += 1

        return zones

class Zone:
    def __init__(self, end_point, color, y_level, origin):
        self.end_point = end_point
        self.color = color
        self.y_level = y_level
        self.origin = origin

    def get_all(self):
        # returns all property values in a tuple, except origin
        return tuple(vars(self).values())[:3]