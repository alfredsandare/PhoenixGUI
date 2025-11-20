from .selectionbutton import SelectionButton


class Checkbutton(SelectionButton):
    def __init__(self,
                 pos,
                 text,
                 font,
                 font_size,
                 max_size=None,
                 anchor="nw",

                 text_color=(255, 255, 255),
                 text_hover_color=None,
                 text_click_color=None,
                 square_color=(255, 255, 255),
                 square_hover_color=None,
                 square_click_color=None,
                 square_size=1,
                 image=None,
                 hover_image=None,
                 click_image=None,

                 text_offset=10,

                 hitbox_padding=0,
                 command=None,
                 layer=0,
                 hover_text=None):

        super().__init__("rect",
                         pos,
                         text,
                         font,
                         font_size,
                         max_size=max_size,
                         anchor=anchor,

                         text_color = text_color,
                         text_hover_color = text_hover_color,
                         text_click_color = text_click_color,
                         shape_color = square_color,
                         shape_hover_color = square_hover_color,
                         shape_click_color = square_click_color,
                         shape_size = square_size,
                         image = image,
                         hover_image = hover_image,
                         click_image = click_image,

                         text_offset=text_offset,

                         hitbox_padding = hitbox_padding,
                         command = command,
                         layer = layer,
                         hover_text = hover_text)
