# Documentation

## Class MenuHandler

class MenuHandler(frame_size, ui_size)

frame_size: tuple, (x, y). The size of the screen in pixels.
ui_size: int. Multiplicative factor of the ui's size.

### Methods

#### load_data_from_dict(data, images)

Parameters:  
data: dict. A dict with data. See below for formatting specifications.  
images: dict. A dict with identifier keys and pygame.surface values.

The data dict should be formatted as such:  
```
data = {
    "my_menu": {
        "pos": (0, 0),
        "size": (200, 200),
        "objects": {
            "my_shape": {
                "type": "shape",
                "pos": (0, 0),
                "size": (40, 40),
                "color": (255, 0, 0),
                "type_": "rect"
            },
            "my_image": {
                "type": "image",
                "pos": (50, 50),
                "image": "my_image"
            }
        }
    }
}
```
'my_menu' will be assigned as the id of that menu. Each menu has a 'objects' key that holds all the menu objects. Again, the key of the object will be assigned as the id of that object. Inside the objects all properties are assigned, but also a 'type' is used to specify what type of object it is.

## Class MenuObject

The superclass for all menu objects.

Properties:
Each property has a getter and setter, see subtitle "methods" further down.

pos: The position (in pixels) of the object relative to the menu's position.
max_size: Used to set a maximum size of the object. The object will automatically never exceed the menu borders. E.g. if you have a text object with alternating text based on the state of the game/application, you define a maximum size for the text.

anchor: Which part of the object that will be anchored to the position coordinates. Valid anchors are: "nw", "n", "ne", "w", "c", "e", "sw", "s", "se".

### Methods

set_layer(layer)

Parameters:
layer: int.


## Class Text
Used for placing text in menues.

class Text(pos, text, font, font_size)

pos: tuple, (x, y). The position of the text in pixels, relative to the menu.
text: string. The text which will be displayed.
font: string. The name of the font. If font is not found in SysFont, it will be searched for in the root of your project.
font_size: int. The size of the font.

Keyword arguments (optional arguments):
max_size: tuple, (width, height). The max size of the object in pixels. By default there is no max size.
wrap_lines: bool. If true and the text is longer the the object's width the lines will be wrapped.
color: tuple, (R, G, B) or (R, G, B, A). The color of the text.
bg_color: tuple, (R, G, B) or (R, G, B, A). The text's background color. Is transparent by default.

### Text color insertion
Text color insertion enables you to create text with different colors in it. The class' property 'color' will be used as a default value. To make a part of a text be a different color, put two percent signs followed by the RGB code, followed by another percent sign, then the text actual text and last a conclusive percent sign. It should be formatted like this: 'foo %%255 0 0%bar%'. That library will render 'foo ' in the default color, and render 'bar' in red. If you want to include a percent sign in the text that's inside a "color zone", simply put a backslash ('\\') before it.

## Class Image
Used for placing images in menues.

class Image(pos, image)

pos: tuple, (x, y). The position of the text in pixels, relative to the menu.
image: pygame.image. The image to be shown. Created with pygame.image.load().

Keyword arguments (optional):
max_size: tuple, (width, height). The max size of the object in pixels. By default there is no max size.
anchor: string. Which part of the object that will be on the position coordinates. See docs for class MenuObject for a list of valid anchors. 

## Class Rect
Used for placing rectangles in menues.

class Rect(pos, size, color)

pos: tuple, (x, y). The position of the rectangle in pixels, relative to the menu.
size: tuple, (width, height). The size of the rectangle.
color: tuple, (R, G, B) or (R, G, B, A). The color of the rectangle.

Keyword arguments (optional):
outline_width: int. The width of the rectangle's outline.
outline_color: tuple, (R, G, B) or (R, G, B, A). The color of the rectangle's outline.
border_radius: int. The radius of the rectangle's cut-off corners. Disabled by default.
max_size: tuple, (width, height). The max size of the object in pixels. By default there is no max size.
anchor: string. Which part of the object that will be on the position coordinates. See docs for class MenuObject for a list of valid anchors.
Note: if either of outline_width and outline_color is not specified, outline will be disabled.

