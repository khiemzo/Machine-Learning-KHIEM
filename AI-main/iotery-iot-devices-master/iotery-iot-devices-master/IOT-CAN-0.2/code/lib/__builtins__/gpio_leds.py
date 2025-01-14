#-----------------------
# notify
#-----------------------

print('LOAD: gpio_leds.py')

#-----------------------
# imports
#-----------------------

import sys,time
from machine import Pin
from neopixel import NeoPixel

#-----------------------
# plain LEDs 
#-----------------------

# class wrapper
# keeps pin as input when off

class LED:

    # pin values
    pin = None # gpio number
    anode = True # led anode is connected to gpio

    # blink values
    ontime = 50
    offtime = 250

    def __init__(self,pin,anode=True,initon=False):

        self.pin = abs(int(pin))

        if not anode:
            self.anode = False

        if initon:
            self.on()

    def on(self):

        if self.pin is not None:

            if self.anode:
                Pin(self.pin,Pin.OUT,value=1)

            else:
                Pin(self.pin,Pin.OUT,value=0)

    def off(self):

        if self.pin is not None:
            Pin(self.pin,Pin.IN,pull=None)

    def blink(self,count=1,ontime=None,offtime=None):

        if not ontime:
            ontime = self.ontime

        if not offtime:
            offtime = self.offtime

        for x in range(count):

            self.on()
            time.sleep_ms(ontime)

            self.off()
            time.sleep_ms(offtime)

# blink any pin shortcut function
def blink(pin,count=1,ontime=22,offtime=220,anode=True):
    LED(pin,anode).blink(count,ontime,offtime)

#-----------------------
# neopixel class
#-----------------------

class NP:

    # brightness out of 255
    brightness = 32

    # name: color tuples
    # bold colors
    colors = {
        'blue': (0, 0, 255),
        'deepbluegatoraide': (0, 32, 255),
        'bluegatoraide': (0, 127, 255),
        'cyan': (0, 255, 255),
        'aqua': (0, 255, 127),
        'electricmint': (0, 255, 32),
        'green': (0, 255, 0),
        'electriclime': (32, 255, 0),
        'greenyellow': (127, 255, 0),
        'yellow': (255, 255, 0),
        'orange': (255, 127, 0),
        'electricpumpkin': (255, 32, 0),
        'red': (255, 0, 0),
        'deeppink': (255, 0, 32),
        'pink': (255, 0, 127),
        'magenta': (255, 0, 255),
        'purple': (127, 0, 255),
        'deeppurple': (32, 0, 255),
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'off': (0, 0, 0),
        }

    # init
    def __init__(self,pin,pixels):

        self.pin = pin
        self.p = Pin(self.pin,Pin.OUT)

        self.pixels = pixels
        self.np = NeoPixel(self.p,self.pixels)

    # all off
    def off(self):

        for pixel in range(self.pixels):
            self.np[pixel] = (0,0,0)

        self.np.write()

    # kill
    def kill(self):

        self.off()
        Pin(self.pin,Pin.IN,Pin.PULL_UP)

    # brightness reset
    def set_brightness(self,brightness=0):

        self.brightness = min(255,abs(brightness))

        self.np.write()

    # get a color
    def get_color(self,color):

        # leave color tuples as is
        if type(color) in (list,tuple):
            return tuple(list(color)+[0,0,0])[:3]

        # get text color value
        color = ''.join(str(color).split())
        value = self.colors.get(color,(255,255,255))

        # scale
        return tuple([int(x*self.brightness/255) for x in value])

    # set a pixel
    def setp(self,pixel,color):

        self.np[min(pixel,self.pixels-1)] = self.get_color(color)

        self.np.write()

#-----------------------
# end
#-----------------------
