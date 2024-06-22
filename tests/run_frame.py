from PhoenixGUI import *
from PhoenixGUI.text_input import validity_check
import pygame

pygame.init()

screen = pygame.display.set_mode((800, 800))
menu_handler = MenuHandler()
menu_handler.set_scroll_strength_multiplier(3)


my_menu = Menu((50, 50), (500, 600), enable_scroll=True, outline_width=1, outline_color=(255, 0, 0), max_scroll_offset=20, scroll_slidebar="sldbr")
menu_handler.add_menu("menu", my_menu)

dropdown = Dropdown((300, 600), (100, 30), "arial", 20, ["Johannes", "Bingus", "Bongus", "Bungus"], "Johannes", box_bg_color=(0, 0, 255), box_outline_color=(255, 255, 255), box_bg_hover_color=(0, 0, 200), box_outline_hover_color=(255, 255, 255), box_bg_click_color=(0, 0, 150), box_outline_click_color=(255, 255, 255))
menu_handler.add_object("menu", "dropdown", dropdown)
dropdown.is_dropped_down = True

menu2 = Menu((200, 200), (300, 300), active=False, bg_color=(100, 100, 100, 200), outline_width=1, outline_color=(0, 255, 0))
menu_handler.add_menu("menu2", menu2)
menu2.set_layer(1)

#text = Text((50, 50), "Hello lorem ipsum dolor%%0 255 0%There lorem ipsum% Hello again", "arial", 20, color=(255, 0, 0), wrap_lines=True)
#menu_handler.add_object("menu", "my_text", text)

image = pygame.image.load(__file__[:-18]+"kenneth.jpg")
menu_image = Image((0, 0), image, anchor="nw")
menu_handler.add_object("menu", "my_image", menu_image)

text2 = Text([300, 300], "Hello lorem ipsum dolor%%0 255 0%There lorem ipsum% Hello again", "arial", 20, color=(255, 0, 0), wrap_lines=True, anchor="se")
menu_handler.add_object("menu2", "my_text", text2)

button = Button((0, 700), 
                text="Johannes",
                text_color=(255, 255, 255),
                text_hover_color=(255, 100, 100),
                text_click_color=(150, 0, 0),
                font="arial",
                font_size=20,
                enable_rect=True,
                command=menu2.activate,
                rect_padx=100,
                rect_pady=5,
                rect_color=(0, 0, 255),
                rect_outline_color=(255, 255, 255),
                anchor="sw",
                text_justify="right")
menu_handler.add_object("menu", "button", button)

button2 = Button((400, 520), 
                text="Inte Johannes",
                text_color=(255, 255, 255),
                text_hover_color=(255, 100, 100),
                text_click_color=(150, 0, 0),
                font="arial",
                font_size=20,
                enable_rect=True,
                command=menu2.activate,
                rect_padx=10,
                rect_pady=5,
                rect_color=(0, 0, 255),
                rect_outline_color=(255, 255, 255),
                anchor="w")
menu_handler.add_object("menu", "button2", button2)


button3 = Button((400, 520), 
                text="Inte Johannes",
                text_color=(255, 255, 255),
                text_hover_color=(255, 100, 100),
                text_click_color=(150, 0, 0),
                font="arial",
                font_size=20,
                enable_rect=True,
                command=menu2.activate,
                rect_padx=10,
                rect_pady=5,
                rect_color=(0, 0, 255),
                rect_outline_color=(255, 255, 255),
                anchor="e")
menu_handler.add_object("menu", "button3", button3)

button4 = Button((250, 600),
                text="banan",
                text_color=(255, 255, 255),
                text_hover_color=(255, 100, 100),
                text_click_color=(150, 0, 0),
                font="arial",
                font_size=20,
                enable_rect=True,
                command=menu2.activate,
                rect_height=50,
                rect_color=(0, 0, 255),
                rect_outline_color=(255, 255, 255),
                anchor="s",
                rect_length=200,
                text_justify="left")
menu_handler.add_object("menu", "button4", button4)



def c1():
    menu2.activate()

def c2():
    menu2.deactivate()

#rect = Rect((200, 200), (200, 200), (100, 100, 255), border_radius=40, anchor="c", width=5)
#menu_handler.add_object("menu", "rect", rect)

circle = Shape((200, 200), (100, 100), (255, 0, 255), "circle")
menu_handler.add_object("menu", "circle", circle)
button2.command = circle.switch_active

checkbutton = Checkbutton((50, 400), "Hola Bingus", "arial", 20, (255, 255, 255), anchor="nw", square_color=(255, 255, 255), square_size=1, text_hover_color=(255, 0, 0))
menu_handler.add_object("menu", "cbtn", checkbutton)

radiobutton = Radiobutton((50, 450), "Not Bingus", "arial", 20, (255, 255, 255), text_hover_color=(255, 0, 0), group="r", command=c1)
menu_handler.add_object("menu", "rbtn", radiobutton)

radiobutton2 = Radiobutton((50, 500), "Really Not Bingus", "arial", 20, (255, 255, 255), text_hover_color=(255, 0, 0), group="r", command=c2, circle_size=2)
menu_handler.add_object("menu", "rbtn2", radiobutton2)

slidebar = Slidebar((500, 300), 600, 40, circle_hover_color=(255, 0, 0), circle_click_color=(0, 255, 255), orientation="vertical", anchor="e")
menu_handler.add_object("menu", "sldbr", slidebar)


sldbr_rect = Shape((250, 400), (100, 20), (0, 255, 255), "rect")
menu_handler.add_object("menu", "sldbr_rect", sldbr_rect)
slidebar2 = Slidebar((250, 400), 100, 20, circle_hover_color=(255, 0, 0), circle_click_color=(255, 0, 255), orientation="horizontal")
menu_handler.add_object("menu", "sldbr2", slidebar2)

text_input_rect = Shape((50, 600), (100, 25), (0, 140, 140), "rect")
menu_handler.add_object("menu", "text_input_rect", text_input_rect)

text_input = TextInput((50, 600), 100, "arial", 20, (255, 255, 255), anchor="nw", validity_check=validity_check.ALL_NUMBERS_DOTS_COMMAS)
# text_input.text_left = "Hello"
# text_input.text_right = " World"
# text_input.is_selected = True
# menu_handler.selected_text_input = text_input
menu_handler.add_object("menu", "text_input", text_input)


# images = {
#     "my_image": pygame.image.load(__file__[:-18]+"kenneth.jpg")
# }

# data = {
#     "my_menu": {
#         "pos": (0, 0),
#         "size": (200, 200),
#         "objects": {
#             "my_shape": {
#                 "type": "shape",
#                 "pos": (0, 0),
#                 "size": (40, 40),
#                 "color": (255, 0, 0),
#                 "type_": "rect"
#             },
#             "my_image": {
#                 "type": "image",
#                 "pos": (50, 50),
#                 "image": "my_image"
#             }
#         }
#     }
# }

# menu_handler.load_data_from_dict(data, images)
# menu_handler.menues["my_menu"].activate()


clock = pygame.time.Clock()
while 1:
    screen.fill((0, 0, 0))

    events = pygame.event.get()
    menu_handler.update(events, screen, clock.get_time())
    #pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(200, 200, 200, 200), 1)

    pygame.display.flip()
    clock.tick(165)
    #print("FPS:", round(clock.get_fps()))
