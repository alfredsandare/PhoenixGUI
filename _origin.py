import pygame
from pygame.locals import *
import pickle
import time
import copy
import math
import os
import random
from PhysicsEngine import PhysicsEngine
from DataHandler import DataHandler

path = ''.join(f"{n}\\" for n in __file__.split('\\')[:-1])

from threading import Thread
def Loop():
    while 1:
        time.sleep(1)
Thread(target=Loop).start()

pygame.init()

class Game:
    def __init__(self):

        '''
        self.settings = {
            'size': [1280, 720], #1440 1080
            'fullscreen': False,
            'invert-scroll': False,
            'scroll-sens': 1,
            'planet-size-compensation': 4, # multiplier for planet size
            'units': {
                'mass': 'prefix', # 'scientific', 'prefix' or 'comparative'
                'radius': 'plain', # 'plain' or 'comparative'
                'gravity': 'plain', # 'plain' or 'comparative'
                'temperature': 'c', #'k', 'c' or 'f'
                'sma': 'km', # 'au' or 'km'
                'luminosity': 'prefix' # 'scientific', 'prefix' or 'comparative'
            },
            'prefixSet': 'british', # 'british', 'american' or 'unit'
            'zoom-speed': 0.25, #this is a percentage. 100% is instant zoom and ->0 zoom is very slow
            'show-moons-in-ledger': False,
            'master-volume': 1,
        }
        '''
        self.LoadSettings(fromFile=True)
        
        self.frameSize = self.settings['size']
        if self.settings['fullscreen']:
            self.screen = pygame.display.set_mode(self.frameSize, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.frameSize)

        pygame.font.init()

        self.images = {}
        os.chdir(path+'graphics\\')
        files = os.listdir(os.getcwd())
        for file in files:
            if file[-4:] == '.png':
                self.images[file[:-4]] = pygame.image.load(path+'graphics\\'+file).convert_alpha()
            else:
                os.chdir(f'{path}graphics\\{file}\\')
                subfiles = os.listdir(os.getcwd())
                for subfile in subfiles:
                    self.images[f'{file}_{subfile[:-4]}'] = pygame.image.load(f'{path}graphics\\{file}\\{subfile}')


        self.sounds = {}
        os.chdir(path+'sound\\')
        sounds = os.listdir(os.getcwd())
        for sound in sounds:
            self.sounds[sound[:-4]] = pygame.mixer.Sound(path+'sound\\'+sound)
            self.sounds[sound[:-4]].set_volume(self.settings['master-volume']**0.5)

        pygame.display.set_caption('StarTales')
        pygame.display.set_icon(self.images['game_icon'])

        self.hitboxes = {}
        self.systemHitboxes = []
        self.view = 'mainMenu'

        self.systemPos = [0, 0]
        # zoom mäts i meter/pixel
        self.systemZoom = 2.992 * 10**8 #<- Här blir 1 au 400 pixlar
        self.targetSystemZoom = 2.992 * 10**8
        self.prevSystemZoom = 2.992 * 10**8
        self.allowZoom = [True, True] #in, out
        self.mousePos = [0, 0]
        self.prevMousePos = [0, 0]

        self.galaxyPos = [26000, 0]
        #zoom is measured in light-years/pixel
        self.galaxyZoom = 0.02 #<- 10 light-years make 500 pixles
        self.targetGalaxyZoom = 0.02
        self.prevGalaxyZoom = 0.02

        self.timeState = False #false is pause, true is play
        self.time = 104001 #number of weeks after year 0. 104000 weeks is 2000 years
        self.frameTimeCounter = 0
        self.timeSpeed = 0 #0, 1, 2, 3 or 4.
        self.times = [120, 60, 40, 20, 4]

        self.currentSystem = 'sol'
        self.currentSystemLargestSma = 0

        self.CurrentKeys = []
        self.CurrentlyClickedButton = None

        self.planetMenuPlanet = None
        self.smallPlanetMenuPlanet = None

        self.megaprojectToAdd = None

        self.settingsMenuTabSelection = 0

        self.InitBgImage()

    def InitBgImage(self, keepImage=False):
        if not keepImage:
            self.bgImageName = 'bg_' + str(random.randint(1, 8))
        #resize the bg image so that it keeps its original resolution yet make up the entire screen.
        image = self.images[self.bgImageName]
        imageSize = image.get_size()
        if imageSize[0]/imageSize[1] > self.frameSize[0]/self.frameSize[1]:
            height = self.frameSize[1]
            width = (imageSize[0]/imageSize[1]) * height
        else:
            width = self.frameSize[0]
            height = (imageSize[1]/imageSize[0]) * width
        self.bgImage = pygame.transform.scale(image, (width, height)).convert()

    def InitSystemViewBg(self):
        self.systemViewBg = []
        pixelsPerCircle = 12000
        pixels = self.frameSize[0] * self.frameSize[1]
        circles = int(pixels/pixelsPerCircle)
        for i in range(circles): #make the systemview bg
            #colour = (55-random.randint(0, 50), 55, 55-random.randint(0, 50), random.randint(100, 200))
            pos = (random.randint(0, self.frameSize[0]), random.randint(0, self.frameSize[1]))
            parentRadius = random.randint(2, 4)
            for i in range(3):
                colour = (30+10*i, 30+10*i, 30+10*i)
                radius = int(parentRadius/(i+1))
                self.systemViewBg.append([colour, pos, radius])

    def ChangeSystem(self, newSystem):
        self.currentSystem = newSystem

        largestSma = 0
        for key, planet in physicsEngine.systemsData[self.currentSystem]['planets'].items():
            if planet['type'] != 'star' and not physicsEngine.IsMoon(self.currentSystem, key) and planet['sma'] > largestSma:
                largestSma = planet['sma']
        self.largestSma = largestSma

        menuHandler.InitLedger()
        menuHandler.UpdateMenuData('ledger2')

    def MainLoop(self):
        clock = pygame.time.Clock()
        FPSCounter = 0

        menuHandler.AddMenu('mainMenu')

        while True:

            self.screen.fill((0, 0, 0))
            self.timeStamps = [time.time()]


            menuesToUpdate = []
            reversedMenues = menuHandler.currentMenues.copy()
            if 'hoverMenu' in reversedMenues:
                reversedMenues.remove('hoverMenu')
            reversedMenues.reverse()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.Commands('quitGame')
                elif event.type == 1025 and event.button < 4:
                    buttons = ['LMB', 'MB2', 'RMB']
                    self.CurrentKeys.append(buttons[event.button - 1])
                elif event.type == 1026 and event.button < 4:
                    buttons = ['LMB', 'MB2', 'RMB']
                    try: #detta är bara en failsafe. Vet ej om den faktiskt kan faila dock.
                        self.CurrentKeys.remove(buttons[event.button - 1])
                    except:
                        pass

                    if event.button == 1 and menuHandler.selectedSlidebar != None: # if mouse up, deselect slidebar
                        menu, key = menuHandler.selectedSlidebar
                        menuHandler.menuesData[menu][key]['state'] = False
                        menuHandler.selectedSlidebar = None


                elif event.type == 1027: #scroll
                    scroll = event.y
                    if self.settings['invert-scroll']:
                        scroll *= -1

                    mouseInsideMenu = False
                    for menu in reversedMenues:

                        if menu in menuHandler.interactiveMenues:
                            menuSize = menuHandler.menuesData[menu]['size']
                            if type(menuSize) is str and menuSize[:6] == '/value':
                                menuSize = menuHandler.Values(menuSize)

                            menuPos = menuHandler.menuesData[menu]['pos']
                            if type(menuPos) is str and menuPos[:6] == '/value':
                                menuPos = menuHandler.Values(menuPos)

                            menuHitbox = [menuPos[0], menuPos[1], menuPos[0]+menuSize[0], menuPos[1]+menuSize[1]]

                            if self.mousePos[0] > menuHitbox[0] and self.mousePos[1] > menuHitbox[1] and self.mousePos[0] < menuHitbox[2] and self.mousePos[1] < menuHitbox[3]:
                                mouseInsideMenu = True 
                                if 'scroll' in menuHandler.menuesData[menu].keys():
                                    if int(menuHandler.menuesData[menu]['maxScroll']) <= 0: # if there are not enough items in the menu, there's no point in scrolling
                                        scrollPerFrame = (8 * scroll * self.settings['scroll-sens']) / 6 # the scroll is distrubted over 6 frames
                                        for i in range(6):
                                            if len(menuHandler.menuesData[menu]['scrollQueue']) > i:
                                                menuHandler.menuesData[menu]['scrollQueue'][i] += scrollPerFrame
                                            else:
                                                menuHandler.menuesData[menu]['scrollQueue'].append(scrollPerFrame)

                                        if 'linkedScrollbar' in list(menuHandler.menuesData[menu].keys()):
                                            _scroll = menuHandler.menuesData[menu]['scroll'] + sum(menuHandler.menuesData[menu]['scrollQueue'])

                                            if _scroll > 0:
                                                _scroll = 0
                                            elif _scroll < menuHandler.menuesData[menu]['maxScroll']:
                                                _scroll = menuHandler.menuesData[menu]['maxScroll']

                                            scrollQuota = _scroll / menuHandler.menuesData[menu]['maxScroll']
                                            linkedMenu, key = menuHandler.menuesData[menu]['linkedScrollbar']
                                            menuHandler.menuesData[linkedMenu][key]['progress'] = scrollQuota
                                            menuesToUpdate.append(linkedMenu)
                                break

                    if not mouseInsideMenu and not any([menu in menuHandler.currentMenues for menu in ['escapeMenu', 'savegamesMenuSave']]) and self.view in ['system', 'galaxy']:
                        if event.y < 0 and self.allowZoom[1] and self.view == 'system':
                            self.targetSystemZoom *= 2**abs(scroll)
                        elif event.y > 0 and self.allowZoom[0] and self.view == 'system':
                            self.targetSystemZoom *= 0.5**scroll

                        elif event.y < 0 and self.targetGalaxyZoom < 125 and self.view == 'galaxy':
                            self.targetGalaxyZoom *= 2**abs(scroll)
                        elif event.y > 0 and self.targetGalaxyZoom > 0.00125 and self.view == 'galaxy':
                            self.targetGalaxyZoom *= 0.5**scroll

                elif event.type == 768: #keydown
                    self.CurrentKeys.append(event.unicode)
                    if event.unicode == '\x1b' and self.view == 'system': # esc
                        if 'savegamesMenuSave' in menuHandler.currentMenues:
                            self.Commands('exitSavegamesMenuSave')
                        elif self.smallPlanetMenuPlanet != None:
                            self.Commands('close_small_planet_menu_planet')
                        elif 'planetMenu' in menuHandler.currentMenues:
                            self.Commands('close_planet_menu')
                        elif 'escapeMenu' not in menuHandler.currentMenues:
                            self.Commands('enterEscapeMenu')
                        elif 'escapeMenu' in menuHandler.currentMenues:
                            self.Commands('exitEscapeMenu')

                    elif event.unicode == ' ' and self.view == 'system' and \
                        not any([menu in menuHandler.currentMenues for menu in ['escapeMenu', 'savegamesMenuSave']]):
                        self.Commands('time_clicked')

                    elif event.unicode == 'g' and self.view in ['system', 'galaxy']:
                        self.Commands('systemGalaxySwitch')

                elif event.type == 769: #keyup
                    self.CurrentKeys.remove(event.unicode)

                elif event.type == 1024: #mouse motion
                    self.mousePos = event.pos

                    if menuHandler.selectedSlidebar != None:
                        menu, key = menuHandler.selectedSlidebar

                        menuPos = menuHandler.menuesData[menu]['pos']
                        itemPos = menuHandler.menuesData[menu][key]['pos']
                        itemSize = menuHandler.menuesData[menu][key]['size']

                        xChange = event.rel[0] / itemSize[0]
                        yChange = event.rel[1] / itemSize[1]

                        if type(menuPos) is str and menuPos[:6] == '/value':
                            menuPos = menuHandler.Values(menuPos)

                        if menuHandler.selectedSlidebarOrientation == 'horizontal':
                            if menuPos[0] + itemPos[0] <= self.prevMousePos[0] <= menuPos[0] + itemPos[0] + itemSize[0]:
                                menuHandler.menuesData[menu][key]['progress'] += xChange
                        else:
                            if menuPos[1] + itemPos[1] <= self.prevMousePos[1] <= menuPos[1] + itemPos[1] + itemSize[1]:
                                menuHandler.menuesData[menu][key]['progress'] += yChange
                                linkedMenu = menuHandler.menuesData[menu][key]['menu']
                                maxScroll = menuHandler.menuesData[linkedMenu]['maxScroll']
                                scrollQuota = menuHandler.menuesData[menu][key]['progress']
                                scroll = scrollQuota * maxScroll
                                if int(menuHandler.menuesData[linkedMenu]['maxScroll']) <= 0:
                                    menuHandler.menuesData[linkedMenu]['scroll'] = scroll
                                    menuHandler.UpdateMenuData(linkedMenu)

                        if menuHandler.menuesData[menu][key]['progress'] > 1:
                            menuHandler.menuesData[menu][key]['progress'] = 1
                        elif menuHandler.menuesData[menu][key]['progress'] < 0:
                            menuHandler.menuesData[menu][key]['progress'] = 0

                    if self.view == 'system' and 'MB2' in self.CurrentKeys:
                        self.systemPos[0] -= event.rel[0] * self.systemZoom
                        self.systemPos[1] -= event.rel[1] * self.systemZoom
                    elif self.view == 'galaxy' and 'MB2' in self.CurrentKeys:
                        self.galaxyPos[0] -= event.rel[0] * self.galaxyZoom
                        self.galaxyPos[1] -= event.rel[1] * self.galaxyZoom
                        
                if event.type == 771 or (event.type == 768 and event.unicode == '\x08'): #text input
                    for menu in menuHandler.currentMenues:
                        for key, item in menuHandler.menuesData[menu].items():
                            if type(item) is dict: #filter away menu pos and size amogus
                                if item['type'] == 'textInput' and item['state']:
                                    if event.type == 771:
                                        menuHandler.menuesData[menu][key]['text'] += event.text
                                    else:
                                        menuHandler.menuesData[menu][key]['text'] = menuHandler.menuesData[menu][key]['text'][:-1]
                                    self.Commands(item['onUpdateCommand'])
                                    menuesToUpdate.append(menu)
                                    break

                selectedTextInput = None
                if event.type == 1026 or event.type == 1024 or event.type == 1025: #mouseclick up, hover or mouseclick down
                    x, y = event.pos[0], event.pos[1]
                    for menu in reversedMenues:

                        #get menupos and menusize data
                        menuSize = menuHandler.menuesData[menu]['size']
                        menuPos = menuHandler.menuesData[menu]['pos']
                        if type(menuSize) is str and menuSize[:6] == '/value':
                            menuSize = menuHandler.Values(menuSize)
                        if type(menuPos) is str and menuPos[:6] == '/value':
                            menuPos = menuHandler.Values(menuPos)

                        if menuPos[0] <= x <= menuPos[0] + menuSize[0] and menuPos[1] <= y <= menuPos[1] + menuSize[1]:
                            if menu in menuHandler.interactiveMenues:
                                for hitbox in self.hitboxes[menu]:
                                    if x >= hitbox[1] and x <= hitbox[3] and y >= hitbox[2] and y <= hitbox[4]:
                                        menuHandler.ResetButtons(menu)
                                        
                                        if hitbox[0][:8] == 'treeview' and event.type == 1026:
                                            item, textItem = hitbox[0].split('%')[1], hitbox[0].split('%')[2]
                                            menuHandler.menuesData[menu][item]['items'][textItem]['downTabbed'] = not menuHandler.menuesData[menu][item]['items'][textItem]['downTabbed']

                                        elif hitbox[0][:17] == 'TreeviewSelection':
                                            if event.type == 1026 and event.button == 1:
                                                item, textItem = hitbox[0].split('%')[1], hitbox[0].split('%')[2]
                                                menuHandler.menuesData[menu][item]['selectedItem'] = textItem
                                                if 'selectionCommand' in menuHandler.menuesData[menu][item].keys():
                                                    self.Commands(f'{menuHandler.menuesData[menu][item]["selectionCommand"]} {textItem}')

                                        elif hitbox[0][:9] == 'textInput':
                                            if event.type == 1026 and event.button == 1:
                                                item = hitbox[0].split('%')[1]
                                                menuHandler.menuesData[menu][item]['state'] = True
                                                selectedTextInput = [menu, item]

                                        elif hitbox[0][:16] == 'radiobuttonArray':
                                            item, button = hitbox[0].split('%')[1], int(hitbox[0].split('%')[2])
                                            if event.type == 1026 and event.button == 1:
                                                states = list(menuHandler.menuesData[menu][item]['itemStates'])
                                                states[2*button] = 1
                                                menuHandler.menuesData[menu][item]['itemStates'] = ''.join(states)
                                                menuHandler.menuesData[menu][item]['selectedItem'] = str(button)

                                            elif event.type == 1024 and 'LMB' not in self.CurrentKeys: #hover
                                                states = list(menuHandler.menuesData[menu][item]['itemStates'])
                                                states[2*button] = 1
                                                menuHandler.menuesData[menu][item]['itemStates'] = ''.join(states)

                                            elif event.type == 1025 and event.button == 1: #click
                                                states = list(menuHandler.menuesData[menu][item]['itemStates'])
                                                states[2*button] = 2
                                                menuHandler.menuesData[menu][item]['itemStates'] = ''.join(states)

                                        elif hitbox[0][:8] == 'dropdown':
                                            item = hitbox[0].split('%')[1]
                                            if len(hitbox[0].split('%')) == 2: # this is the top item of the dropdown menu
                                                if event.type == 1026 and event.button == 1:
                                                    menuHandler.menuesData[menu][item]['state'] = 1
                                                    menuHandler.menuesData[menu][item]['droppedDown'] = not menuHandler.menuesData[menu][item]['droppedDown']
                                                elif event.type == 1024 and 'LMB' not in self.CurrentKeys: #hover
                                                    menuHandler.menuesData[menu][item]['state'] = 1
                                                elif event.type == 1025 and event.button == 1: #click
                                                    menuHandler.menuesData[menu][item]['state'] = 2

                                            else: #this is a dropped down item in the menu
                                                listItem = int(hitbox[0].split('%')[2])
                                                if event.type == 1026 and event.button == 1: #clicked
                                                    menuHandler.menuesData[menu][item]['listItemSelected'] = None
                                                    menuHandler.menuesData[menu][item]['selection'] = menuHandler.menuesData[menu][item]['items'][listItem]
                                                    menuHandler.menuesData[menu][item]['droppedDown'] = False
                                                    self.Commands(menuHandler.menuesData[menu][item]['onNewSelectionCommand'])
                                                elif event.type == 1024 and 'LMB' not in self.CurrentKeys: #hover
                                                    menuHandler.menuesData[menu][item]['listItemSelected'] = listItem
                                                    menuHandler.menuesData[menu][item]['listItemSelectionType'] = 'hover'
                                                elif event.type == 1025 and event.button == 1: #click
                                                    menuHandler.menuesData[menu][item]['listItemSelectionType'] = 'click'

                                        elif hitbox[0][:11] == 'checkbutton':
                                            item = hitbox[0].split('%')[1]
                                            if event.type == 1026 and event.button == 1: #clicked
                                                menuHandler.menuesData[menu][item]['selected'] = not menuHandler.menuesData[menu][item]['selected']
                                                self.Commands(menuHandler.menuesData[menu][item]['onUpdateCommand'])
                                                menuHandler.menuesData[menu][item]['state'] = 1
                                            elif event.type == 1024 and 'LMB' not in self.CurrentKeys:
                                                menuHandler.menuesData[menu][item]['state'] = 1
                                            elif event.type == 1025 and event.button == 1:
                                                menuHandler.menuesData[menu][item]['state'] = 2

                                        elif hitbox[0].split('%')[0] in ['horizontalSlidebar', 'scrollbar']:
                                            item = hitbox[0].split('%')[1]
                                            if event.type == 1026 and event.button == 1: #button release
                                                menuHandler.menuesData[menu][item]['state'] = False
                                                menuHandler.selectedSlidebar = None
                                            elif event.type == 1025 and event.button == 1:
                                                menuHandler.menuesData[menu][item]['state'] = True
                                                menuHandler.selectedSlidebar = [menu, item]

                                            if hitbox[0].split('%')[0] == 'horizontalSlidebar':
                                                menuHandler.selectedSlidebarOrientation = 'horizontal'
                                            else:
                                                menuHandler.selectedSlidebarOrientation = 'vertical'

                                        elif hitbox[0].split('%')[0] == 'hover':
                                            if event.type == 1024:
                                                menuHandler.SetHoverMenuData((x, y), menuHandler.hoverMenuData[hitbox[0].split('%')[1]])
                                                #menuHandler.SetHoverMenuData((x, y), menuHandler.hoverMenuData[hitbox[0].split('%')[1]])

                                        else:
                                            item = hitbox[0].split('%')[1]
                                            if event.type == 1026 and event.button == 1:
                                                if (menu, item) == self.CurrentlyClickedButton:
                                                    menuHandler.menuesData[menu][item]['state'] = 1
                                                    pygame.mixer.Sound.play(self.sounds['click3'])
                                                    self.Commands(hitbox[0].split('%')[0])
                                                    break
                                                self.CurrentlyClickedButton = None
                                            elif event.type == 1024:
                                                if 'LMB' in self.CurrentKeys and self.CurrentlyClickedButton == (menu, item): #hover
                                                    menuHandler.menuesData[menu][item]['state'] = 2
                                                elif 'LMB' not in self.CurrentKeys:
                                                    menuHandler.menuesData[menu][item]['state'] = 1
                                            elif event.type == 1025 and event.button == 1: #click
                                                menuHandler.menuesData[menu][item]['state'] = 2
                                                self.CurrentlyClickedButton = (menu, item)
                                        #break

                                    else: #mouse not inside of this hitbox
                                        if hitbox[0].split('%')[0] not in ['treeview', 'textInput', 'treeviewSelection', 'radiobuttonArray', 'dropdown', 'checkbutton', 'horizontalSlidebar', 'scrollbar', 'hover']:
                                            item = hitbox[0].split('%')[1]
                                            menuHandler.menuesData[menu][item]['state'] = 0
                                        elif hitbox[0][:16] == 'radiobuttonArray':
                                            item, button = hitbox[0].split('%')[1], int(hitbox[0].split('%')[2])
                                            states = list(menuHandler.menuesData[menu][item]['itemStates'])
                                            states[2*button] = 0
                                            menuHandler.menuesData[menu][item]['itemStates'] = ''.join(states)
                                        elif hitbox[0][:8] == 'dropdown':
                                            item = hitbox[0].split('%')[1]
                                            menuHandler.menuesData[menu][item]['listItemSelected'] = None
                                            menuHandler.menuesData[menu][item]['state'] = 0
                                        elif hitbox[0][:11] == 'checkbutton':
                                            item = hitbox[0].split('%')[1]
                                            menuHandler.menuesData[menu][item]['state'] = 0
                                        elif hitbox[0].split('%')[0] == 'hover':
                                            menuHandler.DisableHoverMenu()

                            #when found a menu that the cursor is inside of, don't check for more menues
                            break

                    if event.type == 1026 and event.button == 1 and self.view in ['system', 'galaxy'] and \
                    not any([menu in menuHandler.currentMenues for menu in ['escapeMenu', 'savegamesMenuSave']]):
                        for hitbox in self.systemHitboxes:
                            if x >= hitbox[1] and x <= hitbox[3] and y >= hitbox[2] and y <= hitbox[4]:
                                if self.smallPlanetMenuPlanet == None and self.view == 'system':
                                    self.smallPlanetMenuPlanet = hitbox[0].split("%")[1]
                                    menuHandler.AddMenu('smallPlanetMenu')
                                elif self.view == 'system':
                                    self.smallPlanetMenuPlanet = hitbox[0].split("%")[1]
                                    menuHandler.UpdateMenuData('smallPlanetMenu')
                                else: #galaxy view
                                    self.currentSystem = hitbox[0].split('%')[1]
                                    self.Commands('enterSystemView')

                
                if event.type == 1025 and selectedTextInput == None: #deselect all
                    for menu in menuHandler.currentMenues:
                        for key, item in menuHandler.menuesData[menu].items():
                            if type(item) is dict: #filter away menu pos and size
                                if item['type'] == 'textInput' and item['state']:
                                    menuHandler.menuesData[menu][key]['state'] = False

                for menu in menuHandler.currentMenues:

                    pos = menuHandler.menuesData[menu]['pos']
                    if pos[:6] == '/value':
                        pos = menuHandler.Values(pos)
                    size = menuHandler.menuesData[menu]['size']
                    if size[:6] == '/value':
                        size = menuHandler.Values(size)
                    if type(pos) is str:
                        pos = [int(pos.split()[i]) for i in range(2)]
                    if type(size) is str:
                        size = [int(size.split()[i]) for i in range(2)]                    

                    if pos[0] <= self.mousePos[0] <= pos[0] + size[0] and pos[1] <= self.mousePos[1] <= pos[1] + size[1] and menu not in menuesToUpdate:
                        menuesToUpdate.append(menu)




            if self.view == 'system' and not any([menu in menuHandler.currentMenues for menu in ['escapeMenu', 'savegamesMenuSave']]):
                # preventing the user from going away from the system
                if 'w' in self.CurrentKeys and self.systemPos[1] > -self.frameSize[1]*self.systemZoom/2-self.largestSma:
                    self.systemPos[1] -= self.systemZoom*10
                if 's' in self.CurrentKeys and self.systemPos[1] < self.frameSize[1]*self.systemZoom/2+self.largestSma:
                    self.systemPos[1] += self.systemZoom*10
                if 'a' in self.CurrentKeys and self.systemPos[0] > -self.frameSize[0]*self.systemZoom/2-self.largestSma:
                    self.systemPos[0] -= self.systemZoom*10
                if 'd' in self.CurrentKeys and self.systemPos[0] < self.frameSize[0]*self.systemZoom/2+self.largestSma:
                    self.systemPos[0] += self.systemZoom*10

            elif self.view == 'galaxy' and not any([menu in menuHandler.currentMenues for menu in ['escapeMenu', 'savegamesMenuSave']]):
                if 'w' in self.CurrentKeys:
                    self.galaxyPos[1] -= self.galaxyZoom*10
                if 's' in self.CurrentKeys:
                    self.galaxyPos[1] += self.galaxyZoom*10
                if 'a' in self.CurrentKeys:
                    self.galaxyPos[0] -= self.galaxyZoom*10
                if 'd' in self.CurrentKeys:
                    self.galaxyPos[0] += self.galaxyZoom*10

            #paragraph below fixes the camera position when zooming, so that the position of the system is still where the mouse cursor is
            if self.systemZoom != self.prevSystemZoom:
                #scale between -1 and 1
                mousePos = [2*self.mousePos[0]/self.frameSize[0]-1, 2*self.mousePos[1]/self.frameSize[1]-1]
                #the length and height of the part of the system that is displayed on the screen
                oldWindowSize = [self.prevSystemZoom * self.frameSize[0], self.prevSystemZoom * self.frameSize[1]]
                newWindowSize = [self.systemZoom * self.frameSize[0], self.systemZoom * self.frameSize[1]]
                    
                cameraDiff = [(oldWindowSize[0] - newWindowSize[0])/2 * mousePos[0], (oldWindowSize[1] - newWindowSize[1])/2 * mousePos[1]]
                self.systemPos[0] += cameraDiff[0]
                self.systemPos[1] += cameraDiff[1]

            if self.galaxyZoom != self.prevGalaxyZoom:
                #scale between -1 and 1
                mousePos = [2*self.mousePos[0]/self.frameSize[0]-1, 2*self.mousePos[1]/self.frameSize[1]-1]
                #the length and height of the part of the system that is displayed on the screen
                oldWindowSize = [self.prevGalaxyZoom * self.frameSize[0], self.prevGalaxyZoom * self.frameSize[1]]
                newWindowSize = [self.galaxyZoom * self.frameSize[0], self.galaxyZoom * self.frameSize[1]]

                cameraDiff = [(oldWindowSize[0] - newWindowSize[0])/2 * mousePos[0], (oldWindowSize[1] - newWindowSize[1])/2 * mousePos[1]]
                self.galaxyPos[0] += cameraDiff[0]
                self.galaxyPos[1] += cameraDiff[1]

            if self.view == 'system':
                if self.timeState:
                    self.frameTimeCounter += 1

                if self.frameTimeCounter >= self.times[self.timeSpeed]:
                    self.TimeTick()

                #abs-orbit-progress is the value of the orbit-progress, and changes only every timetick.
                #However, orbit-progress is used to make the orbit smooth.
                for planet in physicsEngine.systemsData[self.currentSystem]['planets'].values():
                    if planet['type'] != 'star' and planet['orbit-progress'] < planet['abs-orbit-progress']:
                        planet['orbit-progress'] += planet['orbital-velocity']/(2 * math.pi * planet['sma']) * 604800 * 360 * 1/self.times[self.timeSpeed]

                #makes the camera follow a planet
                if self.smallPlanetMenuPlanet != None:
                    planet = self.smallPlanetMenuPlanet
                    starID = list(physicsEngine.systemsData[self.currentSystem]['planets'].keys())[0]
                    if physicsEngine.GetProperty(self.currentSystem, planet, 'type') == 'star':
                        self.systemPos = [0, 0]
                    elif physicsEngine.GetProperty(self.currentSystem, planet, 'host') == starID: #this is a planet
                        angle = physicsEngine.GetProperty(self.currentSystem, planet, 'orbit-progress')
                        sma = physicsEngine.GetProperty(self.currentSystem, planet, 'sma')
                        self.systemPos = [sma * math.cos(angle * math.pi / 180), -sma * math.sin(angle * math.pi / 180)]
                    else: #this is a moon
                        angle = physicsEngine.GetProperty(self.currentSystem, planet, 'orbit-progress')
                        sma = physicsEngine.GetProperty(self.currentSystem, planet, 'sma')
                        host = physicsEngine.GetProperty(self.currentSystem, planet, 'host')
                        host_angle = physicsEngine.GetProperty(self.currentSystem, host, 'orbit-progress')
                        host_sma = physicsEngine.GetProperty(self.currentSystem, host, 'sma')

                        self.systemPos = [sma * math.cos(angle * math.pi / 180) + host_sma * math.cos(host_angle * math.pi / 180), 
                        -sma * math.sin(angle * math.pi / 180) - host_sma * math.sin(host_angle * math.pi / 180)]
                self.RenderSystem(self.currentSystem)

            elif self.view == 'galaxy':
                self.RenderGalaxy()

            else:
                self.screen.blit(self.bgImage, (0, 0))
                logoxSize = self.frameSize[0] * 0.6
                image = pygame.transform.scale(self.images['game_logo'], (logoxSize, logoxSize/6.5)).convert_alpha()
                self.screen.blit(image, (20, 20))

            for menu in menuHandler.currentMenues:
                menuHandler.RenderMenu(menu)

            self.prevSystemZoom = self.systemZoom
            if DataHandler.RoundSignificantFigures(self.systemZoom, 3) == DataHandler.RoundSignificantFigures(self.targetSystemZoom, 3): #if close enough
                self.systemZoom = self.targetSystemZoom
            else:
                self.systemZoom += (self.targetSystemZoom-self.systemZoom) * self.settings['zoom-speed']

            self.prevGalaxyZoom = self.galaxyZoom
            if DataHandler.RoundSignificantFigures(self.galaxyZoom, 3) == DataHandler.RoundSignificantFigures(self.targetGalaxyZoom, 3): #if close enough
                self.galaxyZoom = self.targetGalaxyZoom
            else:
                self.galaxyZoom += (self.targetGalaxyZoom-self.galaxyZoom) * self.settings['zoom-speed']



            for menu in reversedMenues:
                if 'scroll' in menuHandler.menuesData[menu].keys():
                    if len(menuHandler.menuesData[menu]['scrollQueue']) > 0:
                        menuHandler.menuesData[menu]['scroll'] += menuHandler.menuesData[menu]['scrollQueue'][0]
                        del menuHandler.menuesData[menu]['scrollQueue'][0]

                        if menuHandler.menuesData[menu]['scroll'] > 0:
                            menuHandler.menuesData[menu]['scroll'] = 0
                        elif menuHandler.menuesData[menu]['scroll'] < menuHandler.menuesData[menu]['maxScroll']:
                            menuHandler.menuesData[menu]['scroll'] = menuHandler.menuesData[menu]['maxScroll']

                        if menu not in menuesToUpdate:
                            menuesToUpdate.append(menu)

            #menues that are hovered on are only updated when an event is detected
            for menu in menuesToUpdate:
                menuHandler.UpdateMenuData(menu)

            #In the menues that the mouse cursor just left, reset all buttons and update
            for menu in menuHandler.currentMenues:
                
                pos = menuHandler.menuesData[menu]['pos']
                if pos[:6] == '/value':
                    pos = menuHandler.Values(pos)
                size = menuHandler.menuesData[menu]['size']
                if size[:6] == '/value':
                    size = menuHandler.Values(size)
                if type(pos) is str:
                    pos = [int(pos.split()[i]) for i in range(2)]
                if type(size) is str:
                    size = [int(size.split()[i]) for i in range(2)]

                if not (pos[0] <= self.mousePos[0] <= pos[0] + size[0] and pos[1] <= self.mousePos[1] <= pos[1] + size[1]) and \
                pos[0] <= self.prevMousePos[0] <= pos[0] + size[0] and pos[1] <= self.prevMousePos[1] <= pos[1] + size[1]:
                    menuHandler.ResetButtons(menu)
                    menuHandler.UpdateMenuData(menu)
                    menuHandler.DisableHoverMenu()

            self.timeStamps.append(time.time())

            ############################################## GAME LOGIC #########################################################

    


            '''
            self.timeStamps.append(time.time())
            for i in self.timeStamps:
                print(i - self.timeStamps[0])
            print('')
            '''


            pygame.display.flip()
            clock.tick(60)
            #print('FPS:', 1 / (time.perf_counter() - FPSCounter))
            FPSCounter = time.perf_counter()
            #for i in range(3):
            #    print('')

            self.prevMousePos = self.mousePos

    def TimeTick(self):
        self.frameTimeCounter = 0
        self.time += 1
        menuHandler.UpdateMenuData('timeMenu')

        #make the planets progress in their orbits
        for system in physicsEngine.systemsData.keys():
            for planet in physicsEngine.systemsData[system]['planets'].values():
                if planet['type'] != 'star':
                    planet['abs-orbit-progress'] += planet['orbital-velocity']/(2 * math.pi * planet['sma']) * 604800 * 360 #604800 seconds in one week
                    if system != self.currentSystem:
                        planet['orbit-progress'] += planet['orbital-velocity']/(2 * math.pi * planet['sma']) * 604800 * 360
                    if planet['abs-orbit-progress'] > 360:
                        planet['abs-orbit-progress'] -= 360
                        planet['orbit-progress'] -= 360

        #apply megaprojects
        for system in list(physicsEngine.systemsData.keys()):
            for planet in physicsEngine.systemsData[system]['planets'].keys():
                physicsEngine.ApplyMegaprojects(system, planet)

        for system in physicsEngine.systemsData.keys():
            physicsEngine.UpdateSystem(system)

        if self.planetMenuPlanet != None:
            planetType = physicsEngine.GetProperty(self.currentSystem, self.planetMenuPlanet, 'type')

            menuHandler.InitMegaprojectMenues()
            menuesToUpdate = [
                'megaprojects1',
                'megaprojects2',
                'planetMenu2Megaprojects',
                'planetMenu2Orbit',
                'landscapesMenu',
                'landscapesMenu2'
            ]
            if planetType == 'terrestrial':

                menuHandler.InitPlanetAtmMenu()
                menuesToUpdate.append('planetMenu2Physics')
                menuesToUpdate.append('planetMenu2Atmosphere')
                menuesToUpdate.append('planetMenu2Atmosphere2')
                menuesToUpdate.append('planetMenu2Atmosphere3')
                menuesToUpdate.append('planetMenu2Atmosphere4')
            elif planetType == 'gas-giant':
                menuesToUpdate.append('planetMenu2PhysicsGasGiant')
                menuesToUpdate.append('planetMenu2PhysicsGasGiant')
            elif planetType == 'star':
                menuesToUpdate.append('planetMenu2PhysicsStar')

            for menu in menuesToUpdate:
                menuHandler.UpdateMenuData(menu)

    def RenderGalaxy(self):
        #draw the bg
        for circle in self.systemViewBg:
            pygame.draw.circle(self.screen, circle[0], circle[1], circle[2])

        #delete all of these hitboxes
        self.systemHitboxes.clear()

        #galaxy center circle
        '''
        pos = [self.frameSize[0]/2-self.galaxyPos[0]/self.galaxyZoom, self.frameSize[1]/2-self.galaxyPos[1]/self.galaxyZoom]
        radius = 5000/self.galaxyZoom # 10000 lys in diameter
        pygame.draw.circle(self.screen, (200, 200, 200), pos, radius)
        '''
        diameter = 100000/self.galaxyZoom # 100000 lys in diameter
        if diameter < 2600:
            pos = [self.frameSize[0]/2-self.galaxyPos[0]/self.galaxyZoom-diameter/2, self.frameSize[1]/2-self.galaxyPos[1]/self.galaxyZoom-diameter/2]
            image = pygame.transform.scale(self.images['galaxy'], [diameter, diameter])
            self.screen.blit(image, pos)

        nameplates = []
        systems = list(physicsEngine.systemsData.keys())
        for system in systems:
            starPos = physicsEngine.systemsData[system]['properties']['pos'] #(x, y) in light-years
            name = physicsEngine.systemsData[system]['properties']['name']
            star = list(physicsEngine.systemsData[system]['planets'].keys())[0]
            starImage = physicsEngine.GetProperty(system, star, 'image')
            starRadius = physicsEngine.GetProperty(system, star, 'radius')

            size = (10**13 * starRadius**0.3/physicsEngine.const.light_year)/self.galaxyZoom
            image = pygame.transform.scale(self.images[starImage], [size, size])
            pos = (self.frameSize[0]/2+(-self.galaxyPos[0]+starPos[0])/self.galaxyZoom-size/2, self.frameSize[1]/2+(-self.galaxyPos[1]+starPos[1])/self.galaxyZoom-size/2)
            self.screen.blit(image, pos)
            nameplates.append([pos[0]+size/2-60, pos[1]+size+10, system])
            self.systemHitboxes.append([f'galaxy%{system}', pos[0], pos[1], pos[0]+size, pos[1]+size])

        self.ProcessNameplates(nameplates)


    def RenderSystem(self, systemID):

        self.timeStamps.append(time.time())

        #draw the bg
        for circle in self.systemViewBg:
            pygame.draw.circle(self.screen, circle[0], circle[1], circle[2])

        #delete all of these hitboxes
        self.systemHitboxes.clear()

        planets = list(physicsEngine.systemsData[self.currentSystem]['planets'].keys())
        planets.pop(0) #Remove the star
        #list below contains all smas in pixels
        smas = []
        for planet in planets:
            if not physicsEngine.IsMoon(self.currentSystem, planet):
                smas.append(physicsEngine.GetProperty(self.currentSystem, planet, 'sma'))
        smas.sort()
        smallestSmaDiff = smas[1] - smas[0]
        for i in range(len(smas)):
            if i>1: #don't do on the first or second one
                if smas[i] - smas[i-1] < smallestSmaDiff:
                    smallestSmaDiff = smas[i] - smas[i-1]

        planetPositions = {} # the center of the image in pixels
        nameplates = []
        sizes = {}
        planetsOnScreen = []
        for i, (key, planet) in enumerate(physicsEngine.systemsData[systemID]['planets'].items()):

            proceed = False
            if physicsEngine.IsMoon(self.currentSystem, key):
                # sma, radius and host_radius are in pixels
                sma = physicsEngine.GetProperty(self.currentSystem, key, 'sma') / self.systemZoom
                radius = physicsEngine.GetProperty(self.currentSystem, key, 'radius') / self.systemZoom
                host_radius = sizes[physicsEngine.GetProperty(self.currentSystem, key, 'host')]

                if (sma - radius) > host_radius: # if the distant from the planet's edge to the moon's edge is far enough
                    proceed = True
            else:
                proceed = True

            if proceed:
                if planet['type'] == 'star':
                    size = 3 * DataHandler.Map(
                        10000/self.systemZoom, 
                        1000/self.systemZoom,
                        10000/self.systemZoom, 
                        0,
                        physicsEngine.GetProperty(self.currentSystem, planets[0], 'sma')/self.systemZoom)**0.5
                    pos = [int(self.frameSize[0]/2-self.systemPos[0]/self.systemZoom-size/2), int(self.frameSize[1]/2-self.systemPos[1]/self.systemZoom-size/2)]

                elif planet['type'] == 'terrestrial' or planet['type'] == 'gas-giant':

                    #planetsize in meters
                    planetSize = planet['radius']**0.5 #sqrt is to exponentially scale planet size.
                    #don't go above 142% jupiters radius (10000km) and don't go below Dione's radius (1000km)
                    if planetSize < 1000:
                        planetSize = 1000
                    elif planetSize > 10000:
                        planetSize = 10000

                    #planetsize now in pixels
                    size = 2 * DataHandler.Map(
                        planetSize/self.systemZoom, 
                        990/self.systemZoom, 
                        10000/self.systemZoom, 
                        0, 
                        smallestSmaDiff/self.systemZoom)**0.3
                    #**0.3 is to make the planets' sizes become exponentially bigger when zooming in and *25 is just a constant to make the sizes good.

                    pos = [round(planetPositions[planet['host']][0] + planet['sma']/self.systemZoom * math.cos(math.pi*planet['orbit-progress']/180)-size/2),
                           round(planetPositions[planet['host']][1] - planet['sma']/self.systemZoom * math.sin(math.pi*planet['orbit-progress']/180)-size/2)]
                    #circle that represents the orbit of the planet
                    radius = planet['sma']/self.systemZoom

                    if radius < 30000:
                        pygame.draw.circle(self.screen, (100, 100, 100), planetPositions[planet['host']], radius, width=1)
                    # funny coords: [center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius]

                planetPositions[key] = [pos[0]+size/2, pos[1]+size/2]
                if -size < pos[0] < self.frameSize[0] and -size < pos[1] < self.frameSize[1]: #if the image is actually on the screen
                    planetsOnScreen.append(key)
                    image = pygame.transform.scale(self.images[planet['image']], [size, size])
                    if self.smallPlanetMenuPlanet == key: # if the camera is following a planet, just center the planet's position
                        # this makes the planet not shake, but everything else shakes
                        pos = [self.frameSize[0]/2-image.get_width()/2, self.frameSize[1]/2-image.get_height()/2]
                    self.screen.blit(image, pos)
                    nameplates.append([pos[0]+size/2-60, pos[1]+size+10, key])
                    self.systemHitboxes.append([f'systemView%{key}', pos[0], pos[1], pos[0]+size, pos[1]+size])

                sizes[key] = size

        #if some planet is on the screen and big enough, allow no further zoom
        prevAllowZoom = self.allowZoom.copy()
        self.allowZoom[0] = not any([sizes[planet] > 400 for planet in planetsOnScreen])
        self.allowZoom[1] = max(smas)/self.systemZoom > 10
        if (not self.allowZoom[0] and prevAllowZoom[0]) or (not self.allowZoom[1] and prevAllowZoom[1]):
            self.targetSystemZoom = self.systemZoom

        self.timeStamps.append(time.time())

        self.ProcessNameplates(nameplates)

    def ProcessNameplates(self, nameplates):
        #groups structure: [xpos, ypos, [text1, text2...]]
        groups = []
        for nameplate in nameplates:
            foundGroup = False
            for j, group in enumerate(groups):
                if self.EntitiesOverlap([nameplate[0], nameplate[1]], [120, 20], [group[0], group[1]], [120, 25*len(group[2])]):
                    groups[j][2].append(nameplate[2])
                    foundGroup = True
                    break

            if not foundGroup:
                groups.append([nameplate[0], nameplate[1], [nameplate[2]]])

        #Now the groups may overlap eachother on the y-axis.
        #A little something needs to be put here to fix it.

        font = menuHandler.GetFont(menuHandler.Values('/value defaultFont bold'), 15)
        for group in groups:
            for i, key in enumerate(group[2]):
                imageID = 'planet_nameplate_selected' if key == self.smallPlanetMenuPlanet else 'planet_nameplate'
                self.screen.blit(self.images[imageID], [group[0], group[1]+25*i])
                if self.view == 'system':
                    text = physicsEngine.GetProperty(self.currentSystem, key, 'name')
                else: #galaxy
                    text = physicsEngine.systemsData[key]['properties']['name']
                textSize = font.size(text)
                renderedText = font.render(text, True, (255, 255, 255))
                self.screen.blit(renderedText, [group[0]+60-textSize[0]/2, group[1]+25*i+10-textSize[1]/2])
                if self.view == 'system':
                    self.systemHitboxes.append([f'systemView%{key}', group[0], group[1]+25*i, group[0]+120, group[1]+25*i+20])
                else: # galaxy
                    self.systemHitboxes.append([f'galaxy%{key}', group[0], group[1]+25*i, group[0]+120, group[1]+25*i+20])



    def EntitiesOverlap(self, coords1, size1, coords2, size2):
        ''' There are two rectangles, 1 and 2.
        Given one coordinate and the size of the first rectangle, we get 4 coords.
        If any of those coords are within the second rectangle, return True.'''
        coords1 = [coords1, [coords1[0]+size1[0], coords1[1]], [coords1[0], coords1[1]+size1[1]], [coords1[0]+size1[0], coords1[1]+size1[1]]]
        for coords in coords1:
            if coords2[0] < coords[0] <= coords2[0] + size2[0] and coords2[1] < coords[1] <= coords2[1] + size2[1]:
                return True
        return False

    def LoadSettings(self, fromFile=True):
        if fromFile:
            with open(f'{path}data\\settings.dat', 'rb') as file:
                self.settings = pickle.load(file)

        # align the menu items with the actual settings
        menuHandler.menuesData['settingsMenu2_0']['resDropdown']['selection'] = f"{self.settings['size'][0]}x{self.settings['size'][1]}"
        menuHandler.menuesData['settingsMenu2_0']['fullscreenCheckbutton']['selected'] = self.settings['fullscreen']
        menuHandler.menuesData['settingsMenu2_0']['invertScrollCheckbutton']['selected'] = self.settings['invert-scroll']
        menuHandler.menuesData['settingsMenu2_0']['scrollSensSlidebar']['progress'] = self.settings['scroll-sens'] / 10
        menuHandler.menuesData['settingsMenu2_0']['zoomSpeedSlidebar']['progress'] = self.settings['zoom-speed']
        menuHandler.menuesData['settingsMenu2_0']['moonsLedgerCheckbutton']['selected'] = self.settings['show-moons-in-ledger']

        menuHandler.menuesData['settingsMenu2_1']['massDropdown']['selection'] = self.settings['units']['mass'].capitalize()
        menuHandler.menuesData['settingsMenu2_1']['radiusDropdown']['selection'] = self.settings['units']['radius'].capitalize()
        menuHandler.menuesData['settingsMenu2_1']['radiusDropdown']['selection'] = self.settings['units']['gravity'].capitalize()

        convert_temp = {'k': 'Kelvin', 'c': 'Celsius', 'f': 'Fahrenheit'}
        menuHandler.menuesData['settingsMenu2_1']['temperatureDropdown']['selection'] = convert_temp[self.settings['units']['temperature']]
        menuHandler.menuesData['settingsMenu2_1']['smaDropdown']['selection'] = self.settings['units']['sma'].capitalize()
        menuHandler.menuesData['settingsMenu2_1']['lumDropdown']['selection'] = self.settings['units']['luminosity'].capitalize()
        menuHandler.menuesData['settingsMenu2_1']['prefixSetDropdown']['selection'] = self.settings['prefixSet'].capitalize()

        menuHandler.menuesData['settingsMenu2_2']['masterVolumeSlidebar']['progress'] = self.settings['master-volume']

    def SaveSettings(self):
        # align the settings with the menu items
        self.settings['invert-scroll'] = menuHandler.menuesData['settingsMenu2_0']['invertScrollCheckbutton']['selected']
        self.settings['scroll-sens'] = menuHandler.menuesData['settingsMenu2_0']['scrollSensSlidebar']['progress'] * 10
        self.settings['zoom-speed'] = menuHandler.menuesData['settingsMenu2_0']['zoomSpeedSlidebar']['progress']
        self.settings['show-moons-in-ledger'] = menuHandler.menuesData['settingsMenu2_0']['moonsLedgerCheckbutton']['selected']

        size = menuHandler.menuesData['settingsMenu2_0']['resDropdown']['selection']
        self.settings['size'] = (int(size.split('x')[0]), int(size.split('x')[1]))
        self.settings['fullscreen'] = menuHandler.menuesData['settingsMenu2_0']['fullscreenCheckbutton']['selected']

        self.frameSize = self.settings['size']
        if self.settings['fullscreen']:
            self.screen = pygame.display.set_mode(self.frameSize, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.frameSize)

        self.settings['units']['mass'] = menuHandler.menuesData['settingsMenu2_1']['massDropdown']['selection'].lower()
        self.settings['units']['radius'] = menuHandler.menuesData['settingsMenu2_1']['radiusDropdown']['selection'].lower()
        self.settings['units']['gravity'] = menuHandler.menuesData['settingsMenu2_1']['gravityDropdown']['selection'].lower()

        convert_temp = {'Kelvin': 'k', 'Celsius': 'c', 'Fahrenheit': 'f'}
        self.settings['units']['temperature'] = convert_temp[menuHandler.menuesData['settingsMenu2_1']['temperatureDropdown']['selection']]
        self.settings['units']['sma'] = menuHandler.menuesData['settingsMenu2_1']['smaDropdown']['selection'].lower()
        self.settings['units']['luminosity'] = menuHandler.menuesData['settingsMenu2_1']['lumDropdown']['selection'].lower()
        self.settings['prefixSet'] = menuHandler.menuesData['settingsMenu2_1']['prefixSetDropdown']['selection'].lower()

        self.settings['master-volume'] = menuHandler.menuesData['settingsMenu2_2']['masterVolumeSlidebar']['progress']

        for sound in self.sounds.values():
            sound.set_volume(self.settings['master-volume'])

        menuHandler.InitLedger()
        menuesToUpdate = ['settingsMenu', 
            'settingsMenu2_0', 
            'settingsMenu2_1', 
            'settingsMenu2_2', 
            'ledger', 
            'ledger2',
            'escapeMenu',
            'timeMenu'
        ]
        for menu in menuesToUpdate:
            menuHandler.UpdateMenuData(menu)

        with open(f'{path}data\\settings.dat', 'wb') as file:
            pickle.dump(self.settings, file)

        self.InitBgImage(keepImage=True)
        self.InitSystemViewBg()

    def GetMegaprojectAddData(self):
        megaprojectType = physicsEngine.megaprojectsData[self.megaprojectToAdd]['type']
        if megaprojectType == 'add_substance':
            weeklyAmount = 0.0001 * physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'mass') #0.01%
            if 'addMegaprojectMenu2' in menuHandler.currentMenues:
                text1 = menuHandler.menuesData['addMegaprojectMenu2']['totalAmountInput1']['text']
                text2 = menuHandler.menuesData['addMegaprojectMenu2']['totalAmountInput2']['text']
                if text1 == '' or text2 == '':
                    return None
                totalAmountToAdd = float(text1) * 10 ** int(text2)
            else:
                text = menuHandler.menuesData['addMegaprojectMenu3']['totalAmountInput']['text']
                if text == '':
                    return None
                substance = physicsEngine.megaprojectsData[game.megaprojectToAdd]['effects']
                substanceId = physicsEngine.const.substanceIdByKey[substance]
                totalSubstanceAmount = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'total-substances')[substanceId]
                totalAmountToAdd = float(text)/100 * totalSubstanceAmount

            if weeklyAmount > totalAmountToAdd:
                weeklyAmount = totalAmountToAdd
            if weeklyAmount == 0:
                weeklyAmount = 1
            time = math.ceil(totalAmountToAdd / weeklyAmount)
            return [self.megaprojectToAdd, True, 0, time, weeklyAmount]
        return None

    def SaveGame(self):
        filename = menuHandler.menuesData['savegamesMenuSave']['input']['text']
        if filename[-4:] == '.dat':
            filename = filename[:-4]
        toSave = [
            physicsEngine.systemsData,
            self.time
        ]
        with open(f'{path}savegames\\{filename}.dat', 'wb') as file:
            pickle.dump(toSave, file)

    def ResetGame(self):
        physicsEngine.Reset()
        self.time = 104001 #number of weeks after year 0. 104000 weeks is 2000 years

    def Commands(self, ID_args):
        ID = ID_args.split()[0]

        if ID == 'quitGame':
            pygame.quit()
            quit()

        elif ID == 'time_clicked':
            self.timeState = not self.timeState
            if self.timeState:
                self.frameTimeCounter = int(self.times[self.timeSpeed]/2) #when unpaused, you become halfway towards a new timetick
            else:
                self.frameTimeCounter = 0 #when paused, set counter to 0
            menuHandler.UpdateMenuData('timeMenu')

        elif ID == 'time_minus':
            if self.timeSpeed > 0:
                self.timeSpeed -= 1

        elif ID == 'time_plus':
            if self.timeSpeed < 4:
                self.timeSpeed += 1

        elif ID == 'close_small_planet_menu_planet':
            menuHandler.RemoveMenu('smallPlanetMenu')
            self.smallPlanetMenuPlanet = None

        elif ID == 'open_planet_menu_from_small':
            self.Commands(f'open_planet_menu {self.smallPlanetMenuPlanet}')
            self.Commands('close_small_planet_menu_planet')

        elif ID == 'enterSavegamesMenu':
            menuHandler.InitSavegamesMenu()
            menuHandler.RemoveMenu('playMenu')
            menuHandler.AddMenu('savegamesMenu')
            menuHandler.AddMenu('savegamesMenu2')

        elif ID == 'exitSavegamesMenu':
            menuHandler.RemoveMenu('savegamesMenu')
            menuHandler.RemoveMenu('savegamesMenu2')
            menuHandler.AddMenu('playMenu')

        elif ID == 'enterSavegamesMenuSave':
            menuHandler.InitSavegamesMenuSave()
            menuHandler.RemoveMenu('escapeMenu')
            menuHandler.AddMenu('savegamesMenuSave')
            menuHandler.AddMenu('savegamesMenu2')

        elif ID[:24] == 'savegamesMenuSaveClicked':
            item = ID_args.split()[1]
            menuHandler.menuesData['savegamesMenuSave']['input']['text'] = \
            menuHandler.menuesData['savegamesMenu2']['treeview']['items'][item]['text']

        elif ID == 'exitSavegamesMenuSave':
            menuHandler.RemoveMenu('savegamesMenuSave')
            menuHandler.RemoveMenu('savegamesMenu2')
            menuHandler.AddMenu('escapeMenu')

        elif ID == 'save_game':
            if menuHandler.menuesData['savegamesMenuSave']['input']['colour'] == (255, 255, 255):
                self.SaveGame()
                self.Commands('exitSavegamesMenuSave')

        elif ID == 'load_game':
            selectedItem = menuHandler.menuesData['savegamesMenu2']['treeview']['selectedItem']
            filename = menuHandler.menuesData['savegamesMenu2']['treeview']['items'][selectedItem]['text']
            with open(f'{path}savegames\\{filename}', 'rb') as file:
                loadedData = pickle.load(file)
            physicsEngine.systemsData = loadedData[0]
            self.time = loadedData[1]
            self.currentSystem = list(physicsEngine.systemsData.keys())[0] #make the current system to the first system in the data.
            # insert file validation here
            menuHandler.RemoveMenu('savegamesMenu')
            menuHandler.RemoveMenu('savegamesMenu2')
            self.Commands('enterSystemView')

        elif ID == 'enterSettingsMenu':

            menuHandler.RemoveMenu('mainMenu')
            menuHandler.AddMenu('settingsMenu')
            menuHandler.AddMenu('settingsMenu2_'+str(self.settingsMenuTabSelection))

        elif ID == 'playButton':
            menuHandler.RemoveMenu('mainMenu')
            menuHandler.AddMenu('playMenu')

        elif ID == 'playMenuBack':
            menuHandler.RemoveMenu('playMenu')
            menuHandler.AddMenu('mainMenu')

        elif ID == 'enterSystemView':
            self.view = 'system'
            self.ChangeSystem(self.currentSystem)
            menuHandler.RemoveMenu('playMenu')
            menuHandler.AddMenu('ledger')
            menuHandler.AddMenu('ledger2')
            menuHandler.AddMenu('timeMenu')
            self.InitSystemViewBg()

        elif ID == 'systemGalaxySwitch':
            if self.view == 'galaxy':
                self.Commands('enterSystemView')
            else: # system
                self.view = 'galaxy'
                self.smallPlanetMenuPlanet = None
                menuHandler.RemoveMenu('smallPlanetMenu')

        elif ID == 'megaprojects_search':
            menuHandler.InitMegaprojectMenues()
            menuHandler.UpdateMenuData('megaprojects2')

        elif ID == 'remove_megaproject':
            toRemove = ID_args.split()[1]
            for i, megaproject in enumerate(physicsEngine.GetProperty(self.currentSystem, self.planetMenuPlanet, 'megaprojects')):
                if megaproject[0] == toRemove:
                    physicsEngine.systemsData[self.currentSystem]['planets'][self.planetMenuPlanet]['megaprojects'].pop(i)
                    break
            menuHandler.InitMegaprojectMenues()
            menuHandler.UpdateMenuData('megaprojects2')

        elif ID == 'close_add_megaproject_menu':
            menuHandler.RemoveMenu('addMegaprojectMenu')
            menuHandler.RemoveMenu('addMegaprojectMenu2')
            menuHandler.RemoveMenu('addMegaprojectMenu3')

        elif ID == 'add_megaproject':
            megaprojectData = self.GetMegaprojectAddData()
            if megaprojectData != None:
                physicsEngine.systemsData[self.currentSystem]['planets'][self.planetMenuPlanet]['megaprojects'].append(megaprojectData)
            
                menuHandler.InitMegaprojectMenues()
                menuHandler.UpdateMenuData('megaprojects1')
                menuHandler.UpdateMenuData('megaprojects2')
                menuHandler.UpdateMenuData('planetMenu2Megaprojects')
                menuHandler.RemoveMenu('addMegaprojectMenu')
                menuHandler.RemoveMenu('addMegaprojectMenu2')
                menuHandler.RemoveMenu('addMegaprojectMenu3')

        elif ID == 'add_megaproject_menu':

            self.megaprojectToAdd = ID_args.split()[1]
            menuHandler.AddMenu('addMegaprojectMenu')
            menuHandler.AddMenu('addMegaprojectMenu2')

        elif ID == 'change_add_megaproject_input_type':
            if 'addMegaprojectMenu2' in menuHandler.currentMenues:
                menuHandler.RemoveMenu('addMegaprojectMenu2')
                menuHandler.AddMenu('addMegaprojectMenu3')
            else:
                menuHandler.RemoveMenu('addMegaprojectMenu3')
                menuHandler.AddMenu('addMegaprojectMenu2')

        elif ID == 'pause_megaproject':
            toPause = ID_args.split()[1]
            for i, megaproject in enumerate(physicsEngine.GetProperty(self.currentSystem, self.planetMenuPlanet, 'megaprojects')):
                if megaproject[0] == toPause:
                    physicsEngine.systemsData[self.currentSystem]['planets'][self.planetMenuPlanet]['megaprojects'][i][1] = \
                    not physicsEngine.systemsData[self.currentSystem]['planets'][self.planetMenuPlanet]['megaprojects'][i][1]
                    break
            menuHandler.InitMegaprojectMenues()
            menuHandler.UpdateMenuData('megaprojects1')
            

        elif ID == 'planetMenu2Switch':
            arg = ID_args.split()[1]
            planetType = physicsEngine.GetProperty(self.currentSystem, self.planetMenuPlanet, 'type')

            toRemove = [
                'planetMenu2Physics',
                'planetMenu2Orbit',
                'planetMenu2Atmosphere',
                'planetMenu2Atmosphere2',
                'planetMenu2Atmosphere3',
                'planetMenu2Atmosphere4',
                'planetMenu2AtmosphereSwitch',
                'planetMenu2Soil',
                'planetMenu2PhysicsGasGiant',
                'planetMenu2PhysicsStar',
                'planetMenu2Megaprojects',
                'megaprojects1',
                'megaprojects2'
            ]
            for menu in toRemove:
                menuHandler.RemoveMenu(menu)

            if arg == 'physics':
                menuHandler.menuesData['planetMenu2']['bg']['imageID'] = 'planet_menu2'
                menuHandler.UpdateMenuData('planetMenu2')
                if planetType == 'terrestrial':
                    menuHandler.InitPlanetAtmMenu()
                    menuHandler.AddMenu('planetMenu2Physics')
                    menuHandler.AddMenu('planetMenu2Orbit')
                    menuHandler.AddMenu(menuHandler.planetMenu2AtmosphereMenu)
                    menuHandler.AddMenu('planetMenu2AtmosphereSwitch')
                    menuHandler.AddMenu('planetMenu2Soil')
                elif planetType == 'gas-giant':
                    menuHandler.AddMenu('planetMenu2PhysicsGasGiant')
                    menuHandler.AddMenu('planetMenu2Orbit')
                elif planetType == 'star':
                    menuHandler.AddMenu('planetMenu2PhysicsStar')

            elif arg == 'megaprojects':
                menuHandler.menuesData['planetMenu2']['bg']['imageID'] = 'planet_menu3'
                menuHandler.UpdateMenuData('planetMenu2')
                menuHandler.InitMegaprojectMenues()
                menuHandler.AddMenu('planetMenu2Megaprojects')
                menuHandler.AddMenu('megaprojects1')
                menuHandler.AddMenu('megaprojects2')

        elif ID == 'switch_planetMenu2Atmosphere':
            menues = ['planetMenu2Atmosphere', 'planetMenu2Atmosphere2', 'planetMenu2Atmosphere3', 'planetMenu2Atmosphere4']
            currentMenu = menues.index(menuHandler.planetMenu2AtmosphereMenu)
            currentMenu += 1
            if len(menues) == currentMenu:
                currentMenu -= len(menues)
            menuHandler.planetMenu2AtmosphereMenu = menues[currentMenu]
            self.Commands('planetMenu2Switch physics') #refresh

        elif ID == 'open_planet_menu':
            if 'planetMenu' in menuHandler.currentMenues:
                self.Commands('close_planet_menu')
            self.planetMenuPlanet = ID_args.split()[1]
            planetType = physicsEngine.GetProperty(self.currentSystem, self.planetMenuPlanet, 'type')
            
            menuHandler.InitPlanetSummary()
            menuHandler.InitMoonsMenu()

            menuHandler.AddMenu('planetMenu')
            menuHandler.AddMenu('planetMenuSummary')
            menuHandler.AddMenu('planetMenuMoons')
            menuHandler.AddMenu('planetMenuMoons2')
            menuHandler.AddMenu('planetMenuOrbit')
            menuHandler.AddMenu('planetMenu2')
            menuHandler.AddMenu('planetMenuButtons')
            self.Commands('planetMenu2Switch physics')
            if planetType == 'terrestrial':
                menuHandler.AddMenu('landscapesMenu')
            elif planetType == 'star' or planetType == 'gas-giant':
                menuHandler.AddMenu('landscapesMenu2')


        elif ID == 'close_planet_menu':
            self.planetMenuPlanet = None

            toRemove = [
                'planetMenu',
                'planetMenuSummary',
                'planetMenuMoons',
                'planetMenuOrbit',
                'planetMenu2',
                'planetMenu2Physics',
                'planetMenu2Orbit',
                'planetMenuMoons2',
                'planetMenu2Atmosphere',
                'planetMenu2Atmosphere2',
                'planetMenu2Atmosphere3',
                'planetMenu2Atmosphere4',
                'planetMenu2AtmosphereSwitch',
                'planetMenu2Soil',
                'landscapesMenu',
                'landscapesMenu2',
                'planetMenu2PhysicsGasGiant',
                'planetMenu2PhysicsStar',
                'planetMenuButtons',
                'planetMenu2Megaprojects',
                'megaprojects1',
                'megaprojects2'
            ]

            for menu in toRemove:
                menuHandler.RemoveMenu(menu)

        elif ID == 'enterEscapeMenu':
            for menu in menuHandler.currentMenues:
                menuHandler.removedMenues.append(menu)
                menuHandler.interactiveMenues.remove(menu)
            menuHandler.AddMenu('escapeMenu')

        elif ID == 'exitEscapeMenu':
            menuHandler.RemoveMenu('escapeMenu')
            for menu in menuHandler.removedMenues.copy():
                menuHandler.removedMenues.remove(menu)
                menuHandler.interactiveMenues.append(menu)

        elif ID == 'exitToMenu':
            self.view = 'mainMenu'
            for menu in menuHandler.currentMenues.copy(): #remove every menu
                menuHandler.RemoveMenu(menu)
            menuHandler.AddMenu('mainMenu')
            self.InitBgImage()
            self.ResetGame()

        elif ID == 'update_savegames_input':
            text = menuHandler.menuesData['savegamesMenuSave']['input']['text']
            if DataHandler.TextValidation.LettersOnly(text):
                menuHandler.menuesData['savegamesMenuSave']['input']['colour'] = (255, 255, 255)
            else:
                menuHandler.menuesData['savegamesMenuSave']['input']['colour'] = (255, 0, 0)


        elif ID == 'add_megaprojects_input':
            menu = int(ID_args.split()[1])
            if menu != 3:
                text1 = menuHandler.menuesData['addMegaprojectMenu2']['totalAmountInput1']['text']
                text2 = menuHandler.menuesData['addMegaprojectMenu2']['totalAmountInput2']['text']

                if DataHandler.TextValidation.Numbers(text1, allow_negative=True, lower_limit = -10, upper_limit=10):
                    menuHandler.menuesData['addMegaprojectMenu2']['totalAmountInput1']['colour'] = (255, 255, 255)
                else:
                    menuHandler.menuesData['addMegaprojectMenu2']['totalAmountInput1']['colour'] = (255, 0, 0)
                if DataHandler.TextValidation.Numbers(text2, allow_negative=False, lower_limit=1, upper_limit=24):
                    menuHandler.menuesData['addMegaprojectMenu2']['totalAmountInput2']['colour'] = (255, 255, 255)
                else:
                    menuHandler.menuesData['addMegaprojectMenu2']['totalAmountInput2']['colour'] = (255, 0, 0)

                totalSubstances = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'total-substances')
                substance = physicsEngine.megaprojectsData[self.megaprojectToAdd]['effects']
                substanceMass = totalSubstances[physicsEngine.const.substanceIdByKey[substance]]
                if menuHandler.menuesData['addMegaprojectMenu2']['totalAmountInput1']['colour'] == (255, 255, 255) and text1 != '' and \
                    menuHandler.menuesData['addMegaprojectMenu2']['totalAmountInput2']['colour'] == (255, 255, 255) and text2 != '': #both valid
                    menuHandler.UpdateAddMegaprojectsMenu()
                    if float(text1) * 10**(int(text2)) < -substanceMass:
                        menuHandler.menuesData['addMegaprojectMenu2']['totalAmountInput1']['colour'] = (255, 0, 0)
                        menuHandler.menuesData['addMegaprojectMenu2']['totalAmountInput2']['colour'] = (255, 0, 0)
                else:
                    menuHandler.menuesData['addMegaprojectMenu']['weeklyAmount']['text'] = 'Weekly Amount: ??? kg'
                    menuHandler.menuesData['addMegaprojectMenu']['time']['text'] = 'Time: ??? weeks'
                    menuHandler.menuesData['addMegaprojectMenu']['effectsClarification']['text'] = '??? Temperature change'
            else:
                text = menuHandler.menuesData['addMegaprojectMenu3']['totalAmountInput']['text']
                if DataHandler.TextValidation.Numbers(text, allow_negative=True, lower_limit = -100, upper_limit=100) and text != '':
                    menuHandler.menuesData['addMegaprojectMenu3']['totalAmountInput']['colour'] = (255, 255, 255)
                    menuHandler.UpdateAddMegaprojectsMenu()
                else:
                    menuHandler.menuesData['addMegaprojectMenu3']['totalAmountInput']['colour'] = (255, 0, 0)

                    menuHandler.menuesData['addMegaprojectMenu']['weeklyAmount']['text'] = 'Weekly Amount: ??? kg'
                    menuHandler.menuesData['addMegaprojectMenu']['time']['text'] = 'Time: ??? weeks'
                    menuHandler.menuesData['addMegaprojectMenu']['effectsClarification']['text'] = '??? Temperature change'



        elif ID == 'settingsMenu_tab':
            self.settingsMenuTabSelection = int(ID_args.split()[1])-1
            for i in range(3):
                menuHandler.RemoveMenu('settingsMenu2_'+str(i))
            menuHandler.AddMenu('settingsMenu2_'+str(self.settingsMenuTabSelection))

        elif ID == 'exitSettingsMenu':
            menuesToRemove = ['settingsMenu', 'settingsMenu2_0', 'settingsMenu2_1', 'settingsMenu2_2']
            for menu in menuesToRemove:
                menuHandler.RemoveMenu(menu)
            if self.view == 'mainMenu':
                menuHandler.AddMenu('mainMenu')

        elif ID == 'applySettings':
            self.SaveSettings()

        elif ID == 'okSettings':
            self.SaveSettings()
            self.Commands('exitSettingsMenu')

        elif ID == 'enterCreditsMenu':
            menuHandler.RemoveMenu('mainMenu')
            menuHandler.AddMenu('creditsMenu')

        elif ID == 'backCredits':
            menuHandler.AddMenu('mainMenu')
            menuHandler.RemoveMenu('creditsMenu')


