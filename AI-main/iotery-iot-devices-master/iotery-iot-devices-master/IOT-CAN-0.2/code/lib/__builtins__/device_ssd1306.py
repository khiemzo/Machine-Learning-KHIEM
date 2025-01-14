#-----------------------
# notify
#-----------------------

print('LOAD: device_ssd1306.py')

#-----------------------
# imports
#-----------------------

import os,sys,time
import gc
import io

from math import sin, cos, radians
from machine import Pin
from machine import I2C

# these are based on clayton's old libraries
# they could use some improvements

# i have made some improvements, but... 
# i2c is dreadfully slow compared to spi
# but it works fine for simple things

#-----------------------
# general ssd1306
#-----------------------

# see i2c and spi classes below

class SSD1306:

    # Note: Some modules require 3.3V (charge pump is active). Will be blank with 5V.
    # See command below: Enable charge pump regulator 8Dh, 14h

    # FRAME:
    width = 128
    height = 64
    xoffset = 0 # partial frames are centered in the 1306 memory space
    yoffset = 0 # partial frames are in upper half of the 1306 memory space 

    # display variables 
    contrast_value = 255 # default to highest

    def __init__(self):

        self.frame = None
        gc.collect()

        self.pages  = self.height//8
        self.fbytes = self.width*self.pages
        self.frame  = bytearray(self.fbytes)
        self.xoffset = (128-self.width)//2

        print('INIT:',len(self.frame))

    #-------------------------------------------
    # ssd1306 init
    #-------------------------------------------

    def ssd1306init(self):

        # Set MUX Ratio A8h 3Fh
        # Set Display Offset D3h 00h
        # Set Display Start Line 40h
        # Set Segment re-map A0h/A1h
        # Set COM Output Scan Direction C0h/C8h
        # Set Contrast Control 81h 7Fh
        self.command((0x81,self.contrast_value))
        # Disable Entire Display On A4h
        self.command((0xA4,))       
        # Set Normal Display A6h
        self.command((0xA6,))
        # Set Osc Frequency D5h 80h
        # Enable charge pump regulator 8Dh, 14h
        self.command((0x8D,0x14))       
        # Set COM Pins hardware configuration DAh 02
        # Display On AFh
        self.command((0xAF,))

        # Set Memory Addressing Mode
        self.command((0x20,0x00)) # horizontal addressing
        self.command((0x21,self.xoffset,self.xoffset+self.width-1)) # row start,end # row start,end
        self.command((0x22,self.yoffset,self.yoffset+self.pages-1)) # page start,end

    #-------------------------------------------
    # set values
    #-------------------------------------------

    def contrast(self,c=None):
        if c != None:
            self.contrast_value = c
        self.command((0x81,self.contrast_value))

    def on(self):
        self.command((0xAF,))
    def off(self):
        self.command((0xAE,))

    def invert(self):
        self.command((0xA7,))
    def uninvert(self):
        self.command((0xA6,))

    # x-axis swap
    def mirror(self):
        self.command((0xA1,))
    def unmirror(self):
        self.command((0xA0,))

    # y-axis swap
    def flip(self):
        self.command((0xC8,))
        self.yoffset = 8 - self.pages
    def unflip(self):
        self.command((0xC0,))
        self.yoffset = 0

    # x and y axis swap
    def r180(self):
        self.mirror()
        self.flip()
    def unr180(self):
        self.unmirror()
        self.unflip()

    def port_clear(self):
        #self.writeto((0,) * self.fbytes) # inefficient memory management
        self.command((0x21,self.xoffset,self.xoffset+self.width-1))
        for p in range(self.pages):
            self.command((0x22,p,p))    
            self.port.writeto(self.addr,bytearray((0x40,))+bytearray(self.width))
    
    #-------------------------------------------
    # frame 
    #-------------------------------------------

    page_mod = [0]*8 # flag if page has changed

    def page_clear(self,n=1):

        n = min(8,max(1,n))
        
        for x in range((n-1)*self.width,n*self.width):
            self.frame[x] = 0

        self.page_mod[n-1] = 1

    def frame_clear(self):
        #self.frame = bytearray(self.fbytes) # inefficient memory management
        for x in range(self.fbytes):
            self.frame[x] = 0
        self.page_mod = [1]*8

    def frame_fill(self):
        #self.frame = bytearray((0xFF,)*self.fbytes) # inefficient memory management
        for x in range(self.fbytes):
            self.frame[x] = 255
        self.page_mod = [1]*8

    def frame_scroll(self,n=1):
        # scroll frame up n pages

        n = min(8,max(1,n))

        if n == 8:
            self.frame_clear()

        else:
            for x in range(0,(self.pages-n)*self.width):
                self.frame[x] = self.frame[x+(self.width*n)]
            for x in range((self.pages-n)*self.width,self.pages*self.width):
                self.frame[x] = 0
            self.page_mod = [1]*8

    def frame_show(self):

        # set start:end for row (same for both)
        self.command((0x21,self.xoffset,self.xoffset+self.width-1))
        
        if self.isi2c:
            for p in range(self.pages):
                if self.page_mod[p]:

                    # set start:end pages (just 1 page)
                    self.command((0x22,p,p))

                    # write only page data
                    self.port.writeto(self.addr,bytearray((0x40,))+self.frame[p*self.width:(p+1)*self.width])

        else:

            # set start:end pages
            self.command((0x22,self.yoffset,self.yoffset+self.pages-1))

            # write full frame
            self.writeto(self.frame)

        self.page_mod = [0]*8
    
    def bitset(self,X,Y,value=1):

        # full grid
        # starting from top-left corner as (1,1)
        # ending at bottom-right corner as (self.width,self.height)

        # values in range
        if 1 <= X <= self.width and 1 <= Y <= self.height:

            # r is the column, just X-1
            r = X-1

            # p is the page (0-7)
            p = (Y-1)//8

            # b is the bit (0-1)
            b = (Y-1)%8

            # B is the byte to change
            B = (p * self.width) + r

            # set
            if value:
                self.frame[B] |= (2**b)

            # clear
            else:
                self.frame[B] &= ~(2**b)

            # update pages mod
            self.page_mod[p] = 1

    def bitclear(self,X,Y,value=0):

        self.bitset(X,Y,0)

    #-------------------------------------------
    # shapes 
    #-------------------------------------------

    def hline(self,X,Y,L,value=1):
        if L >= 0:
            if value:
                for x in range(X,X+L+1):
                    self.bitset(x,Y)
            else:
                for x in range(X,X+L+1):
                    self.bitclear(x,Y)
        else:
            if value:
                for x in range(X,X+L-1,-1):
                    self.bitset(x,Y)
            else:
                for x in range(X,X+L-1,-1):
                    self.bitclear(x,Y)
            
    def vline(self,X,Y,L,value=1):
        if L >= 0:
            if value:
                for y in range(Y,Y+L+1):
                    self.bitset(X,y)
            else:
                for y in range(Y,Y+L+1):
                    self.bitclear(X,y)
        else:
            if value:
                for y in range(Y,Y+L-1,-1):
                    self.bitset(X,y)
            else:
                for y in range(Y,Y+L-1,-1):
                    self.bitclear(X,y)

    def line(self,X1,Y1,X2,Y2,value=1):

        if X1 == X2:
            self.vline(X1,Y1,Y2-Y1,value)

        elif Y1 == Y2:
            self.hline(X1,Y1,X2-X1,value)

        else:

            m = (Y2-Y1)/(X2-X1)
            b = Y1 - m*X1

            if abs(m) <= 1:

                X1 = int(round(X1,0))
                X2 = int(round(X2,0))

                if X1 > X2:
                    X1,X2 = X2,X1

                for x in range(X1,X2+1):
                    y = int(round(m*x+b,0))

                    if value:
                        self.bitset(x,y)
                    else:
                        self.bitclear(x,y)

            else:

                Y1 = int(round(Y1,0))
                Y2 = int(round(Y2,0))

                if Y1 > Y2:
                    Y1,Y2 = Y2,Y1

                for y in range(Y1,Y2+1):
                    x = int(round((y-b)/m,0))

                    if value:
                        self.bitset(x,y)
                    else:
                        self.bitclear(x,y)

    def ray(self,X,Y,length=32,angle=45,value=1,draw=True):

        angle *= -(6.2832/360)

        x = int(round(X+length*cos(angle),0))
        y = int(round(Y+length*sin(angle),0))

        if draw:
            self.line(X,Y,x,y,value)

        return x,y

    def rect(self,X1,Y1,X2,Y2,value=1):

        # rectangle from top-left to bottom-right
        
        self.hline(X1,Y1,X2-X1,value)
        self.hline(X1,Y2,X2-X1,value)
        self.vline(X1,Y1,Y2-Y1,value)
        self.vline(X2,Y1,Y2-Y1,value)

    def poly(self,X,Y,R,value=1,sides=8,start=0,end=360):

        # draw multiple lines (sides)
        # centered on (X,Y)
        # radius R is distance from (X,Y) to line ends
        # start and end are angles from (X,Y) to arc ends in degrees
        # start to end is always counter-clockwise in degrees
        # end must be > start

        # circles = start 0, end 360, sides big enough to be smooth

        if start > end:
            start,end = end,start
        arc = (end-start)
        sideangle = arc/sides

        lastx,lasty = self.ray(X,Y,R,start,draw=False)

        while start < end:

            start += sideangle

            nextx,nexty = self.ray(X,Y,R,start,draw=False)

            self.line(lastx,lasty,nextx,nexty,value)

            lastx,lasty = nextx,nexty

        return lastx,lasty

    #-------------------------------------------
    # text 
    #-------------------------------------------

    # size 7 (height 7 pixels) base font (can be scaled by whole numbers)
    font  = ['   XX XXX  XX XXX XXXXXXXX XX X  XXXX  XXX  XX   X   XX  X XX XXX  XX XXX  XX XXXXXX  XX   XX   XX   XX   XXXXXX XXX  X  XXX  XXX     XXXXXX XXX XXXXX XXX  XXX X       XXXXXX    X          X XXX  X X  XXX XX    X  XX   X   XX          XX  X X XX      X XXX ', '  X  XX  XX  XX  XX   X   X  XX  X X    XX X X   XX XXXX XX  XX  XX  XX  XX  X  X  X  XX   XX   XX   XX   X    XX   XXX X   XX   XX   XX    X   X    XX   XX   X X      X    XX   X    X     XX   XXXXXXX X XXX  XX XX  X XXX X  X        X  X X X X X    X X   X', '  X  XX  XX   X  XX   X   X   X  X X    XXX  X   X X XX XXX  XX  XX  XX  XX     X  X  XX   XX   X X X  X X    X X   X X     X    XX   XX    X       X X   XX   X     XXXX    X X X    X XXX  XX X X X X X X     X    X  X  X X    X    X  X  X XX     X  X     X ', '  XXXXXXX X   X  XXXX XXX X XXXXXX X    XXX  X   X   XX  XX  XXXX X  XXXX  XX   X  X  XX   XX X X  X    X    X  X   X X    X   XX XXXXXXXXX XXXX   X   XXX  XXXX  XXX   X    X X      X   XXXXX XX  X X  XXX   X      XX     X    X   XXXX    X        XX     X  ', '  X  XX  XX   X  XX   X   X  XX  X X    XX X X   X   XX  XX  XX   X  XX X    X  X  X  XX   XX X X X X   X   X   X   X X   X      X    X    XX   X X   X   X    X     XXXX    X X      X      XX    XXXXX  X X X      X   X   X    X    X  X  X X      X  X    X  ', '  X  XX  XX  XX  XX   X   X  XX  X X X  XX  XX   X   XX  XX  XX   X X X  XX  X  X  X  X X X XX XXX   X  X  X    X   X X  X   X   X    XX   XX   X X   X   XX   X        X    X  XX X X        X   X X X X X XX  XX   X  X     X  X        X  X XX    X    X      ', '  X  XXXX  XX XXX XXXXX    XXXX  XXXX XX X  XXXXXX   XX  X XX X    X XX  X XX   X   XX   X  X   XX   X  X  XXXXX XXX XXXXXXXX XXX     X XXX  XXX  X    XXX  XXX         XXXXXX   X XX        X XXX       XXX    XX    XX X     XX  XXX     XX  X    X      X  X  '] #
    chars = {'height': 7, 'gap': 1, 'invert': False, ' ': (' ', 2, 0), 'A': ('A', 4, 2), 'B': ('B', 4, 6), 'C': ('C', 4, 10), 'D': ('D', 4, 14), 'E': ('E', 4, 18), 'F': ('F', 4, 22), 'G': ('G', 4, 26), 'H': ('H', 4, 30), 'I': ('I', 3, 34), 'J': ('J', 4, 37), 'K': ('K', 4, 41), 'L': ('L', 4, 45), 'M': ('M', 5, 49), 'N': ('N', 4, 54), 'O': ('O', 4, 58), 'P': ('P', 4, 62), 'Q': ('Q', 4, 66), 'R': ('R', 4, 70), 'S': ('S', 4, 74), 'T': ('T', 5, 78), 'U': ('U', 4, 83), 'V': ('V', 5, 87), 'W': ('W', 5, 92), 'X': ('X', 5, 97), 'Y': ('Y', 5, 102), 'Z': ('Z', 5, 107), '0': ('0', 5, 112), '1': ('1', 3, 117), '2': ('2', 5, 120), '3': ('3', 5, 125), '4': ('4', 5, 130), '5': ('5', 5, 135), '6': ('6', 5, 140), '7': ('7', 5, 145), '8': ('8', 5, 150), '9': ('9', 5, 155), '`': ('`', 2, 160), '-': ('-', 3, 162), '=': ('=', 3, 165), '[': ('[', 3, 168), ']': (']', 3, 171), '\\': ('\\', 3, 174), ';': (';', 1, 177), "'": ("'", 1, 178), ',': (',', 1, 179), '.': ('.', 1, 180), '/': ('/', 3, 181), '~': ('~', 5, 184), '!': ('!', 1, 189), '@': ('@', 5, 190), '#': ('#', 5, 195), '$': ('$', 5, 200), '%': ('%', 5, 205), '^': ('^', 3, 210), '&': ('&', 5, 213), '*': ('*', 3, 218), '(': ('(', 3, 221), ')': (')', 3, 224), '_': ('_', 3, 227), '+': ('+', 3, 230), '{': ('{', 3, 233), '}': ('}', 3, 236), '|': ('|', 1, 239), ':': (':', 1, 240), '"': ('"', 3, 241), '>': ('>', 4, 244), '<': ('<', 4, 248), '?': ('?', 5, 252)} #
    
    def place_text(self,text,X,Y,scale=1,center=True,middle=True,value=1):

        # frames start in the top-left as (1,1)
        # frames end in the bottom-right as (128,64)
        # if not center, then left
        # if not middle, then top

        # unscaled
        char_height = self.chars['height']
        char_gap    = self.chars['gap'   ]

        text = str(text).upper()
        text = ''.join([c for c in text if c in self.chars])
        text = ' '.join(text.split())

        #print('TEXT:',[text],scale)

        if text:

            X = int(round(X,0))
            Y = int(round(Y,0))

            if middle:
                Y = max(Y-int(scale*char_height/2),1)

            if center:
                tlen = int((sum([self.chars[c][1] for c in text]) + (len(text)-1)*char_gap)*scale)
                X = max(X-tlen//2,1)
            
            xindex = 0           
            for c in text:
                c2,cwidth,cindex = self.chars[c]
                for x in range(cwidth):
                    cX = cindex + x
                    for xscale in range(scale):
                        tX = xindex + X
                        yindex = char_height * scale
                        for cY in range(char_height-1,-1,-1):
                            for yscale in range(scale):
                                if self.font[cY][cX] in ('X','#'): #
                                    tY = Y + yindex
                                    if value:
                                        self.bitset(tX,tY)
                                    else:
                                        self.bitclear(tX,tY)
                                yindex -= 1
                        xindex += 1
                xindex += int(char_gap*scale)
                if xindex + X >= self.width:
                    break

    def test(self,ontime=1000):
        self.frame_clear()
        self.rect(1,1,self.width,self.height,1)
        self.frame_show()
        self.place_text('iotery',64,32,scale=2,center=True,middle=True,value=1)
        self.frame_show()
        time.sleep_ms(int(ontime/3))
        self.invert()
        time.sleep_ms(int(ontime/3))
        self.uninvert()
        time.sleep_ms(int(ontime/3))
        self.frame_clear()
        self.frame_show()

#-----------------------
# I2C option
#-----------------------

class SSD1306_I2C(SSD1306):

    # is I2C
    isi2c = True
    isspi = False

    # I2C pins
    scl = 22
    sda = 21

    # I2C port
    port = 1
    freq = 100000 # low rate to start (try x4 for max)
    addr = None

    # command buffer
    cbuffer = bytearray(2)
    cbuffer[0] = 0x80 # Co=1, D/C#=0

    # open port
    def port_open(self,test=True):

        # port
        #self.port = I2C(self.port,scl=Pin(self.scl),sda=Pin(self.sda),freq=self.freq)
        self.port = I2C(scl=Pin(self.scl),sda=Pin(self.sda),freq=self.freq)

        # scan for address
        for x in self.port.scan():
            print('ADDR:',x)
            if not self.addr:
                self.addr = x

        # setup ssd1306
        self.ssd1306init()
        self.port_clear()

        # test
        if test:
            self.test()

    # port close
    def port_close(self):

        # setup
        self.port_clear()
        self.off()        

        # port
        try:
            self.port.deinit()
        except:
            pass
        del self.port

    # write command buffer to port
    def command(self,buffer):

        b = bytearray(buffer)
        for c in b:
            self.cbuffer[0] = 0x80
            self.cbuffer[1] = c
            self.port.writeto(self.addr,self.cbuffer)

    # write data buffer to port
    def writeto(self,buffer):
        self.port.writeto(self.addr,bytearray((0x40,))+bytearray(buffer))

    #-----------------------
    # FTREE
    #-----------------------

    def do_trees(self,unr180=True):

        self.repl_disconnect()

        import device_ftree

        # un-rotate screen 180
        if unr180:
            self.unr180()

        ft = device_ftree.FTree()
        ft.canvas_width = self.width
        ft.canvas_height = self.height

        try:

            while 1:

                self.frame_clear()

                # for i2c, prevents too many shows
                show_every = 2

                bc = 0
                for x,y in ft.rtree(64,0): # start point
                    self.bitset(x,y)
                    bc += 1
                    if not bc % show_every:
                        self.frame_show()
                self.frame_show()

                time.sleep_ms(1000)
                self.port_clear()
                time.sleep_ms(250)

        except KeyboardInterrupt:
            pass

        # clear
        self.frame_clear()
        self.port_clear()

        # re-rotate screen 180
        if unr180:
            self.r180()        

    #-----------------------
    # REPL
    #-----------------------

    def repl_connect(self):
        self.repl_disconnect()
        self.stream = STREAM(self)
        os.dupterm(self.stream)

    def repl_disconnect(self):
        os.dupterm(None)
        self.stream = None

#-----------------------
# IO stream class
#-----------------------

class STREAM(io.IOBase):

    # base = https://github.com/micropython/micropython/blob/master/examples/bluetooth/ble_uart_repl.py

    line = []

    def __init__(self,device):
        self.device = device

    def _on_rx(self):
        # for ESP32
        if hasattr(os,'dupterm_notify'):
            os.dupterm_notify(None)

    def read(self,sz=None):
        print('1306 STREAM READ:',[sz])
        return b''
        ##return self._uart.read(sz)

    def readinto(self,buffer):
        print('1306 STREAM READINTO:',[len(buffer)])
        return None
        ##avail = self._uart.read(len(buf))
        ##if not avail:
        ##    return None
        ##for i in range(len(avail)):
        ##    buf[i] = avail[i]
        ##return len(avail)

    def ioctl(self,op,arg):
        print('1306 STREAM IOCTL:',[op,arg])
        return 0
        ##if op == _MP_STREAM_POLL:
        ##    if self._uart.any():
        ##        return _MP_STREAM_POLL_RD
        ##return 0

    def _flush(self):
        print('1306 STREAM FLUSH')
        pass
        ##data = self._tx_buf[0:100]
        ##self._tx_buf = self._tx_buf[100:]
        ##self._uart.write(data)
        ##if self._tx_buf:
        ##    schedule_in(self._flush, 50)

    def write(self,buffer):

        try:

            text = buffer.decode('ascii')
            wrapped = False

            for c in text:
                
                while len(self.line) >= 20:
                    self.writeit(''.join(self.line[:20]))
                    self.line = self.line[20:]
                    self.device.frame_scroll()
                    wrapped = True

                if c in '\r\n':
                    if self.line and not wrapped:
                        self.writeit(''.join(self.line))
                        self.line = []
                        self.device.frame_scroll()
                    
                else:
                    self.line.append(c)

                self.wrapped = False

            while len(self.line) > 20:
                self.writeit(''.join(self.line[:20]))
                self.line = self.line[20:]
                self.device.frame_scroll()

            self.writeit(''.join(self.line))

        except Exception as e:
            sys.print_exception(e)

        return len(buffer)

        # causes print-to-screen loop: print('1306 STREAM WRITE:',[buffer])       
        ##empty = not self._tx_buf
        ##self._tx_buf += buf
        ##if empty:
        ##    schedule_in(self._flush, 50)

    def writeit(self,text):
        self.device.page_clear(self.device.pages)
        self.device.place_text(text,1,self.device.height-7,1,0,0)
        self.device.frame_show()

#-----------------------
# end
#-----------------------

###-----------------------
### SPI option
###-----------------------
##
##class SSD1306_SPI(SSD1306):
##
##    ### UNTESTED ###
##    # this was broght over from another clayton library
##
##    global SPI
##    from machine import SPI
##
##    # is spi
##    isi2c = False
##    isspi = True
##
##    # SPI pins (including cs and dc, miso is not used)
##    mosi = 13
##    sck  = 14
##    cs   = 15
##    dc   = 33 # this is a data/command switch used by the ssd1306
##    res  = 21
##
##    # SPI port
##    port = 1
##    baudrate = 10 * 1024 * 1024 # low rate to start (try x8 for max)
##    polarity = 0
##    phase = 0
##    bits = 8
##    firstbit = SPI.MSB
##
##    # init
##    def __init__(self):
##        pass
##
##    # open port
##    def port_open(self,test=True):
##
##        # RES
##        if self.res:
##            self.RES = Pin(self.res,mode=Pin.OUT)
##            self.RES.value(1)
##            time.sleep_ms(1)
##            self.RES.value(0)
##            time.sleep_ms(10)
##            self.RES.value(1)
##
##        # port
##        self.port = SPI(self.port,baudrate=self.baudrate,polarity=self.polarity,phase=self.phase,bits=self.bits,firstbit=self.firstbit,sck=Pin(self.sck),mosi=Pin(self.mosi))
##
##        # CS
##        self.CS = Pin(self.cs,mode=Pin.OUT)
##        self.CS.value(1)
##
##        # DC
##        self.DC = Pin(self.dc,mode=Pin.OUT)
##        self.DC.value(1)
##
##        # setup ssd1306
##        self.ssd1306init()
##        self.port_clear()
##
##        # test
##        if test:
##            #self.port_test()
##            self.hypno()
##
##    # port close
##    def port_close(self):
##
##        # setup
##        self.port_clear()
##        self.off()        
##
##        # port
##        self.port.deinit()
##        del self.port
##
##        # CS
##        Pin(self.cs,mode=Pin.IN)
##
##        # DC
##        Pin(self.dc,mode=Pin.IN)
##
##    # write command buffer to port
##    def command(self,buffer):
##        b = bytearray(buffer)
##        print('COMMAND:',b)
##        self.CS.value(1)
##        self.DC.value(0)
##        self.CS.value(0)
##        self.port.write(b)
##        self.CS.value(1)
##        self.DC.value(1)
##
##    # write data buffer to port
##    def writeto(self,buffer):
##        self.CS.value(1)
##        self.DC.value(1)
##        self.CS.value(0)
##        self.port.write(bytearray(buffer))
##        self.CS.value(1)

