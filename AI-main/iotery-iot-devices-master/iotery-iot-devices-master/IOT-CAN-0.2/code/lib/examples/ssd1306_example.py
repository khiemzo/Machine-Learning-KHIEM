#-----------------------
# notify
#-----------------------

print('LOAD: ssd1306_example.py')

#-----------------------
# imports
#-----------------------

import time
import gc
import device_ssd1306
import device_ftree

#-----------------------
# setup
#-----------------------

# the buffer is big, so clear memory as much as possible
gc.collect()

# make oled device
oled = device_ssd1306.SSD1306_I2C()

# change pins (these are the defaults)
oled.scl = 22
oled.sda = 21

# change baud 100K is default, 400K generally works
oled.baudrate = 400000

# set screen resolution position
# 1306 defaults to 128x64 (it's max value)

# use these for smaller
oled.width = 128
oled.height = 64
oled.xoffset = 0
oled.yoffset = 0

# do this if if you changed screen size
oled.__init__()

# open the port
oled.port_open(test=False)

# set display values
oled.contrast(255) # brightness 0 to 255
oled.r180() # rotate screen 180
# oled.unr180() # un-rotate screen 180
# also flip, unflip, mirror, unmirror, invert, uninvert

# run a test pattern
oled.test()

# clear screen to start
oled.frame_clear() # this clears the frame
oled.frame_show() # this pushes the frame to the device

#-----------------------
# connect to REPL
#-----------------------

oled.repl_connect()
for x in range(11):
    print('hello repl',x)
oled.repl_disconnect()
oled.frame_clear()
oled.frame_show()

#-----------------------
# basic functions
#-----------------------

# (1,1) is the top left
# (128,64) is the bottom right

# oled.on() # turns oled on
# oled.off() # turns oled off
# oled.port_clear() # clear the oled (not the internal frame)

# oled.frame_clear() # clears internal display buffer (not the oled)
# oled.frame_fill()  # fills the internal display buffer
# oled.frame_show()  # sends internal frame to the oled

# oled.bitset(x,y)
# oled.bitclear(x,y)

#-----------------------
# shapes
#-----------------------

# oled.hline(X,Y,L,value=1) # horizontal line from XY length L
# oled.vline(X,Y,L,value=1) # vertical

# oled.line(X1,Y1,X2,Y2,value=1) # line between two points
# oled.ray(X,Y,length=32,angle=45,value=1) # ray

# oled.rect(X1,Y1,X2,Y2,value=1) # rectangle between opposite corners

# oled.poly(X,Y,R,value=1,sides=8,start=0,end=360) # center XY, radius, sides, start angle, end angle
# use a poly to draw an approx circle

# hint: draw the same object a second time with value=0 to remove it and not the whole frame

#-----------------------
# text
#-----------------------

# 1: clear the frame
# 2: place your text
# 3: send frame to oled (show)

# (0,0) is the top left
# base your text (x,y) on this

# base font is 7 pixels tall
# can be scaled by whole numbers
# if not center, then top
# if not middle, then left
# value == 1 == pixels on

# if line is too long to display
# right side is truncated (i.e. no wrap)

time.sleep_ms(250)

oled.frame_clear()
oled.place_text('Tiny'   ,64,14,scale=2,center=True,middle=True,value=1)
oled.place_text('Fractal',64,32,scale=2,center=True,middle=True,value=1)
oled.place_text('Trees'  ,64,50,scale=2,center=True,middle=True,value=1)
oled.frame_show()

time.sleep_ms(1000)
oled.port_clear()

oled.frame_clear()
oled.place_text('ESP32',64,32,scale=4,center=True,middle=True,value=1)
oled.frame_show()

time.sleep_ms(1000)
oled.port_clear()

oled.frame_clear()
oled.place_text('OLED',64,16,scale=3,center=True,middle=True,value=1)
oled.place_text('128x64 0.96in',64,48,scale=1,center=True,middle=True,value=1)
oled.frame_show()

time.sleep_ms(1000)
oled.port_clear()

#-----------------------
# fractal trees
#-----------------------

try:
    oled.do_trees()
except KeyboardInterrupt:
    pass

#-----------------------
# done
#-----------------------

oled.port_close()
oled.frame_clear()

#-----------------------
# end
#-----------------------