class MenuHandler():
    def __init__(self):
        with open(path+'data\\menues.dat', 'rb') as file:
            self.menuesData = pickle.load(file)

        with open(path+'data\\hoverMenu.dat', 'rb') as file:
            self.hoverMenuData = pickle.load(file)

        self.currentMenuesData = {}
        self.currentMenues = []
        self.interactiveMenues = []
        self.removedMenues = [] # all menues removed when escapemenu is entered
        self.selectedSlidebar = None
        self.selectedSlidebarOrientation = 'horizontal'
        self.planetMenu2AtmosphereMenu = 'planetMenu2Atmosphere' # which menu here is currently viewed.

    def InitSavegamesMenu(self):
        os.chdir(f'{path}savegames\\')
        files = os.listdir(os.getcwd())

        for i, filename in enumerate(files):
            self.menuesData['savegamesMenu2']['treeview']['items'][f'item{i}'] = {
                'text': filename,
                'textColour': (255, 255, 255),
                'side': 'left',
                'indents': 0,
                'downTabbed': False
            }
        if len(files) == 0:
            i = 0
            self.menuesData['savegamesMenu2']['treeview']['selectedItem'] = None
        else:
            self.menuesData['savegamesMenu2']['treeview']['selectedItem'] = 'item0'
        self.menuesData['savegamesMenu2']['maxScroll'] = -(i+1)*35+240
        self.menuesData['savegamesMenu2']['treeview']['selectionCommand'] = None


    def InitSavegamesMenuSave(self):
        self.InitSavegamesMenu()
        self.menuesData['savegamesMenu2']['maxScroll'] = self.menuesData['savegamesMenu2']['maxScroll']-35
        self.menuesData['savegamesMenu2']['size'] = (600, self.menuesData['savegamesMenu2']['size'][1]-35)
        self.menuesData['savegamesMenu2']['treeview']['selectedItem'] = None
        self.menuesData['savegamesMenu2']['treeview']['selectionCommand'] = 'savegamesMenuSaveClicked'


    def InitLedger(self):
        if game.view != 'system':
            return
        toDelete = []
        for item in self.menuesData['ledger2']:
            if item[:7] == 'button_' or item[:10] == 'planetPic_' or item[:11] == 'planetText_' or item[:12] == 'planetText2_':
                toDelete.append(item)
        for item in toDelete:
            del self.menuesData['ledger2'][item]

        planetTypes = {
            'terrestrial': 'Terrestrial World',
            'gas-giant': 'Gas giant',
            'star': 'Star'
        }
        addedPlanets = 0
        for i, (key, planet) in enumerate(physicsEngine.systemsData[game.currentSystem]['planets'].items()):
            #IMPLY logic gate
            if (physicsEngine.IsMoon(game.currentSystem, key) == game.settings['show-moons-in-ledger']) or game.settings['show-moons-in-ledger']:
                self.menuesData['ledger2']['button_'+key] = {
                    'type': 'button',
                    'imageID': 'ledger_planet_button',
                    'hoverImageID': 'ledger_planet_button_hover',
                    'clickImageID': 'ledger_planet_button_click',
                    'text': None,
                    'font': 'Arial',
                    'fontSize': 20,
                    'colour': (255, 255, 255),
                    'hoverColour': (255, 255, 255),
                    'clickColour': (255, 255, 255),
                    'command': 'open_planet_menu '+key,
                    'state': 0,
                    'pos': (10, addedPlanets*45),
                    'crop': (0, 0, 200, 40)
                }
                self.menuesData['ledger2']['planetPic_'+key] = {
                    'type': 'image',
                    'imageID': planet['image'],
                    'pos': (20, 5+addedPlanets*45),
                    'crop': (0, 0, 30, 30),
                    'resize': (30, 30)
                }
                self.menuesData['ledger2']['planetText_'+key] = {
                    'type': 'text',
                    'text': planet['name'],
                    'font': '/value defaultFont bold',
                    'fontSize': 18,
                    'pos': (60, 4+addedPlanets*45),
                    'anchor': 'w',
                    'wrapLines': False,
                    'wordwrapJustification': 'c', #w eller c
                    'crop': (0, 0, 120, 30),
                    'textColour': (255, 255, 255),
                    'bgColour': None
                }
                self.menuesData['ledger2']['planetText2_'+key] = {
                    'type': 'text',
                    'text': planetTypes[planet['type']],
                    'font': '/value defaultFont bold',
                    'fontSize': 14,
                    'pos': (60, 21+addedPlanets*45),
                    'anchor': 'w',
                    'wrapLines': False,
                    'wordwrapJustification': 'c', #w eller c
                    'crop': (0, 0, 120, 30),
                    'textColour': (255, 255, 255),
                    'bgColour': None
                }
                addedPlanets += 1
        self.menuesData['ledger2']['maxScroll'] = 359-addedPlanets*45 #359 is the length of the menu. There are 8 objects shown in the ledger, and 45 pixels/object


    def InitMoonsMenu(self):
        toDelete = []
        for item in self.menuesData['planetMenuMoons2']:
            if item[:7] == 'button_' or item[:10] == 'planetPic_' or item[:11] == 'planetText_':
                toDelete.append(item)
        for item in toDelete:
            del self.menuesData['planetMenuMoons2'][item]

        self.menuesData['planetMenuMoons2']['scroll'] = 0
        self.menuesData['planetMenuMoons2']['scrollQueue'] = []


        addedPlanets = 0
        for i, (key, planet) in enumerate(physicsEngine.systemsData[game.currentSystem]['planets'].items()):
            if planet['host'] == game.planetMenuPlanet:
                self.menuesData['planetMenuMoons2']['button_'+key] = {
                    'type': 'button',
                    'imageID': 'moons_menu_button',
                    'hoverImageID': 'moons_menu_button_hover',
                    'clickImageID': 'moons_menu_button_click',
                    'text': None,
                    'font': 'Arial',
                    'fontSize': 20,
                    'colour': (255, 255, 255),
                    'hoverColour': (255, 255, 255),
                    'clickColour': (255, 255, 255),
                    'command': 'open_planet_menu '+key,
                    'state': 0,
                    'pos': (5, addedPlanets*45),
                    'crop': (0, 0, 200, 40)
                }
                self.menuesData['planetMenuMoons2']['planetPic_'+key] = {
                    'type': 'image',
                    'imageID': planet['image'],
                    'pos': (10, 5+addedPlanets*45),
                    'crop': (0, 0, 30, 30),
                    'resize': (30, 30)
                }
                self.menuesData['planetMenuMoons2']['planetText_'+key] = {
                    'type': 'text',
                    'text': planet['name'],
                    'font': '/value defaultFont bold',
                    'fontSize': 18,
                    'pos': (50, 10+addedPlanets*45),
                    'anchor': 'w',
                    'wrapLines': False,
                    'wordwrapJustification': 'c', #w eller c
                    'crop': (0, 0, 65, 30),
                    'textColour': (255, 255, 255),
                    'bgColour': None
                }
                addedPlanets += 1
        self.menuesData['planetMenuMoons2']['maxScroll'] = -addedPlanets*45+234


    def SortSubstances(self, substances):
        substanceNames = physicsEngine.const.substancesNames
        sortedSubstances = []
        sortedSubstanceNames = []
        for i in range(8): #8 fractions
            appended = False
            for j in range(len(sortedSubstances)):
                if substances[i] < sortedSubstances[j]:
                    appended = True
                    sortedSubstances.insert(j, substances[i])
                    sortedSubstanceNames.insert(j, substanceNames[i])
                    break
            if not appended:
                sortedSubstances.append(substances[i])
                sortedSubstanceNames.append(substanceNames[i])

        sortedSubstances.reverse()
        sortedSubstanceNames.reverse()
        return sortedSubstances, sortedSubstanceNames


    def InitPlanetAtmMenu(self):
        # AMT COMP MENU
        fractions = physicsEngine.GetAtmFractions(game.currentSystem, game.planetMenuPlanet)
        sortedFractions, sortedSubstanceNames = self.SortSubstances(fractions)

        textFractions = []
        for i in range(8):
            if sortedFractions[i] > 0.0001:
                textFractions.append(str(round(sortedFractions[i]*100, 2))+'%')
            elif sortedFractions[i] > 10**-6:
                text = '{:.6f}'.format(DataHandler.RoundSignificantFigures(sortedFractions[i]*100, 2)) #because 0.0000001 is supposed to be '0.0000001', not '1e-7'
                while text[-1] == '0': #remove zeroes at the end of the string
                    text = text[:-1]
                textFractions.append(text+'%') 
            else:
                textFractions.append('0%')

        for i in range(8):
            self.menuesData['planetMenu2Atmosphere']['treeview2']['items']['item'+str(i)] = {
                'text': sortedSubstanceNames[i],
                'textColour': (255, 255, 255),
                'side': 'left',
                'indents': 0,
                'downTabbed': False
            }
            self.menuesData['planetMenu2Atmosphere']['treeview2']['items']['item'+str(i)+'right'] = {
                'text': textFractions[i],
                'textColour': (255, 255, 255),
                'side': 'right',
                'indents': 0,
                'downTabbed': False
            }


        # TOTAL SUBSTANCES MENU
        totalSubstances = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'total-substances')
        sortedTotalSubstances, sortedSubstanceNames = self.SortSubstances(totalSubstances)

        for i in range(8):
            if game.settings['units']['mass'] == 'prefix': 
                text = DataHandler.NumberPrefix(sortedTotalSubstances[i], 3, True, game.settings['prefixSet'])+[' ', ''][game.settings['prefixSet'] == 'unit']+'kg'
            else:
                text = DataHandler.ScientificNotation(sortedTotalSubstances[i], 2)+'kg'
            self.menuesData['planetMenu2Atmosphere2']['treeview1']['items']['item'+str(i)] = {
                'text': sortedSubstanceNames[i],
                'textColour': (255, 255, 255),
                'side': 'left',
                'indents': 0,
                'downTabbed': False
            }
            self.menuesData['planetMenu2Atmosphere2']['treeview1']['items']['item'+str(i)+'right'] = {
                'text': text,
                'textColour': (255, 255, 255),
                'side': 'right',
                'indents': 0,
                'downTabbed': False
            }


        # ON GROUND MENU
        onGround = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'on-ground')
        sortedOnGround, sortedSubstanceNames = self.SortSubstances(onGround)

        for i in range(8):
            if game.settings['units']['mass'] == 'prefix': 
                text = DataHandler.NumberPrefix(sortedOnGround[i], 3, True, game.settings['prefixSet'])+[' ', ''][game.settings['prefixSet'] == 'unit']+'kg'
            else:
                text = DataHandler.ScientificNotation(sortedOnGround[i], 2)+'kg'

            self.menuesData['planetMenu2Atmosphere3']['treeview1']['items']['item'+str(i)] = {
                'text': sortedSubstanceNames[i],
                'textColour': (255, 255, 255),
                'side': 'left',
                'indents': 0,
                'downTabbed': False
            }
            self.menuesData['planetMenu2Atmosphere3']['treeview1']['items']['item'+str(i)+'right'] = {
                'text': text,
                'textColour': (255, 255, 255),
                'side': 'right',
                'indents': 0,
                'downTabbed': False
            }


        # IN ATMOSPHERE MENU
        inAtmosphere = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'in-atmosphere')
        sortedInAtmosphere, sortedSubstanceNames = self.SortSubstances(inAtmosphere)

        for i in range(8):
            if game.settings['units']['mass'] == 'prefix': 
                text = DataHandler.NumberPrefix(sortedInAtmosphere[i], 3, True, game.settings['prefixSet'])+[' ', ''][game.settings['prefixSet'] == 'unit']+'kg'
            else:
                text = DataHandler.ScientificNotation(sortedInAtmosphere[i], 2)+'kg'

            self.menuesData['planetMenu2Atmosphere4']['treeview1']['items']['item'+str(i)] = {
                'text': sortedSubstanceNames[i],
                'textColour': (255, 255, 255),
                'side': 'left',
                'indents': 0,
                'downTabbed': False
            }
            self.menuesData['planetMenu2Atmosphere4']['treeview1']['items']['item'+str(i)+'right'] = {
                'text': text,
                'textColour': (255, 255, 255),
                'side': 'right',
                'indents': 0,
                'downTabbed': False
            }


    def InitPlanetSummary(self):
        done = False
        i=0
        while not done:
            try:
                del self.menuesData['planetMenuSummary']['text'+str(i)]
            except:
                done = True
            i+=1
        summary = physicsEngine.GeneratePlanetSummary(game.currentSystem, game.planetMenuPlanet)
        font = self.GetFont(self.Values('/value defaultFont bold'), 16)
        textsPlacedInColumn = 0
        xpos = [10, 135]
        extraYPos = 0
        wentToRightSide = False # becomes true when the left side of the planet summary is filled
        for i, text in enumerate(summary):
            if 50 + 30*textsPlacedInColumn + extraYPos > 246: #time to switch column
                wentToRightSide = True
                textsPlacedInColumn = 0
                extraYPos = 0

            self.menuesData['planetMenuSummary']['text'+str(i)] = {
                'type': 'text',
                'text': text,
                'font': '/value defaultFont bold',
                'fontSize': 16,
                'pos': (xpos[int(wentToRightSide)], 50 + 30*textsPlacedInColumn + extraYPos),
                'anchor': 'w',
                'wrapLines': True,
                'wordwrapJustification': 'w', #w eller c
                'crop': (0, 0, 110, 300),
                'textColour': (255, 255, 255),
                'bgColour': None
            }

            textXSize = font.size(text)[0]
            amountOfWraps = len(self.WrapLine(text, font, 110)) - 1
            extraYPos += font.size(text)[1] * amountOfWraps
            textsPlacedInColumn+=1


    def CreateMegaprojectData(self, menu, i, megaproject):
        ''' 
        Internal function for InitMegaprojectMenues 
        Adds data to the megaproject menues.
        There are two similar megaproject menues, that is why this function is used
        '''

        if menu == 'megaprojects1':
            megaprojectID = megaproject[0]
        else:
            megaprojectID = megaproject

        self.menuesData[menu][f'bg{i}'] = {
            'type': 'image',
            'imageID': 'megaprojects_bg',
            'pos': (0, 125*i),
            'crop': (0, 0, 420, 120)
        }

        image = physicsEngine.megaprojectsData[megaprojectID]['image']
        self.menuesData[menu][f'icon{i}'] = {
            'type': 'image',
            'imageID': image,
            'pos': (10, 10+125*i),
            'crop': (0, 0, 100, 100)
        }

        title = physicsEngine.megaprojectsData[megaprojectID]['title']
        self.menuesData[menu][f'title{i}'] = {
            'type': 'text',
            'text': title,
            'font': '/value defaultFont bold',
            'fontSize': 20,
            'pos': (120, 12+125*i),
            'anchor': 'w',
            'wrapLines': False,
            'wordwrapJustification': 'c', #w eller c
            'crop': (0, 0, 300, 300),
            'textColour': (255, 255, 255),
            'bgColour': None
        }

        if physicsEngine.megaprojectsData[megaprojectID]['type'] == 'add_substance':
            substance = physicsEngine.megaprojectsData[megaprojectID]['effects']
            if menu == 'megaprojects1':
                desc = f"Changes the amount of {physicsEngine.const.substanceNameByKey[substance].lower()}."
            else:
                desc = f"Changes the amount of {physicsEngine.const.substanceNameByKey[substance].lower()}, its form is determined by planet temperature."

        else:
            desc = physicsEngine.megaprojectsData[megaprojectID]['desc']
        self.menuesData[menu][f'desc{i}'] = {
            'type': 'text',
            'text': desc,
            'font': '/value defaultFont bold',
            'fontSize': 16,
            'pos': (120, 35+125*i),
            'anchor': 'w',
            'wrapLines': True,
            'wordwrapJustification': 'w', #w eller c
            'crop': (0, 0, 260, 300),
            'textColour': (255, 255, 255),
            'bgColour': None
        }

        if menu == 'megaprojects1':
            self.menuesData[menu][f'closeButton{i}'] = {
                'type': 'button',
                'imageID': '24x24_cross',
                'hoverImageID': '24x24_cross_hover',
                'clickImageID': '24x24_cross_click',
                'text': '',
                'font': '/value defaultFont bold',
                'fontSize': 20,
                'colour': (255, 255, 255),
                'hoverColour': (255, 255, 255),
                'clickColour': (255, 255, 255),
                'command': f'remove_megaproject {megaprojectID}',
                'state': 0,
                'pos': (376, 4+i*125),
                'crop': (0, 0, 24, 24)
            }

            if megaproject[1]:
                imageIDS = ['24x24_pause', '24x24_pause_hover', '24x24_pause_click']
            else:
                imageIDS = ['24x24_play', '24x24_play_hover', '24x24_play_click']
            self.menuesData[menu][f'pauseButton{i}'] = {
                'type': 'button',
                'imageID': imageIDS[0],
                'hoverImageID': imageIDS[1],
                'clickImageID': imageIDS[2],
                'text': '',
                'font': '/value defaultFont bold',
                'fontSize': 20,
                'colour': (255, 255, 255),
                'hoverColour': (255, 255, 255),
                'clickColour': (255, 255, 255),
                'command': f'pause_megaproject {megaprojectID}',
                'state': 0, #1 för hover, 2 för nedtryckt, 0 för inget
                'pos': (376, 34+i*125),
                'crop': (0, 0, 24, 24)
            }

            text = 'Active' if megaproject[1] else 'Paused'
            self.menuesData[menu][f'activeText{i}'] = {
                'type': 'text',
                'text': text,
                'font': '/value defaultFont bold',
                'fontSize': 16,
                'pos': (120, 55+125*i),
                'anchor': 'w',
                'wrapLines': False,
                'wordwrapJustification': 'c', #w eller c
                'crop': (0, 0, 300, 300),
                'textColour': (255, 255, 255),
                'bgColour': None
            }

            if megaproject[3] == 0: # this megaproject is indefinite
                text = 'Indefinite'
            else:
                text = f'{round(megaproject[2]/megaproject[3]*100)}%, finishes on {DataHandler.GetDate(megaproject[3]+game.time-megaproject[2])}'
            self.menuesData[menu][f'finishText{i}'] = {
                'type': 'text',
                'text': text,
                'font': '/value defaultFont bold',
                'fontSize': 16,
                'pos': (120, 75+125*i),
                'anchor': 'w',
                'wrapLines': False,
                'wordwrapJustification': 'c', #w eller c
                'crop': (0, 0, 300, 300),
                'textColour': (255, 255, 255),
                'bgColour': None
            }

            text = 'effectsText not found'
            megaprojectType = physicsEngine.megaprojectsData[megaprojectID]['type']
            if megaprojectType == 'add_substance':
                substance = physicsEngine.megaprojectsData[megaproject[0]]['effects']
                text = f"{DataHandler.ScientificNotation(megaproject[4], 2)} kg {substance} weekly."

            self.menuesData[menu][f'effectsText{i}'] = {
                'type': 'text',
                'text': text,
                'font': '/value defaultFont bold',
                'fontSize': 16,
                'pos': (120, 95+125*i),
                'anchor': 'w',
                'wrapLines': False,
                'wordwrapJustification': 'c', #w eller c
                'crop': (0, 0, 300, 300),
                'textColour': (255, 255, 255),
                'bgColour': None
            }

        else:
            self.menuesData[menu][f'addButton{i}'] = {
                'type': 'button',
                'imageID': '24x24_plus',
                'hoverImageID': '24x24_plus_hover',
                'clickImageID': '24x24_plus_click',
                'text': '',
                'font': '/value defaultFont bold',
                'fontSize': 20,
                'colour': (255, 255, 255),
                'hoverColour': (255, 255, 255),
                'clickColour': (255, 255, 255),
                'command': f'add_megaproject_menu {megaprojectID}',
                'state': 0,
                'pos': (376, 4+i*125),
                'crop': (0, 0, 24, 24)
            }


    def InitMegaprojectMenues(self):
        system = game.currentSystem
        planet = game.planetMenuPlanet

        for item in self.menuesData['megaprojects2'].copy():
            if item != 'size' and item != 'pos' and item != 'scroll' and item != 'linkedScrollbar':
                del self.menuesData['megaprojects2'][item]
        self.menuesData['megaprojects2']['scroll'] = 0
        self.menuesData['megaprojects2']['scrollQueue'] = []

        for item in self.menuesData['megaprojects1'].copy():
            if item != 'size' and item != 'pos' and item != 'scroll' and item != 'linkedScrollbar':
                del self.menuesData['megaprojects1'][item]
        self.menuesData['megaprojects1']['scroll'] = 0
        self.menuesData['megaprojects1']['scrollQueue'] = []

        if physicsEngine.GetProperty(system, planet, 'type') == 'terrestrial':
            for i, megaproject in enumerate(physicsEngine.GetProperty(system, planet, 'megaprojects')):
                self.CreateMegaprojectData('megaprojects1', i, megaproject)
            if len(physicsEngine.GetProperty(system, planet, 'megaprojects')) == 0:
                i=0
            self.menuesData['megaprojects1']['maxScroll'] = -(i+1)*125+210

            addedProjects = 0
            for megaprojectID in physicsEngine.megaprojectsData:
                #if the search matches
                if self.menuesData['planetMenu2Megaprojects']['search']['text'].lower() in \
                physicsEngine.megaprojectsData[megaprojectID]['title'].lower() and \
                megaprojectID not in [megaproject[0] for megaproject in physicsEngine.GetProperty(system, planet, 'megaprojects')]:
                    self.CreateMegaprojectData('megaprojects2', addedProjects, megaprojectID)
                    addedProjects += 1
            self.menuesData['megaprojects2']['maxScroll'] = -addedProjects*125+210
        else:
            self.menuesData['megaprojects1']['maxScroll'] = 210
            self.menuesData['megaprojects2']['maxScroll'] = 210


        self.menuesData['planetMenu2Megaprojects']['text2']['text'] = \
        f"{len(physicsEngine.GetProperty(system, planet, 'megaprojects'))}/2 Active"


    def UpdateAddMegaprojectsMenu(self):
        weeklyAmount = 0.0001 * physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'mass') #0.01%
        totalAmountToAdd = 0
        megaprojectType = physicsEngine.megaprojectsData[game.megaprojectToAdd]['type']

        if 'addMegaprojectMenu2' in menuHandler.currentMenues:
            text1 = menuHandler.menuesData['addMegaprojectMenu2']['totalAmountInput1']['text']
            text2 = menuHandler.menuesData['addMegaprojectMenu2']['totalAmountInput2']['text']
            text1Colour = menuHandler.menuesData['addMegaprojectMenu2']['totalAmountInput1']['colour']
            text2Colour = menuHandler.menuesData['addMegaprojectMenu2']['totalAmountInput2']['colour']
            if text1 != '' and text2 != '' and text1Colour == (255, 255, 255) and text2Colour == (255, 255, 255):
                totalAmountToAdd = float(text1) * 10 ** int(text2)

        else:
            text = menuHandler.menuesData['addMegaprojectMenu3']['totalAmountInput']['text']
            textColour = menuHandler.menuesData['addMegaprojectMenu3']['totalAmountInput']['colour']
            if text != '' and textColour == (255, 255, 255):
                if megaprojectType == 'add_substance':
                    substance = physicsEngine.megaprojectsData[game.megaprojectToAdd]['effects']
                    substanceId = physicsEngine.const.substanceIdByKey[substance]
                    totalSubstanceAmount = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'total-substances')[substanceId]
                    totalAmountToAdd = float(text)/100 * totalSubstanceAmount

        if weeklyAmount > totalAmountToAdd:
            weeklyAmount = totalAmountToAdd

        if totalAmountToAdd != 0:
            menuHandler.menuesData['addMegaprojectMenu']['weeklyAmount']['text'] = \
                f"Weekly Amount: {DataHandler.ScientificNotation(weeklyAmount, 2)} kg"
            menuHandler.menuesData['addMegaprojectMenu']['time']['text'] = \
                f"Time: {DataHandler.WeeksToYears(math.ceil(totalAmountToAdd / weeklyAmount))}"

            if megaprojectType == 'add_substance':
                substance = physicsEngine.megaprojectsData[game.megaprojectToAdd]['effects']
                totalAmount = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'total-substances') \
                    [physicsEngine.const.substanceIdByKey[substance]]
                if totalAmount == 0:
                    totalAmount = 1
                copiedPhysicsEngine = copy.deepcopy(physicsEngine)
                megaprojectData = game.GetMegaprojectAddData()
                if megaprojectData != None:
                    copiedPhysicsEngine.systemsData[game.currentSystem]['planets'][game.planetMenuPlanet]['megaprojects'].append(megaprojectData)
                
                #only the necessary properties to calculate
                properties = [
                    'bb-temperature',
                    'gas-fractions', 
                    'gases',
                    'in-atmosphere',
                    'atm-pressure',
                    'target-temperature',
                    'temperature',
                ]
                done = False
                newTemp = -1
                i=0
                while not done:
                    prevTemp = newTemp
                    copiedPhysicsEngine.ApplyMegaprojects(game.currentSystem, game.planetMenuPlanet)
                    for _property in properties:
                        copiedPhysicsEngine.Update(game.currentSystem, game.planetMenuPlanet, _property)
                    newTemp = copiedPhysicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'temperature')
                    if round(newTemp, 4) == round(prevTemp, 4):
                        done = True
                        i-=1
                    i+=1

                temperature = round(DataHandler.ConvertTemperature(game.settings['units']['temperature'], 'k', physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'temperature')), 2)
                newTemperature = round(DataHandler.ConvertTemperature(game.settings['units']['temperature'], 'k', copiedPhysicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'temperature')), 2)
                planetName = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'name')
                time = DataHandler.WeeksToYears(i)
                text = f"In {time} this will change {planetName}'s temperature from {temperature} to {newTemperature}"

                menuHandler.menuesData['addMegaprojectMenu']['effectsClarification']['text'] = text


    def GetFont(self, font, size):
        try:
            return pygame.font.Font(path+font+'.ttf', size)
        except:
            return pygame.font.SysFont(font, size)


    def ResetButtons(self, menuID, thoroughly=False):
        #make all the buttons' states to 0
        for key in list(self.menuesData[menuID].keys()):
            try:
                if self.menuesData[menuID][key]['type'] in ['button', 'checkbutton']:
                    self.menuesData[menuID][key]['state'] = 0
                elif self.menuesData[menuID][key]['type'] == 'dropdown':
                    self.menuesData[menuID][key]['state'] = 0
                    self.menuesData[menuID][key]['listItemSelected'] = None
                    if thoroughly:
                        self.menuesData[menuID][key]['droppedDown'] = False
            except:
                pass


    def AddMenu(self, menuID):
        if menuID not in self.currentMenues:
            self.ResetButtons(menuID, thoroughly=True)
            self.currentMenues.append(menuID)
            self.interactiveMenues.append(menuID)
            self.UpdateMenuData(menuID)


    def RemoveMenu(self, menuID):
        try:
            self.currentMenues.remove(menuID)
            self.interactiveMenues.remove(menuID)
            del self.currentMenuesData[menuID]
            del game.hitboxes[menuID]
        except:
            pass


    def Values(self, ID):
        args = ID.split()
        if len(args) > 2: #more than '/value' and the ID
            args.pop(0)
            ID = args.pop(0)
        else:
            ID = args[1]
        #now the variable ID is the ID and the variable args is the args

        if ID == 'defaultFont':
            if 'bold' in args:
                return 'rajdhani-bold'
            return 'rajdhani-regular'

        elif ID == 'frameSize':
            ''' args[0] is anchor, args[1] is xOffset and args[2] is yOffset '''
            if args[0] == 'w':
                pos = [0, int(game.frameSize[1]/2)]
            elif args[0] == 'c':
                pos = [int(game.frameSize[0]/2), int(game.frameSize[1]/2)]
            elif args[0] == 'e':
                pos = [game.frameSize[0], int(game.frameSize[1]/2)]
            elif args[0] == 'n':
                pos = [0, int(game.frameSize[1]/2)]
            elif args[0] == 'ne':
                pos = [game.frameSize[0], 0]
            elif args[0] == 'sw':
                pos = [0, game.frameSize[1]]

            return [pos[0]+int(args[1]), pos[1]+int(args[2])]

        elif ID == 'planetMenuPlanetName':
            return physicsEngine.systemsData[game.currentSystem]['planets'][game.planetMenuPlanet]['name']

        elif ID == 'planet_menu_landscape_pic':
            planetType = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'type')
            if planetType == 'terrestrial':
                return 'landscape_'+physicsEngine.systemsData[game.currentSystem]['planets'][game.planetMenuPlanet]['landscape-pics'][int(args[0])-1]
            else:
                return 'landscape_'+physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'landscape-pics')


        elif ID == 'moonsMenuTitle':
            if physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'type') == 'star':
                return 'Planets'
            else:
                return 'Moons'

        elif ID == 'small_planet_menu':
            if args[0] == 'title':
                return physicsEngine.GetProperty(game.currentSystem, game.smallPlanetMenuPlanet, 'name')
            elif args[0] == 'planet':
                #if physicsEngine.IsMoon(game.currentSystem, game.smallPlanetMenuPlanet):

                if physicsEngine.GetProperty(game.currentSystem, game.smallPlanetMenuPlanet, 'type') == 'star':
                    return f'{physicsEngine.GetStellarClassification(game.currentSystem, game.smallPlanetMenuPlanet)}-class'

                else:
                    isMoon = physicsEngine.IsMoon(game.currentSystem, game.smallPlanetMenuPlanet)
                    host = physicsEngine.GetProperty(game.currentSystem, game.smallPlanetMenuPlanet, 'host')
                    host_name = physicsEngine.GetProperty(game.currentSystem, host, 'name')
                    orbits = physicsEngine.GetListOfOrbits(game.currentSystem, host)
                    endings = ['th', 'st', 'nd', 'rd', 'th', 'th', 'th', 'th', 'th', 'th']
                    return f'{orbits.index(game.smallPlanetMenuPlanet) + 1}{endings[int(str(orbits.index(game.smallPlanetMenuPlanet) + 1)[-1])]} {["planet", "moon"][isMoon]} of {host_name}'

            elif args[0] == 'type':
                types = {
                    'terrestrial': 'Terrestrial World',
                    'gas-giant': 'Gas giant',
                    'star': 'Star'
                }
                return types[physicsEngine.GetProperty(game.currentSystem, game.smallPlanetMenuPlanet, 'type')]

        elif ID == 'timeButton':
            matrix = {
                'normal': ['play_icon', 'pause_icon'],
                'hover': ['play_icon_hover', 'pause_icon_hover'],
                'click': ['play_icon', 'pause_icon']
            }
            return matrix[args[0]][game.timeState]

        elif ID == 'time':
            return DataHandler.GetDate(game.time)

        elif ID == 'timeSpeed':
            return str(game.timeSpeed+1)


        elif ID == 'piechart1':
            data = [
                {
                    'cut': 0.05,
                    'colour': (255, 0, 0)
                },
                {
                    'cut': 0.15,
                    'colour': (0, 255, 0)
                },
                {
                    'cut': 0.05,
                    'colour': (0, 0, 255)
                },
                {
                    'cut': 0.4,
                    'colour': (0, 255, 0)
                },
                {
                    'cut': 0.35,
                    'colour': (0, 0, 255)
                }
            ]
            return data

        elif ID == 'physics':
            if args[0] == 'type':
                types = {
                    'terrestrial': 'Terrestrial',
                    'gas-giant': 'Gas giant',
                    'star': 'Star'
                }
                return types[physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'type')]

            elif args[0] == 'mass':
                mass = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'mass')

                if game.settings['units']['mass'] == 'scientific':
                    return DataHandler.ScientificNotation(mass, 2)+'kg'

                elif game.settings['units']['mass'] == 'comparative':
                    compare = physicsEngine.const.massComparisonByPlanetType
                    units = physicsEngine.const.massUnitsByPlanetType
                    planetType = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'type')
                    compare_mass = compare[planetType]
                    return str(DataHandler.RoundSignificantFigures(mass/compare_mass, 3))+' '+units[planetType]

                else: #prefix
                    return DataHandler.NumberPrefix(mass, 3, True, game.settings['prefixSet'])+[' ', ''][game.settings['prefixSet'] == 'unit']+'kg'

            elif args[0] == 'radius':
                radius = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'radius')

                if game.settings['units']['radius'] == 'plain':
                    return DataHandler.AddCommas(int(radius/1000))+' km'

                else: #comparative
                    compare = {
                        'terrestrial': physicsEngine.const.radius_earth,
                        'gas-giant': physicsEngine.const.radius_jupiter,
                        'star': physicsEngine.const.radius_sun
                    }
                    units = {
                        'terrestrial': 'RE',
                        'gas-giant': 'RJ',
                        'star': 'RS'
                    }
                    planetType = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'type')
                    compare_radius = compare[planetType]
                    return str(DataHandler.RoundSignificantFigures(radius/compare_radius, 3))+' '+units[planetType]

            elif args[0] == 'gravity':
                gravity = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'gravity')

                if game.settings['units']['gravity'] == 'plain':
                    return str(DataHandler.RoundSignificantFigures(gravity, 3))+' N'

                else: #comparative
                    compare_gravity = physicsEngine.const.gravity_earth
                    return str(DataHandler.RoundSignificantFigures(gravity/compare_gravity, 3))+' GE'

            elif args[0] == 'albedo':
                albedo = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'albedo')
                return str(round(albedo, 2))

            elif args[0] == 'erv':
                erv = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'erv')
                return str(DataHandler.RoundSignificantFigures(erv, 3, makeInt=True))+' m/s'

            elif args[0] == 'temperature':
                temperature = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'temperature')
                temperature = DataHandler.ConvertTemperature(game.settings['units']['temperature'], 'k', temperature)
                units = physicsEngine.const.temperatureUnitNames
                return str(DataHandler.RoundSignificantFigures(temperature, 3, makeInt=True))+' '+units[game.settings['units']['temperature']]

            elif args[0] == 'mfs':
                mfs = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'mfs')
                rounded = DataHandler.RoundSignificantFigures(mfs, 3, makeInt=True)
                if rounded > 1000:
                    return DataHandler.AddCommas(rounded)
                else:
                    return str(rounded)

            elif args[0] == 'host':
                host = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'host')
                return physicsEngine.GetProperty(game.currentSystem, host, 'name')

            elif args[0] == 'sma':
                sma = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'sma')

                if game.settings['units']['sma'] == 'au':
                    smaAU = sma / physicsEngine.const.au
                    return str(DataHandler.RoundSignificantFigures(smaAU, 3))+' AU'
                else: # km
                    return DataHandler.NumberPrefix(round(sma/1000), 3, False, game.settings['prefixSet'], makeInt=True)+' km'

            elif args[0] == 'orbital-velocity':
                orbitalVel = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'orbital-velocity')
                return str(DataHandler.RoundSignificantFigures(orbitalVel/1000, 3))+' km/s'

            elif args[0] == 'pressure':
                pressure = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'atm-pressure')
                if pressure < 10:
                    return '~0 kPa'
                return str(DataHandler.RoundSignificantFigures(pressure/1000, 3, makeInt=True))+' kPa'

            elif args[0] == 'atm-comp':
                fractions = physicsEngine.GetAtmFractions(game.currentSystem, game.planetMenuPlanet)
                gases_colours = [
                    (190, 40, 190),
                    (0, 95, 190),
                    (180, 5, 105),
                    (175, 10, 15),
                    (15, 95, 0),
                    (100, 0, 255),
                    (255, 255, 0),
                    (255, 0, 255)
                ]
                return [{'cut': fractions[i], 'colour': gases_colours[i]} for i in range(8)]

            elif args[0] == 'radiation':
                radiation = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'surface-radiation')
                if radiation < 1:
                    radiation = 0
                return str(DataHandler.NumberPrefix(radiation, 3, False, game.settings['prefixSet'], makeInt=True))

            elif args[0] == 'soil':
                soil = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'soil')
                return str(soil[int(args[1])])+' ppm'

            elif args[0] == 'luminosity':
                lum = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'luminosity')
                if game.settings['units']['luminosity'] == 'scientific':
                    return DataHandler.ScientificNotation(lum, 2)+'W'
                elif game.settings['units']['luminosity'] == 'comparative':
                    compare = physicsEngine.const.lum_sun
                    return str(DataHandler.RoundSignificantFigures(lum/compare, 3))+' LS'
                else: #prefix
                    return DataHandler.NumberPrefix(lum, 3, True, game.settings['prefixSet'])+[' ', ''][game.settings['prefixSet'] == 'unit']+'W'

            elif args[0] == 'stellar-classification':
                return physicsEngine.GetStellarClassification(game.currentSystem, game.planetMenuPlanet)

        elif ID == 'megaprojects':
            megaprojectType = physicsEngine.megaprojectsData[game.megaprojectToAdd]['type']
            if args[0] == 'effects':
                if megaprojectType == 'add_substance':
                    substance = physicsEngine.megaprojectsData[game.megaprojectToAdd]['effects']
                    return f"Effects: Adds {physicsEngine.const.substanceNameByKey[substance]}"

            elif args[0] == 'title':
                return f"Megaproject: {physicsEngine.megaprojectsData[game.megaprojectToAdd]['title']}"

            elif args[0] == 'desc':
                if megaprojectType == 'add_substance':
                    substance = physicsEngine.megaprojectsData[game.megaprojectToAdd]['effects']
                    return f"Changes the amount of {physicsEngine.const.substanceNameByKey[substance].lower()}, its form is determined by planet temperature." #to planet's ground or atmosphere."
            
            elif args[0] == 'current_amount':
                substance = physicsEngine.megaprojectsData[game.megaprojectToAdd]['effects']
                substanceId = physicsEngine.const.substanceIdByKey[substance]
                totalSubstanceAmount = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'total-substances')[substanceId]
                if game.settings['units']['mass'] == 'prefix': 
                    text = DataHandler.NumberPrefix(totalSubstanceAmount, 3, True, game.settings['prefixSet'])+[' ', ''][game.settings['prefixSet'] == 'unit']+'kg'
                else:
                    text = DataHandler.ScientificNotation(totalSubstanceAmount, 2)+'kg'
                planetName = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'name')
                substanceName = physicsEngine.const.substanceNameByKey[substance].lower()
                return f'{planetName} currently has {text} of {substanceName}.'

        elif ID == 'settings_menu_tabs_selection_pos':
            return (80*game.settingsMenuTabSelection+22, 60)

        elif ID == 'ledger_title':
            return ' Celestial Bodies ' if game.settings['show-moons-in-ledger'] else ' Planets '

        elif ID == 'explanation_planet_temperature':
            targetTemp = physicsEngine.GetProperty(game.currentSystem, game.planetMenuPlanet, 'target-temperature')
            unit = game.settings['units']['temperature']
            convertedTemp = DataHandler.ConvertTemperature(unit, 'k', targetTemp)
            targetTempText = f"{DataHandler.RoundSignificantFigures(convertedTemp, 3, makeInt=True)} {physicsEngine.const.temperatureUnitNames[unit]}"
            return f"The average surface temperature of the planet.\nDrifting towards the planet's target temperature, which currently is {targetTempText}."

        return 'VALUE NOT FOUND'


    def TruncLine(self, text, font, maxWidth):
        '''Internal function for WrapLine'''
        real = len(text)
        stext=text
        l=font.size(text)[0]
        cut=0
        a=0
        done=1
        old=None
        while l > maxWidth:
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


    def WrapLine(self, text, font, maxWidth):
        '''Returns given text in a list of strings divided so that no line exceeds the maxWidth'''
        '''text is text, font is the pygame font and maxWidth is the maximum width in pixels'''
        done = 0
        wrapped = []
        while not done:
            nl, done, stext = self.TruncLine(text, font, maxWidth)
            wrapped.append(stext.strip())
            text=text[nl:]
        return wrapped


    def CutLine(self, text, font, maxWidth):
        '''Returns shorted version of given text so that it fits within the maxWidth'''
        done = False
        i=0
        while not done:
            if i == 0: #för att str[:0] returnar ''
                cutText = text
            else:
                cutText = text[:-i]+'..'
            textSize = font.size(cutText)[0]
            if textSize <= maxWidth or cutText == '': #sluta när den passar eller om den inte passar alls
                done = True

            i+=1
        return cutText


    def DecodeText(self, text, defaultColour):
        decodedText = ''
        zones = []
        colours = []
        toSkip = []
        charsToBeIgnored = 0  # in the text
        for i, char in enumerate(text):
            if char == '%' and i+1<len(text) and text[i+1] == '%':  # found a zone
                #end previous nozone
                if i > 0:
                    zones.append(len(decodedText))
                    colours.append(defaultColour)

                #get the colour
                j=0
                char2 = text[i+j+2]
                while char2 != '%':
                    char2 = text[i+j+2]
                    j+=1
                offset = j
                colourText = text[i+2:i+offset+1]
                zoneColour = tuple(int(colourText.split()[j]) for j in range(3))

                j=0
                char2 = text[i+offset+2]
                while char2 != '%':
                    char2 = text[i+offset+j+2]
                    j+=1
                zones.append(i+j-1-charsToBeIgnored)
                colours.append(zoneColour)
                decodedText += text[i+2+offset:i+offset+j+1]
                for k in range(i, i+offset+j+2):
                    toSkip.append(k)
                charsToBeIgnored += offset+3

            elif i not in toSkip:  # no zone
                decodedText += char

        if len(zones) == 0 or len(decodedText) > zones[-1]:
            zones.append(len(decodedText))
            colours.append(defaultColour)

        return decodedText, zones, colours


    def ConsiderRemovedChars(self, lines, zones, originalText):
        # when the lines are wrapped up spaces are stripped away from the lines.
        # this function changes the zones' values according to the removed characters.
        joinedLines = ''.join(line for line in lines)

        removedChars = []
        for i in range(len(originalText)):
            if originalText[i] != joinedLines[i-len(removedChars)]:
                removedChars.append(i)

        for i in range(len(zones)):
            zoneValue = zones[i]
            for charIndex in removedChars:
                print(i, zoneValue)
                if charIndex >= zoneValue:
                    break
                zones[i] -= 1
        return zones


    def ApplyTextColourInsertion(self, lines, zones, colours, defaultColour):
        joinedLines = ''.join(line for line in lines)
        splits = []
        for i, line in enumerate(lines):
            prevLinePos = 0
            if i > 0:
                prevLinePos = splits[i-1]
            splits.append(len(line)+prevLinePos)  # now contains all line breaks

        defaultColours = tuple(defaultColour for i in range(len(splits)))
        splits = list(zip(splits, defaultColours))
        for i in range(len(splits)):
            splits[i] += (i, 'lineSplit')
        # splits is now made up of tuples: (end_point, colour, y_level, origin)

        for (zone, colour) in zip(zones, colours):
            for i, split in enumerate(splits):
                if split[0] >= zone:
                    break
            splits.insert(i, (zone, colour, splits[i][2], 'zone'))  # insert new zone

            # When adding a new zone, colour of previous zones from line splits' colours need to be changed
            zoneType = 'zone'
            if i > 0:
                zoneType = splits[i-1][3]
            j=0
            while zoneType == 'lineSplit':
                splits[i-j-1] = list(splits[i-j-1])
                splits[i-j-1][1] = splits[i][1]
                splits[i-j-1] = tuple(splits[i-j-1])

                zoneType = splits[i-j-2][3]
                j+=1

        # remove duplicates
        splitsCopy = splits.copy()
        deleted = 0
        for i, split in enumerate(splitsCopy):
            prevSplitPos = 0
            if i > 0:
                prevSplitPos = splitsCopy[i-1][0]
            if split[0] == prevSplitPos:
                del splits[i-deleted]
                deleted += 1

        zones = []  # remove the lineSplit/zone thing
        for split in splits:
            zones.append(split[:3])

        return zones


    def ObjectCrop(self, objectSize, objectPos, menuSize, menuPos):
        ''' crops the object if it is partly outside the menu borders '''
        crop = [0, 0, objectSize[0], objectSize[1]] #left, top, right, down

        if objectPos[0] < menuPos[0]:
            crop[0] = menuPos[0] - objectPos[0]

        if objectPos[1] < menuPos[1]:
            crop[1] = menuPos[1] - objectPos[1]

        if objectPos[0] + objectSize[0] > menuPos[0] + menuSize[0]:
            crop[2] = objectSize[0] - ((objectPos[0] + objectSize[0]) - (menuPos[0] + menuSize[0]))

        if objectPos[1] + objectSize[1] > menuPos[1] + menuSize[1]:
            crop[3] = objectSize[1] - ((objectPos[1] + objectSize[1]) - (menuPos[1] + menuSize[1]))

        posChange = [crop[0], crop[1]]

        return crop, posChange

    def RenderMenu(self, menuID):
        for item in self.currentMenuesData[menuID]:
            if item[0] == 'blit':
                if len(item) == 4:
                    rect = game.screen.blit(item[1], item[2], item[3])
                else: #len is 3
                    rect = game.screen.blit(item[1], item[2])

            elif item[0] == 'polygon':
                pygame.draw.polygon(game.screen, item[1], item[2])
            elif item[0] == 'rect':
                pygame.draw.rect(game.screen, item[1], item[2], item[3], item[4])

    def UpdateMenuData(self, menuID):

        '''

        Det finns en hel del att förbättra här lol
        - På många ställen används [str.split()[i] for i in range(x)] när man bara kan skriva str.split() istället
        - Istället för att allt är strings i menudata kan /value checken också kolla om objekt i fråga är en string, och sen kolla om den börjar med /value
        - "Convert items from strings" kan istället assignas till nya variabler
        - "del menuData['size'], menuData['pos']", "del menuData['maxScroll']" är dåligt. Istället kan man bara kolla så att en menuitems key inte är något 
            av de tre keywordsen i loopen
        - Om ovanstående två saker fixas kan copy.deepcopy() elimineras. Då kan även import copy tas bort.
        - När eventhanteraren inser att en knapp är hovrad över/nertryckt behöver inte all data för hela menyn uppdateras. Istället behöver bara datan för
            den knappen uppdateras. 
        - Om en items crop[2] eller crop[3] är 0 behöver den inte läggas till i self.currentMenuesData[menuID]

        '''
        
        if menuID not in self.currentMenues:
            return
        self.currentMenuesData[menuID] = []
        game.hitboxes[menuID] = []


        #menuData = self.menuesData[menuID].copy()
        menuData = copy.deepcopy(self.menuesData[menuID]) # om det här har för hög performance hit så går det att ändra alla "convert properties from str" till nya variabler så att de inte ändrar self.menuesData. Exempel: newPos = [int(item['pos'].split()[0]), int(item['pos'].split()[1])]
        menuSize = menuData['size'] 
        menuPos = menuData['pos']
        del menuData['size'], menuData['pos']

        if 'scroll' in menuData.keys():
            menuScroll = menuData['scroll']
            del menuData['scroll']
        else:
            menuScroll = 0
        if 'maxScroll' in menuData.keys(): # maxScroll is not used in this function.
            del menuData['maxScroll']
        if 'scrollQueue' in menuData.keys(): # scrollQueue is not used in this function.
            del menuData['scrollQueue']
        if 'linkedScrollbar' in menuData.keys(): # linkedScrollbar is not used in this function.
            del menuData['linkedScrollbar']

        if type(menuSize) is str and menuSize[:6] == '/value':
            menuSize = self.Values(menuSize)
        if type(menuPos) is str and menuPos[:6] == '/value':
            menuPos = self.Values(menuPos)
        if type(menuScroll) is str and menuScroll[:6] == '/value':
            menuScroll = self.Values(menuScroll)

        for key in menuData.keys():

            for itemKey in menuData[key]:

                if menuData[key]['type'] == 'treeview' and itemKey == 'items': 
                    for treeviewItemKey in menuData[key][itemKey].keys():

                        for treeviewItemPropertyKeys in menuData[key][itemKey][treeviewItemKey]:

                            if type(menuData[key][itemKey][treeviewItemKey][treeviewItemPropertyKeys]) is str and \
                                menuData[key][itemKey][treeviewItemKey][treeviewItemPropertyKeys][:6] == '/value':
                                menuData[key][itemKey][treeviewItemKey][treeviewItemPropertyKeys] = self.Values(menuData[key][itemKey][treeviewItemKey][treeviewItemPropertyKeys])

                elif type(menuData[key][itemKey]) is str and menuData[key][itemKey][:6] == '/value':
                    menuData[key][itemKey] = self.Values(menuData[key][itemKey])


        toPutLast = []
        for k, (key, item) in enumerate(menuData.items()): #for each item in the menu

            if item['type'] == 'image':
                crop = item['crop']
                pos = [item['pos'][0]+menuPos[0], item['pos'][1]+menuPos[1]+menuScroll]
                image = game.images[item['imageID']]
                if 'resize' in item.keys():
                    image = pygame.transform.scale(image, item['resize']).convert_alpha()

                crop, posChange = self.ObjectCrop([crop[2]-crop[0], crop[3]-crop[1]], pos, menuSize, menuPos)
                pos = [pos[0]+posChange[0], pos[1]+posChange[1]]
                self.currentMenuesData[menuID].append(['blit', image, pos, crop])

            elif item['type'] == 'text':
                item['pos'] = (item['pos'][0], item['pos'][1]+menuScroll)

                font = self.GetFont(item['font'], item['fontSize'])
                fontHeight = font.size('H')[1]

                originalText, zones, colours = self.DecodeText(item['text'], item['textColour'])
                textPieces = originalText.split('\n')
                processedTextPieces = []
                for text in textPieces:
                    if item['wrapLines']:
                        processedTextPieces.extend(self.WrapLine(text, font, item['crop'][2]))
                    else:
                        processedTextPieces.append(self.CutLine(text, font, item['crop'][2]))

                zones = self.ConsiderRemovedChars(processedTextPieces, zones, originalText)
                zones = self.ApplyTextColourInsertion(processedTextPieces, zones, colours, item['textColour'])

                #make lines out of the zones
                joinedLines = ''.join(line for line in processedTextPieces)
                finalTextPieces = []
                prevZoneEnd = 0
                for zone in zones:
                    finalTextPieces.append(joinedLines[prevZoneEnd:zone[0]])
                    prevZoneEnd = zone[0]

                totalChars = 0
                for i, text in enumerate(finalTextPieces):
                    pos = [item['pos'][0]+menuPos[0], item['pos'][1]+zones[i][2]*fontHeight+menuPos[1]]

                    # snap to the left
                    for j in range(i):
                        if zones[j][2] == zones[i][2]:
                            pos[0] += font.size(finalTextPieces[j])[0]

                    renderedText = font.render(text, True, zones[i][1], item['bgColour'])

                    crop, posChange = self.ObjectCrop(font.size(text), pos, menuSize, menuPos)
                    pos = [pos[0]+posChange[0], pos[1]+posChange[1]]
                    self.currentMenuesData[menuID].append(['blit', renderedText, pos, crop])
                    if 'hover' in item.keys():
                        game.hitboxes[menuID].append([f"hover%{item['hover']}", *pos, pos[0]+crop[2], pos[1]+crop[3]])

                    totalChars += len(text)


                '''
                for i, text in enumerate(processedTextPieces):
                    pos = [item['pos'][0]+menuPos[0], item['pos'][1]+i*fontHeight+menuPos[1]]
                    if item['wrapLines']:
                        if item['wordwrapJustification'] == 'w':
                            indentLength = 0
                        elif item['wordwrapJustification'] == 'c':
                            boxCenter = int(item['crop'][2] / 2)
                            textCenter = int(font.size(text)[0] / 2)
                            indentLength = boxCenter - textCenter
                        pos[0] += indentLength

                    if item['anchor'] == 'c': #else 'w'  
                        textSize = font.size(text)
                        pos[0] -= int(textSize[0]/2)
                        pos[1] -= int(textSize[1]/2)

                    renderedText = font.render(text, True, item['textColour'], item['bgColour'])

                    crop, posChange = self.ObjectCrop(font.size(text), pos, menuSize, menuPos)
                    pos = [pos[0]+posChange[0], pos[1]+posChange[1]]
                    self.currentMenuesData[menuID].append(['blit', renderedText, pos, crop])
                    if 'hover' in item.keys():
                        game.hitboxes[menuID].append([f"hover%{item['hover']}", *pos, pos[0]+crop[2], pos[1]+crop[3]])

                '''

                


            elif item['type'] == 'textInput':
                item['pos'] = (item['pos'][0], item['pos'][1]+menuScroll)

                font = self.GetFont(item['font'], item['fontSize'])
                text = self.CutLine(item['text'], font, item['size'][0])
                fontHeight = font.size('H')[1]
                textWidth = font.size(text)[0]
                renderedText = font.render(text, True, item['colour'], item['bgColour'])
                pos = [item['pos'][0]+menuPos[0], item['pos'][1]+int(item['size'][1]/2)-int(fontHeight/2)+menuPos[1]]
                self.currentMenuesData[menuID].append(['blit', renderedText, pos])
                game.hitboxes[menuID].append([f'textInput%{key}', pos[0], pos[1]-5, pos[0]+item['size'][0], pos[1]+item['size'][1]-5])
                if item['cursorImage'] != '&None' and item['state']:
                    image = game.images[item['cursorImage']]
                    self.currentMenuesData[menuID].append(['blit', image, [pos[0]+textWidth, pos[1]+int(fontHeight/2)-image.get_height()/2]])

            elif item['type'] == 'radiobuttonArray':
                fontSize = item['fontSize']
                pos = list(item['pos'])
                pos[1] += menuScroll
                size = item['size']
                textColour = item['textColour']
                items = item['items'].split()
                states = item['itemStates']
                bgColour = item['bgColour']
                rowDistance = item['rowDistance']

                font = self.GetFont(item['font'], fontSize)
                fontHeight = font.size('H')[1]
                for i, text in enumerate(items):
                    imagePos = [pos[0]+menuPos[0], pos[1]+menuPos[1]+rowDistance*i]
                    imageIDS = [['emptyImage', 'emptyImageHover', 'emptyImageClick'], ['selectedImage', 'selectedImageHover', 'selectedImageClick']]
                    image = game.images[item[imageIDS[i==int(item['selectedItem'])][states[i]]]]
                    self.currentMenuesData[menuID].append(['blit', image, imagePos])

                    renderedText = font.render(text, True, textColour, bgColour)
                    crop, posChange = self.ObjectCrop(font.size(text), imagePos, menuSize, menuPos)
                    textPos = [imagePos[0]+posChange[0]+image.get_width()+10, imagePos[1]+posChange[1]+image.get_height()/2-fontHeight/2+1]
                    self.currentMenuesData[menuID].append(['blit', renderedText, textPos, crop])

                    textLen = font.size(text)[0]
                    game.hitboxes[menuID].append([f'radiobuttonArray%{key}%{i}', imagePos[0], imagePos[1], imagePos[0]+image.get_width()+10+textLen, imagePos[1]+image.get_height()])


            elif item['type'] == 'treeview':

                font = self.GetFont(item['font'], item['fontSize'])

                #line below draws the hitbox for the treeview. Can be used for debugging
                #pygame.draw.rect(game.screen, (255, 0, 0), pygame.Rect(item['pos'][0]+menuPos[0], item['pos'][1]+menuPos[1], item['crop'][2], item['crop'][3]), 2)

                textItems = item['items']
                rowsPlaced = 0
                extraYPos = 0 #if a line is split in two lines, extra ypos is added
                previousRendered = False
                for i, textItem in enumerate(textItems.values()):
                    if 'extraYPos' in list(textItem.keys()):
                        extraYPos += textItem['extraYPos']

                    textKey = list(textItems.keys())[i]

                    #create the variables for position and text
                    if textItem['side'] == 'left':
                        ypos = item['pos'][1] + item['rowDistance'] * rowsPlaced + extraYPos + menuScroll
                        xpos = item['pos'][0] + item['indentLength']*textItem['indents']
                        text = self.CutLine(textItem['text'], font, item['pos'][0] + item['crop'][2] - xpos - item['rightSideClearance'])
                        if item['enableDropdown'] and textItem['side'] == 'left':
                            xpos += item['arrowLength'] #so that the text is further in

                    else:
                        ypos = item['pos'][1] + item['rowDistance'] * (rowsPlaced - 1) + extraYPos + menuScroll
                        text = self.CutLine(textItem['text'], font, item['rightSideClearance'])
                        xpos = item['pos'][0] + item['crop'][2] - font.size(text)[0]

                    #check if the line is supposed to be drawn or not.
                    #it's not to be drawn if its outside the hitbox
                    renderNext = True
                    if item['enableDropdown']:
                        currentItemIndents = textItem['indents']
                        itemKeys = list(item['items'].keys())

                        for itemKey in itemKeys: #ta bort alla som är högersida
                            if item['items'][itemKey]['side'] == 'right':
                                itemKeys.remove(itemKey)

                        itemKeys.reverse()
                        for j in range(len(itemKeys) - i):
                            itemKeys.pop(0)

                        smallestIndent = 99999
                        for itemKey in itemKeys:
                            #if item above in hierarchy is not downtabbed, don't render
                            if item['items'][itemKey]['indents'] < currentItemIndents and \
                                item['items'][itemKey]['indents'] < smallestIndent and \
                                not item['items'][itemKey]['downTabbed']:

                                renderNext = False
                                break

                            if item['items'][itemKey]['indents'] < smallestIndent:
                                smallestIndent = item['items'][itemKey]['indents']

                    #if the text is entirely outside the hitbox, don't render
                    #if side is right and text on the same row on the left is not rendered, dont render
                    if (not previousRendered and textItem['side'] == 'right') or ypos > item['pos'][1]+item['crop'][3]:
                        renderNext = False

                    previousRendered = renderNext

                    if renderNext:
                        if textItem['side'] == 'left':
                            rowsPlaced += 1

                            if len(list(textItems.keys())) > i+1: #if there is textKey ahead
                                nextTextKey = list(textItems.keys())[i+1]
                                if item['items'][nextTextKey]['side'] == 'right' and len(list(textItems.keys())) > i+2: # if the next textItem is on the right and there is at least another key ahead, ignore the key on the right
                                    nextTextKey = list(textItems.keys())[i+2]
                                    hasNoTabsUnder = textItems[textKey]['indents'] >= int(textItems[nextTextKey]['indents'])
                                else:
                                    hasNoTabsUnder = True
                            else: #so if there is no textkey ahead
                                hasNoTabsUnder = True

                            if item['enableDropdown']:
                                if not hasNoTabsUnder:

                                    if textItem['downTabbed']:
                                        self.currentMenuesData[menuID].append(['blit', game.images[item['downarrow']], [xpos-item['arrowLength']+menuPos[0], ypos+menuPos[1]]])
                                    else:
                                        self.currentMenuesData[menuID].append(['blit', game.images[item['leftarrow']], [xpos-item['arrowLength']+menuPos[0], ypos+menuPos[1]]])

                                    game.hitboxes[menuID].append(['treeview%'+key+'%'+textKey, xpos-item['arrowLength']+menuPos[0], ypos+menuPos[1], xpos+item['arrowLength']+menuPos[0], ypos+item['rowDistance']+menuPos[1]])
                                    #line below draws hitboxes for the arrows. Can be used for debugging
                                    #pygame.draw.rect(game.screen, (255, 0, 0), pygame.Rect(xpos-item['arrowLength']+menuPos[0], ypos+menuPos[1], item['arrowLength'], item['rowDistance']), 2) #måla hitboxen

                        xpos, ypos = xpos+menuPos[0], ypos+menuPos[1]

                        if 'selectedItem' in item:
                            image = game.images[item['selectionImage']]
                            fontHeight = font.size('H')[1]
                            xOffset = int(item['xOffset'])
                            pos = [xpos+xOffset, ypos+fontHeight/2-image.get_height()/2-1]
                            crop, posChange = self.ObjectCrop((image.get_width(), image.get_height()), pos, [menuSize[0]-xOffset, menuSize[1]], [menuPos[0]+xOffset, menuPos[1]])
                            pos = [pos[0]+posChange[0], pos[1]+posChange[1]]

                            if textKey == item['selectedItem']: #this textitem is selected
                                self.currentMenuesData[menuID].append(['blit', image, pos, crop])
                            else:
                                game.hitboxes[menuID].append([f'TreeviewSelection%{key}%{textKey}', pos[0], pos[1], pos[0]+crop[2], pos[1]+crop[3]])
                        
                        crop, posChange = self.ObjectCrop(font.size(text), (xpos, ypos), menuSize, menuPos)
                        xpos, ypos = xpos+posChange[0], ypos+posChange[1]
                        renderedText = font.render(text, True, textItem['textColour'], item['bgColour'])
                        self.currentMenuesData[menuID].append(['blit', renderedText, [xpos, ypos], crop])
                        if 'hover' in textItem.keys():
                            game.hitboxes[menuID].append([f"hover%{textItem['hover']}", xpos, ypos, xpos+crop[2], ypos+crop[3]])

            elif item['type'] == 'button':
                item['pos'] = (item['pos'][0], item['pos'][1]+menuScroll)

                crop = item['crop']
                pos = (item['pos'][0]+crop[0]+menuPos[0], item['pos'][1]+crop[1]+menuPos[1])
                imageIDS = ['imageID', 'hoverImageID', 'clickImageID']

                crop, posChange = self.ObjectCrop([crop[2]-crop[0], crop[3]-crop[1]], pos, menuSize, menuPos)
                pos = [pos[0]+posChange[0], pos[1]+posChange[1]]
                self.currentMenuesData[menuID].append(['blit', game.images[item[imageIDS[item['state']]]], pos, crop])
                game.hitboxes[menuID].append([item['command']+'%'+key, pos[0], pos[1], pos[0]+crop[2]-crop[0], pos[1]+crop[3]-crop[1]])

                if 'hover' in item.keys():
                    game.hitboxes[menuID].append([f"hover%{item['hover']}", pos[0], pos[1], pos[0]+crop[2], pos[1]+crop[3]])
                
                if item['text'] != None:

                    colourIDS = ['colour', 'hoverColour', 'clickColour']
                    colour = item[colourIDS[item['state']]]

                    font = self.GetFont(item['font'], item['fontSize'])
                    textSize = font.size(item['text'])
                    renderedText = font.render(item['text'], True, colour, None)
                    self.currentMenuesData[menuID].append(['blit', renderedText, [pos[0]-int(textSize[0]/2)+int(crop[2]/2), pos[1]-int(textSize[1]/2)+int(crop[3]/2)]])


            elif item['type'] == 'piechart':

                sumOfCuts = 0
                for pieSlice in item['items']:
                    sumOfCuts += pieSlice['cut']
                if not (0.99 < sumOfCuts < 1.01):
                    raise ValueError('Sum of "{}_{}" piechart cuts is not 1'.format(menuID, key))

                sumOfPreviousAngles = 0
                for i, pieSlice in enumerate(item['items']):
                    angle = round(360 * pieSlice['cut'])
                    cx = item['pos'][0]+menuPos[0] #center x
                    cy = item['pos'][1]+menuPos[1] #center y
                    points = [(cx, cy)]
                    for j in range(angle):
                        x = cx + int(item['radius'] * math.cos((360 - (j + sumOfPreviousAngles)) * math.pi/180))
                        y = cy + int(item['radius'] * math.sin((360 - (j + sumOfPreviousAngles)) * math.pi/180))
                        points.append((x, y))
                    points.append((cx, cy))

                    if len(points) > 2: #If it has less than three points the pieslice is not even a pixel wide at the edge, so don't even bother drawing it.
                        self.currentMenuesData[menuID].append(['polygon', pieSlice['colour'], points])

                    sumOfPreviousAngles += angle

            elif item['type'] == 'dropdown':
                pos = [item['pos'][0]+menuPos[0], item['pos'][1]+menuPos[1]+menuScroll]
                crop, posChange = self.ObjectCrop(item['size'], pos, menuSize, menuPos)
                pos = [pos[0]+posChange[0], pos[1]+posChange[1]]

                if item['droppedDown']:
                    imageID = 'selected'+['ImageID', 'HoverImageID', 'ClickImageID'][item['state']]
                else:
                    imageID = ['imageID', 'hoverImageID', 'clickImageID'][item['state']]
                self.currentMenuesData[menuID].append(['blit', game.images[item[imageID]], pos, crop])
                game.hitboxes[menuID].append([f'dropdown%{key}', pos[0], pos[1], pos[0]+item['size'][0], pos[1]+item['size'][1]])

                font = self.GetFont(item['font'], item['fontSize'])
                fontHeight = font.size('H')[1]

                text = self.CutLine(item['selection'], font, item['size'][0]-item['rightSideClearance'])
                textPos = [pos[0]+5, pos[1]+item['size'][1]/2-fontHeight/2]
                renderedText = font.render(text, True, item['textColour'], None)
                crop, posChange = self.ObjectCrop(font.size(text), pos, menuSize, menuPos)
                textPos = [textPos[0]+posChange[0], textPos[1]+posChange[1]]
                if item['droppedDown']:
                    toPutLast.append(['blit', renderedText, textPos, crop])
                else:
                    self.currentMenuesData[menuID].append(['blit', renderedText, textPos, crop])

                if item['droppedDown']: # if dropped down
                    drawn_items = 0
                    for i, objectItem in enumerate(item['items']):
                        if objectItem != item['selection']: #don't bother drawing a dropdown item for the already selected item
                            objectItemPos = [pos[0], pos[1]+(drawn_items+1)*item['itemYSize']]
                            crop, posChange = self.ObjectCrop([item['size'][0], item['itemYSize']], objectItemPos, menuSize, menuPos)
                            objectItemPos = [objectItemPos[0]+posChange[0], objectItemPos[1]+posChange[1]]

                            if i != item['listItemSelected']:
                                imageID = 'dropdownImageID'
                            else:
                                if item['listItemSelectionType'] == 'hover':
                                    imageID = 'dropdownHoverImageID'
                                else:
                                    imageID = 'dropdownClickImageID'
                            toPutLast.append(['blit', game.images[item[imageID]], objectItemPos, crop])
                            game.hitboxes[menuID].append([f'dropdown%{key}%{i}', objectItemPos[0], objectItemPos[1], objectItemPos[0]+item['size'][0], objectItemPos[1]+item['size'][1]])

                            text = self.CutLine(objectItem, font, item['size'][0])
                            textPos = [objectItemPos[0]+5, objectItemPos[1]+item['size'][1]/2-fontHeight/2]
                            renderedText = font.render(text, True, item['textColour'], None)
                            crop, posChange = self.ObjectCrop(font.size(text), textPos, menuSize, menuPos)
                            textPos = [textPos[0]+posChange[0], textPos[1]+posChange[1]]
                            toPutLast.append(['blit', renderedText, textPos, crop])

                            drawn_items += 1

            elif item['type'] == 'checkbutton':
                pos = [item['pos'][0]+menuPos[0], item['pos'][1]+menuPos[1]+menuScroll]
                crop, posChange = self.ObjectCrop(item['size'], pos, menuSize, menuPos)
                pos = [pos[0]+posChange[0], pos[1]+posChange[1]]

                if item['selected']:
                    imageID = 'selected'+['ImageID', 'HoverImageID', 'ClickImageID'][item['state']]
                else:
                    imageID = ['imageID', 'hoverImageID', 'clickImageID'][item['state']]
                self.currentMenuesData[menuID].append(['blit', game.images[item[imageID]], pos, crop])
                imageSize = [game.images[item[imageID]].get_width(), game.images[item[imageID]].get_height()]

                font = self.GetFont(item['font'], item['fontSize'])
                fontHeight = font.size('H')[1]
                text = self.CutLine(item['text'], font, item['size'][0]-5-imageSize[0])
                textPos = [pos[0]+imageSize[0]+5, pos[1]+imageSize[1]/2-fontHeight/2]
                renderedText = font.render(text, True, item['textColour'], None)
                crop, posChange = self.ObjectCrop(font.size(text), textPos, menuSize, menuPos)
                textPos = [textPos[0]+posChange[0], textPos[1]+posChange[1]]
                self.currentMenuesData[menuID].append(['blit', renderedText, textPos, crop])

                game.hitboxes[menuID].append([f'checkbutton%{key}', pos[0], pos[1], pos[0]+imageSize[0]+5+font.size(text)[0], pos[1]+item['size'][1]])

            elif item['type'] == 'horizontalSlidebar':
                pos = [item['pos'][0]+menuPos[0], item['pos'][1]+menuPos[1]+menuScroll]
                crop, posChange = self.ObjectCrop(item['size'], pos, menuSize, menuPos)
                pos = [pos[0]+posChange[0], pos[1]+posChange[1]]
                self.currentMenuesData[menuID].append(['blit', game.images[item['bgImage']], pos, crop])

                pos = [item['pos'][0]+menuPos[0]+item['size'][0]*item['progress']-item['slideSize']/2, item['pos'][1]+menuPos[1]+menuScroll+item['size'][1]/2-item['slideSize']/2]
                crop, posChange = self.ObjectCrop((item['slideSize'], item['slideSize']), pos, menuSize, menuPos)
                pos = [pos[0]+posChange[0], pos[1]+posChange[1]]
                self.currentMenuesData[menuID].append(['blit', game.images[item[['slideImage', 'slideImageClicked'][item['state']]]], pos, crop])
                game.hitboxes[menuID].append([f'horizontalSlidebar%{key}', pos[0], pos[1], pos[0]+item['slideSize'], pos[1]+item['slideSize']])

            elif item['type'] == 'scrollbar':
                pos = [item['pos'][0]+menuPos[0], item['pos'][1]+menuPos[1]+menuScroll]
                crop, posChange = self.ObjectCrop(item['size'], pos, menuSize, menuPos)
                pos = [pos[0]+posChange[0], pos[1]+posChange[1]]
                self.currentMenuesData[menuID].append(['blit', game.images[item['bgImage']], pos, crop])

                pos = [item['pos'][0]+menuPos[0]+item['size'][0]/2-item['slideSize']/2, item['pos'][1]+menuPos[1]+item['size'][1]*item['progress']+menuScroll-item['slideSize']/2]
                crop, posChange = self.ObjectCrop((item['slideSize'], item['slideSize']), pos, menuSize, menuPos)
                pos = [pos[0]+posChange[0], pos[1]+posChange[1]]
                self.currentMenuesData[menuID].append(['blit', game.images[item[['slideImage', 'slideImageClicked'][item['state']]]], pos, crop])
                game.hitboxes[menuID].append([f'scrollbar%{key}', pos[0], pos[1], pos[0]+item['slideSize'], pos[1]+item['slideSize']])

            elif item['type'] == 'rect':
                #rects are not cropped to not go outside of menu borders
                pos = [item['pos'][0]+menuPos[0], item['pos'][1]+menuPos[1]+menuScroll]
                size = item['size']

                #the inner rectangle
                pos = [pos[0]+item['width'], pos[1]+item['width']]
                size = [size[0]-2*item['width'], size[1]-2*item['width']]
                self.currentMenuesData[menuID].append(['rect', item['colour'], pygame.Rect(*pos, *size), 0, item['border-radius']])

                #the outer rectangle
                self.currentMenuesData[menuID].append(['rect', item['borderColour'], pygame.Rect(*pos, *size), item['width'], item['border-radius']])

        for item in toPutLast:
            self.currentMenuesData[menuID].append(item)

    def SetHoverMenuData(self, mousePos, _input):
        #Sets the menu data
        self.AddMenu('hoverMenu')
        self.menuesData['hoverMenu']['pos'] = [mousePos[0]+10, mousePos[1]+10]
        for key in self.menuesData['hoverMenu'].copy().keys():
            if key not in ['pos', 'size', 'bgRect']:
                del self.menuesData['hoverMenu'][key]

        self.menuesData['hoverMenu']['text'] = {
            'type': 'text',
            'text': _input,
            'font': '/value defaultFont bold',
            'fontSize': 16,
            'pos': [8, 8],
            'anchor': 'w',
            'wrapLines': True,
            'wordwrapJustification': 'w', #w eller c
            'crop': (0, 0, 184, 600),
            'textColour': (255, 255, 255),
            'bgColour': None
        }

        #set the rectangle size
        self.UpdateMenuData('hoverMenu')
        hoverRectLength = 0
        hoverRectHeight = 0
        basePos = None
        for i, item in enumerate(self.currentMenuesData['hoverMenu']):
            if item[0] == 'blit':
                size = item[1].get_size()
                pos = item[2]
                if basePos == None:
                    basePos = pos

                if pos[0] - basePos[0] + size[0] > hoverRectLength:
                    hoverRectLength = pos[0] - basePos[0] + size[0]
                if pos[1] - basePos[1] + size[1] > hoverRectHeight:
                    hoverRectHeight = pos[1] - basePos[1] + size[1]

        self.menuesData['hoverMenu']['bgRect']['size'] = (hoverRectLength+16, hoverRectHeight+16)
        self.menuesData['hoverMenu']['size'] = (hoverRectLength+16, hoverRectHeight+16)

        width, height = self.menuesData['hoverMenu']['size']
        xpos, ypos = self.menuesData['hoverMenu']['pos']
        if xpos + width > game.frameSize[0]: #goes outside the frame on the right side
            self.menuesData['hoverMenu']['pos'][0] -= width
        if ypos + height > game.frameSize[1]: #goes outside the frame on the bottom side
            self.menuesData['hoverMenu']['pos'][1] -= height

        self.UpdateMenuData('hoverMenu')

    def DisableHoverMenu(self):
        self.RemoveMenu('hoverMenu')


menuHandler = MenuHandler()
physicsEngine = PhysicsEngine()
game = Game()
game.MainLoop()
