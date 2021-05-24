import pygame
import json

class COLORS:
    WHITE=(255, 255, 255)
    BLACK=(0, 0, 0)
    RED=(255, 0, 0)
    GREEN=(0, 255, 0)
    BLUE=(0, 0, 255)
    CYAN=(0, 255, 255)
    MAGENTA=(255, 0, 255)
    YELLOW=(255, 255, 0)
    GRAY=(127, 127, 127)
    LIGHT_GRAY=(160, 160, 160)
    DARK_GRAY=(94, 94, 94)
    
class Button(object):
    def __init__(self, name, position, size, color=(0,0,255), text="", textColor=(255, 255, 255), onClick=None, txtSize = 36):
        self.NAME = name
        self.POS = position
        self.SIZE = size
        self.COLOR = color
        self.TXT = text
        self.TXTCOLOR = textColor
        self.VISIBLE = True
        self.ON_CLICK = onClick
        self.TXTSIZE = txtSize
        
    def draw(self, surf, justification = "center"):
        if not self.VISIBLE: return self
        if self.COLOR != None: pygame.draw.rect(surf, self.COLOR, (self.POS, self.SIZE))
        if self.TXT != "":
            font = pygame.font.Font(None, self.TXTSIZE) #TODO: Figure out a way to auto-size the text
            text = font.render(self.TXT, 1, self.TXTCOLOR)
            if (justification == "center"):
                textPos = text.get_rect(centerx=self.POS[0]+(self.SIZE[0])/2.0, centery=self.POS[1]+(self.SIZE[1])/2.0)
            else:# (justification = "left"):
                textPos = (self.POS[0], self.POS[1])
                
            surf.blit(text, textPos)
        return self
        
    def was_clicked(self, mousePos):
        if not self.VISIBLE: return False
        return pygame.Rect(self.POS, self.SIZE).collidepoint(mousePos)
        
    def set_visible(self, vis):
        self.VISIBLE = vis
        
    def act_if_clicked(self, mousePos):
        if self.ON_CLICK != None and self.Clicked(mousePos):
            self.ON_CLICK(self.NAME)
            return True
        return False
        
class Text(object):
    def __init__(self, name, text, position, height=36, color=(0, 0, 0)):
        self.NAME = name
        self.TXT = text
        self.POS = position
        self.HT = height
        self.COLOR = color
        self.VISIBLE = True
        
    def draw(self, surf, shadow=False):
        if not self.VISIBLE: return
        self.FONT = pygame.font.Font(None, self.HT)
        if shadow:
            text = self.FONT.render(self.TXT, 1, (255-self.COLOR[0], 255-self.COLOR[1], 255-self.COLOR[2]))
            textPos = text.get_rect(left=self.POS[0]+2, top=self.POS[1]+2)
            surf.blit(text, textPos)
        
        text = self.FONT.render(self.TXT, 1, self.COLOR)
        textPos = text.get_rect(left=self.POS[0], top=self.POS[1])
        surf.blit(text, textPos)
        return self
    
    def center(self, pt, vertical=True, horizontal=True):
        self.FONT = pygame.font.Font(None, self.HT)
        text = self.FONT.render(self.TXT, 1, self.COLOR)
        textPos = text.get_rect(left=self.POS[0], top=self.POS[1])
        newLeft = self.POS[0]
        newTop = self.POS[1]
        if horizontal: newLeft = pt[0]-(textPos.width/2)
        if vertical: newTop = pt[1] - (textPos.height/2)
        self.POS = (newLeft, newTop)
    
    def set_text(self, text):
        self.TXT = text
        
    def set_visible(self, vis):
        self.VISIBLE = vis
        
    def was_clicked(self, mousePos): #this one requires you to pass the mouse coordinates
        if not self.VISIBLE: return False
        self.FONT = pygame.font.Font(None, self.HT)
        text = self.FONT.render(self.TXT, 1, self.COLOR)
        textPos = text.get_rect(left=self.POS[0], top=self.POS[1])
        return textPos.collidepoint(mousePos)
        
    def get_rect(self):
        text = self.FONT.render(self.TXT, 1, self.COLOR)
        return text.get_rect(left=self.POS[0], top=self.POS[1])
        
