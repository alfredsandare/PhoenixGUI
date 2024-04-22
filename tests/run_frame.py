from PhoenixGUI import *
import pygame

screen = pygame.display.set_mode((800, 800))
menu_handler = MenuHandler(screen, 1)
menu_handler.set_scroll_strength_multiplier(3)

my_menu = Menu((50, 50), (500, 600), enable_scroll=True, scroll_slidebar="sldbr")
menu_handler.add_menu("menu", my_menu)
my_menu.set_outline(1, (255, 0, 0))

menu2 = Menu((200, 200), (300, 300), active=False, bg_color=(100, 100, 100, 200))
menu_handler.add_menu("menu2", menu2)
menu2.set_layer(1)
menu2.set_outline(1, (0, 255, 0))

#text = Text((50, 50), "Hello lorem ipsum dolor%%0 255 0%There lorem ipsum% Hello again", "arial", 20, color=(255, 0, 0), wrap_lines=True)
#menu_handler.add_object("menu", "my_text", text)

image = pygame.image.load(__file__[:-18]+"kenneth.jpg")
menu_image = Image((0, 0), image, anchor="nw")
menu_handler.add_object("menu", "my_image", menu_image)

text2 = Text((50, 150), "Hello lorem ipsum dolor%%0 255 0%There lorem ipsum% Hello again", "arial", 20, color=(255, 0, 0), wrap_lines=True)
menu_handler.add_object("menu2", "my_text", text2)

button = Button((50, 700), 
                text="Johannes",
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
                rect_outline_color=(255, 255, 255))
menu_handler.add_object("menu", "button", button)

def c1():
    menu2.activate()

def c2():
    menu2.deactivate()

#rect = Rect((200, 200), (200, 200), (100, 100, 255), border_radius=40, anchor="c", width=5)
#menu_handler.add_object("menu", "rect", rect)

circle = Shape((200, 200), (100, 100), (255, 0, 255), "ellipse")
menu_handler.add_object("menu", "circle", circle)

checkbutton = Checkbutton((50, 400), "Hola Bingus", "arial", 20, (255, 255, 255), anchor="nw", square_color=(255, 255, 255), square_size=1, text_hover_color=(255, 0, 0))
menu_handler.add_object("menu", "cbtn", checkbutton)

radiobutton = Radiobutton((50, 450), "Not Bingus", "arial", 20, (255, 255, 255), text_hover_color=(255, 0, 0), group="r", command=c1)
menu_handler.add_object("menu", "rbtn", radiobutton)

radiobutton2 = Radiobutton((50, 500), "Really Not Bingus", "arial", 20, (255, 255, 255), text_hover_color=(255, 0, 0), group="r", command=c2, circle_size=2)
menu_handler.add_object("menu", "rbtn2", radiobutton2)

slidebar = Slidebar((475, 25), 550, 40, circle_hover_color=(255, 0, 0), circle_click_color=(0, 255, 255), orientation="vertical")
menu_handler.add_object("menu", "sldbr", slidebar)



clock = pygame.time.Clock()
while 1:
    screen.fill((0, 0, 0))

    events = pygame.event.get()
    menu_handler.update(events, screen)
    #pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(200, 200, 200, 200), 1)

    pygame.display.flip()
    clock.tick(60)
    #print("FPS:", clock.get_fps())
