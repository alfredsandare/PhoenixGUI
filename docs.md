# Documentation

## Class MenuHandler

class MenuHandler()

Keyword parameters:  
ui_size=1: int. Multiplicative factor of the ui's size.

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

To assign images correctly, the dict should only contain an image id as the value of the keys 'image', 'hover_image' or 'click_image'. The images will then be searched for in the 'images' parameter, where the actual images should be.

#### add_font_path(path)
Adds an absolute path where the MenuHandler will search for .ttf files. This function should be called after all menues and objects have been loaded.

#### update(events, screen)
Updates the MenuHandler. This function should be called once every frame in your game.

Parameters:  
events: List[pygame.Event]. A list of the pygame events that are recieved from pygame.  
screen: pygame.Surface. The surface you want everything displayed on.


## Class MenuObject

The superclass for all menu objects.

### Properties:
Each property has a getter and setter, see subtitle "methods" further down.

pos: The position (in pixels) of the object relative to the menu's position.

max_size: Used to set a maximum size of the object. The object will automatically never exceed the menu borders. E.g. if you have a text object with alternating text based on the state of the game/application, you define a maximum size for the text.  

anchor: Which part of the object that will be anchored to the position coordinates. Valid anchors are: "nw", "n", "ne", "w", "c", "e", "sw", "s", "se".

layer: int. The item's layer. The Menu will sort its objects in ascending order before drawing them.

active: bool. Whether or not this item will be displayed.

### Methods

set_layer(layer)

Parameters:
layer: int.


## Class Text
Used for placing text in menues.

class Text(pos, text, font, font_size)

### Parameters

pos: tuple, (x, y). The position of the text in pixels, relative to the menu.


text: string. The text which will be displayed.


font: string. The name of the font. If font is not found in SysFont, it will be searched for in the root of your project.

font_size: int. The size of the font.

### Keyword arguments (optional arguments):
max_size: tuple, (width, height). The max size of the object in pixels. By default there is no max size.

wrap_lines: bool. If true and the text is longer the the object's width the lines will be wrapped.

color: tuple, (R, G, B) or (R, G, B, A). The color of the text.

bg_color: tuple, (R, G, B) or (R, G, B, A). The text's background color. Is transparent by default.

### Text color insertion
Text color insertion enables you to create text with different colors in it. The class' property 'color' will be used as a default value. To make a part of a text be a different color, put two percent signs followed by the RGB code, followed by another percent sign, then the text actual text and last a conclusive percent sign. It should be formatted like this: 'foo %%255 0 0%bar%'. That library will render 'foo ' in the default color, and render 'bar' in red. If you want to include a percent sign in the text that's inside a "color zone", simply put a backslash ('\\') before it.

## Class Image
Used for placing images in menues.

class Image(pos, image)

### Parameters

pos: tuple, (x, y). The position of the text in pixels, relative to the menu.

image: pygame.image. The image to be shown. Created with pygame.image.load().

### Keyword arguments

max_size: tuple, (width, height). The max size of the object in pixels. By default there is no max size.

anchor: string. Which part of the object that will be on the position coordinates. See docs for class MenuObject for a list of valid anchors. 

## Class Shape
Used for placing shapes in menues. Can be either rectangle or circle.

class Rect(pos, size, color)

### Parameters

pos: tuple, (x, y). The position of the rectangle in pixels, relative to the menu.

size: tuple, (width, height). The size of the rectangle.

color: tuple, (R, G, B) or (R, G, B, A). The color of the rectangle.

type_: str. Either "rect" or "circle"

### Keyword arguments (optional):

outline_width: int. The width of the rectangle's outline.

outline_color: tuple, (R, G, B) or (R, G, B, A). The color of the rectangle's outline.

border_radius: int. The radius of the rectangle's cut-off corners. Disabled by default.

See docs for the superclass MenuObject for more kwargs.

Note: if either of outline_width and outline_color is not specified, outline will be disabled.

## Class Button
Used for placing buttons in menues. Buttons can contain an image, text, or a rectangle. Or any combination of the three,

class Button(pos)

## Paramters

pos: tuple, (x, y). The position of the button in pixels, relative to the menu.

### Keyword arguments (optional):

image: pygame.image. The image to be shown. Created with pygame.image.load(). If not specified, there will be no image on the button.

hover_image: pygame.image. The image to be shown while mouse is hovering over the button. If not specified, the normal image will be shown while mouse is hovering.

click_image: pygame.image. The image to be shown while button is clicked down. If not specified, the normal image will be shown while button is clicked down.

text: string. The text on the button. If not specified, there will be no text on the button.

font: string. The name of the font. If font you have custom fonts in .ttf files, you can register their path with MenuHandler.add_font_path().

font_size: int. The size of the font.

text_color: tuple, (R, G, B) or (R, G, B, A). The color of the text. White by default.

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

### Parameters

pos: tuple, (x, y). The position of the button in pixels, relative to the menu.

text: string. The text which will be displayed to the right of the button.

font: string. The name of the font. If font is not found in SysFont, it will be searched for in the root of your project.

font_size: int. The size of the font.

### Keyword arguments:

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

## Class Slidebar

class Slidebar(pos, length, circle_size)

Used to instantiate slidebar objects. Think of the whole thing as a rectangle with a circle on it, although only the circle is actually rendered. No rectangle will be rendered, you'll have to put one behind it manually should you wish to. The rectangle's length will be set to the length specified with the 'length' parameter, and its width will be set to the diameter (size) of the circle. A slidebar's anchor is applied to the rectangle and not the circle.

### Parameters:

pos: tuple, (x, y). The position of the button in pixels, relative to the menu.

length: int. The length of the slidebar. The circle size is included in the length.

circle_size: int. The diameter of the circle.

### Keyword arguments:

orientation: str. The orientation of the slidebar. Either 'horizontal' or 'vertical'. 'horizontal' by default.

circle_color: tuple, (R, G, B) or (R, G, B, A). The color of the circle. White by default.

circle_hover_color: tuple, (R, G, B) or (R, G, B, A). The color of the circle when the mouse is hovering on it.

circle_click_color: tuple, (R, G, B) or (R, G, B, A). The color of the circle when it's clicked on.