class TextPopup(Text):
    def __init__(self, text, timeout=10, size=36, color=COLORS.WHITE, backgroundColor=COLORS.BLACK):
        self.TXT = text
        self.COLOR = color
        self.BACKCOLOR = backgroundColor
        self.HT = size
        self.FONT = pygame.font.Font(None, self.HT)
        self.VISIBLE = True
        self.POS = (0, 0)
        self.TIME = timeout
        self.COUNTER = 0
        
        
    def activate(self, surf):
        self.BACKUP = surf.copy()
        surf.fill(self.BACKCOLOR)
        size = surf.get_size()
        self.Center((size[0]/2, size[1]/2))
        super(TextPopup, self).Draw(surf)
        self.COUNTER = 0
        self.VISIBLE = True
        
    def tick(self, surf):
        if self.COUNTER == 0:
            self.Activate(surf)
        self.COUNTER += 1
        if (self.COUNTER > self.TIME):
            self.VISIBLE = False
            surf.blit(self.BACKUP, (0, 0))
        return self.VISIBLE



ACTIVE_TXTFIELD = None
K_NORMAL = 0
K_TEXT_ENTER = 1

KeyMode = K_NORMAL
class TextField(object):
    def __init__(self, name, defaultTxt, position, size, txtColor=(0, 0, 0), border = True, borderColor=(0, 0, 0), backgroundColor=(192, 192, 192)):
        self.NAME = name
        self.POS = position
        self.SIZE = size
        self.COLOR = txtColor
        self.BACKCOLOR = backgroundColor
        self.BORDERCOLOR = borderColor
        self.BORDER = border #border is a 1px outline
        self.FONT = pygame.font.Font(None, size[1]+4)
        self.VISIBLE = True
        self.MARKER = True
        
        global ACTIVE_TXTFIELD
        
        if (ACTIVE_TXTFIELD != None and name == ACTIVE_TXTFIELD.NAME):
            #we are a copy of the active txtfield
            self.TXT = ACTIVE_TXTFIELD.TXT
            ACTIVE_TXTFIELD = self
        else:
            self.TXT = defaultTxt
    
    def draw(self, surf):
        if not self.VISIBLE: return
        
        self.act_if_clicked()
        
        if self.BORDER: #required for background and border
            pygame.draw.rect(surf, self.BORDERCOLOR, (self.POS[0]-1, self.POS[1]-1, self.SIZE[0]+2, self.SIZE[1]+2))
            pygame.draw.rect(surf, self.BACKCOLOR, (self.POS[0], self.POS[1], self.SIZE[0], self.SIZE[1]))
        txt = self.TXT
        global ACTIVE_TXTFIELD        
        active = (ACTIVE_TXTFIELD != None and ACTIVE_TXTFIELD.NAME == self.NAME)
        if (active and self.MARKER): txt += "|"
        text = self.FONT.render(txt, 1, self.COLOR)
        textPos = text.get_rect(left=self.POS[0], top=self.POS[1])
        surf.blit(text, textPos)
        return self.TXT
    
    def set_visible(self, vis):
        self.VISIBLE = vis
        
    def was_clicked(self, mousePos): #this one requires you to pass the mouse coordinates
        if not self.VISIBLE: return False
        return pygame.Rect(self.POS, self.SIZE).collidepoint(mousePos)

    def act_if_clicked(self, mousePos):
        global ACTIVE_TXTFIELD
        global KeyMode
        global K_TEXT_ENTER
        if (self.was_clicked(mousePos)):
            ACTIVE_TXTFIELD = self
            KeyMode = K_TEXT_ENTER
        elif (ACTIVE_TXTFIELD == self and pygame.mouse.get_pressed()[0]):
            ACTIVE_TXTFIELD = None
            KeyMode = K_NORMAL
            
            
'''Loads buttons, texts, and text inputs from a .json file'''
def load(inst, path):
    buttons = []
    texts = []
    #inputs = []
    with open(path, 'r') as f:
        filedata = json.load(f)
    #at this point we have the serialized objects
    #now we create objects from them
    for b in filedata['buttons']:
        #name, position, size, color=(0,0,255), text="", textColor=(255, 255, 255), onClick=None, txtSize = 36):
        pos = (b['position'][0], b['position'][1])
        size = (b['size'][0], b['size'][1])
        color = (b['color'][0], b['color'][1], b['color'][2])
        textColor = (b['textColor'][0], b['textColor'][1], b['textColor'][2])
        callbackTxt = b['callback']
        callback = None
        if callbackTxt != 'None' and inst:
            callback = getattr(inst, callbackTxt)
        #print(callbackTxt)
        #print(callback)
        button = Button(b['name'], pos, size, color, b['text'], textColor, callback, b['textSize'])
        if not inst and callbackTxt != 'None':
            button.CallbackTxt = callbackTxt
            #print('Setting CallbackTxt value')
        buttons.append(button)
        
    for t in filedata['texts']:
        #name, text, position, height=36, color=(0, 0, 0)):
        pos = (t['position'][0], t['position'][1])
        height = t['height']
        color = (t['color'][0], t['color'][1], t['color'][2])
        texts.append(Text(t['name'], t['text'], pos, height, color))

    return buttons, texts