## Class Button
Used for placing buttons in menues. Buttons can contain an image, text, or a rectangle. Or any combination of the three,

class Button(pos)

pos: tuple, (x, y). The position of the button in pixels, relative to the menu.

Keyword arguments (optional):
max_size: tuple, (width, height). The max size of the object in pixels. By default there is no max size.
anchor: string. Which part of the object that will be on the position coordinates. See docs for class MenuObject for a list of valid anchors.
image: pygame.image. The image to be shown. Created with pygame.image.load(). If not specified, there will be no image on the button.
hover_image: pygame.image. The image to be shown while mouse is hovering over the button. If not specified, the normal image will be shown while mouse is hovering.
click_image: pygame.image. The image to be shown while button is clicked down. If not specified, the normal image will be shown while button is clicked down.
text: string. The text on the button. If not specified, there will be no text on the button.
font: string. The name of the font. If font is not found in SysFont, it will be searched for in the root of your project.
font_size: int. The size of the font.
text_color: tuple, (R, G, B) or (R, G, B, A). The color of the text.
text_hover_color: tuple, (R, G, B) or (R, G, B, A). The color of the text while mouse is hovering.
text_click_color: tuple, (R, G, B) or (R, G, B, A). The color of the text when the button is clicked down.
hitbox_padding: int. Increases the hitbox size [pixels].
command: function. Function to be executed when button is pressed.
enable_rect: bool. Enables a rectangle around the button's text or image.
rect_padx: int. Makes the rectangle extra large horizontally.
rect_pady: int. Makes the rectangle extra large vertically.
rect_border_radius: int. The radius of the rectangle's rounded corners. 0 by default, which disables rounded corners.
rect_outline_width: int. The width of the rectangle's outline. 0 by default, which disables the outline.
rect_color: tuple, (R, G, B) or (R, G, B, A). The color of the rectangle.
rect_hover_color: tuple, (R, G, B) or (R, G, B, A). The color of the rectangle while hovering.
rect_click_color: tuple, (R, G, B) or (R, G, B, A). The color of the rectangle while clicked down.
rect_outline_color: tuple, (R, G, B) or (R, G, B, A). The color of the rectangle's outline.
rect_outline_hover_color: tuple, (R, G, B) or (R, G, B, A). The color of the rectangle's outline while hovering.
rect_outline_click_color: tuple, (R, G, B) or (R, G, B, A). The color of the rectangle's outline while clicked down.

## Class Checkbutton

class Checkbutton(pos, text, font, font_size, text_color)

pos: tuple, (x, y). The position of the button in pixels, relative to the menu.
text: string. The text which will be displayed to the right of the button.
font: string. The name of the font. If font is not found in SysFont, it will be searched for in the root of your project.
font_size: int. The size of the font.

Keywod arguments (optional):
max_size: tuple, (width, height). The max size of the object in pixels. By default there is no max size.
anchor: string. Which part of the object that will be on the position coordinates. See docs for class MenuObject for a list of valid anchors.

text_color: tuple, (R, G, B) or (R, G, B, A). The color of the text. White by default.
text_hover_color: tuple, (R, G, B) or (R, G, B, A). The color of the text while mouse is hovering.
text_click_color: tuple, (R, G, B) or (R, G, B, A). The color of the text when the button is clicked down.
square_color: tuple, (R, G, B) or (R, G, B, A). The color of the squares. White by default.
square_hover_color: tuple, (R, G, B) or (R, G, B, A). The color of the squares while mouse is hovering.
square_click_color: tuple, (R, G, B) or (R, G, B, A). The color of the squares when the button is clicked down.
square_size: int. Used to multiply the size of the square, be default it is customized to the text's height.
image: pygame.image. The image to be shown. Created with pygame.image.load(). If not specified, there will be no image on the button.
hover_image: pygame.image. The image to be shown while mouse is hovering over the button. If not specified, the normal image will be shown while mouse is hovering.
click_image: pygame.image. The image to be shown while button is clicked down. If not specified, the normal image will be shown while button is clicked down.
text_offset: int. The distance between the button and the text. 10 by default.
hitbox_padding: int. Increases the hitbox size [pixels].
command: function. Function to be executed when button is pressed.