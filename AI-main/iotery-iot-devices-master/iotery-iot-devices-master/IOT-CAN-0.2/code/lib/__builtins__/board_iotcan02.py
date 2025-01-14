#-----------------------
# notify
#-----------------------

print('RUN: setup_iotcan02.py')

#-----------------------
# define board constants
#-----------------------

from micropython import const

# moving counter-clockwise around the ESP module from the EN pin
PIN_GPI36    = const(36) # HALL SENSOR_VP, 16 pin header
PIN_GPI39    = const(39) # HALL SENSOR_VN, 16 pin header
PIN_VSYS     = const(34) # system voltage
PIN_CONINPUT = const(35) # jst connector input
PIN_LED1     = const(32) # LED1
PIN_CANINT   = const(33) # 
PIN_CANCS    = const(25) # 
PIN_ACCINT   = const(26) # 
PIN_ACCCS    = const(27) # 
PIN_SCL      = const(14) # SPI BUS
PIN_MISO     = const(12) # SPI BUS
PIN_MOSI     = const(13) # SPI BUS
PIN_MANRST   = const(15) # 
PIN_CONSINK  = const( 2) # jst connector sink
PIN_LOAD     = const( 0) # LOAD (low on boot to program), BUTTON
PIN_BUZZER   = const( 4) # 
PIN_RX1      = const(16) # GPS UART
PIN_TX1      = const(17) # GPS UART
PIN_SD_CS    = const( 5) # SDCard
PIN_SD_SCL   = const(18) # SDCard
PIN_SD_MISO  = const(19) # SDCard
PIN_GPIO21   = const(21) # 16 pin header
PIN_GPIO22   = const(22) # 16 pin header
PIN_SD_MOSI  = const(23) # SDCard

# can values
CAN_OSC = const( 16) # CAN bus osc freq in Mhz 
CAN_NBR = const(125) # CAN bus NBR in Kbps

BOARD_NAME = 'IOT-CAN-0.2'
BOARD_DATE = '2020-08-24'

print('BOARD SETUP: {} {}'.format(BOARD_NAME,BOARD_DATE))

#-----------------------
# immediate UI feedback
#-----------------------

# turn on blue led (led1)

from machine import Pin
Pin(PIN_LED1,Pin.OUT,value=1)

#-----------------------
# esp32 object 
#-----------------------

import os
import gc
from esp32 import raw_temperature
from esp32 import hall_sensor

class ESP32:

    @property
    def reset(self):
        print('HARDWARE RESET')
        time.sleep_ms(100)
        if PIN_MANRST:
            Pin(PIN_MANRST,Pin.OUT,value=0)
        return False

    @property
    def temp(self):
        return raw_temperature()

    @property
    def tempf(self):
        return raw_temperature()*1.8 + 32

    @property
    def hall(self):
        try:
            return hall_sensor()
        except:
            return 0

    @property
    def memory(self):
        gc.collect()
        free = gc.mem_free()
        used = gc.mem_alloc()
        return {'free':free,
                'used':used,
                'total':free+used,
                'perc':round(100*used/(free+used),2)}

    @property
    def flash(self):
        bsize,frsize,blocks,bfree,bavail,files,ffree,favail,flag,namemax = os.statvfs('/')
        size = bsize * blocks
        free = bsize * bfree
        return {'free':free,
                'used':size-free,
                'total':size,
                'perc':round(100*(size-free)/size,2)}
    
esp32 = ESP32()

#-----------------------
# hardware reset
#-----------------------

from machine import reset_cause
reset_cause = reset_cause()
print('LAST RESET:',{
    # machine.PWRON_RESET     = 1
    # machine.HARD_RESET      = 2
    # machine.WDT_RESET       = 3
    # machine.DEEPSLEEP_RESET = 4
    # machine.SOFT_RESET      = 5
    1: 'POWERON',
    2: 'HARDWARE',
    3: 'WATCHDOG',
    4: 'DEEPSLEEP',
    5: 'SOFTWARE'}.get(reset_cause,'UNKNOWN'))

# software resets DO NOT clear peripherals
# machine.reset() and WDT don't do full resets either
if reset_cause >= 3:
    esp32.reset

#-----------------------
# UI feedback objects
#-----------------------

from gpio_beep import BEEP
beeper = BEEP(PIN_BUZZER)
beeper.jingle(vol=20) # I'm awake!

from gpio_leds import LED
led1 = LED(PIN_LED1)

#-----------------------
# additional imports
#-----------------------

import os
import sys
import time
import gc

from machine import lightsleep

from gpio_spi  import SPIBUS
from gpio_ints import INTS

import device_sdcard 
import device_lis3dh
import device_mcp2515
import device_gps

# garbage collect post import
gc.collect()

#-----------------------
# sdcard SPI bus 2 
#-----------------------

sdcard = device_sdcard.SDCARD()
sdcard.mount()

#-----------------------
# devices SPI bus 1 
#-----------------------

spibus = SPIBUS() # default is HSPI (ID 1)
spibus.baudrate = 10000000 # max for board bus devices
spibus.open()

# init all cs pins (default high = un-select)
# do this so they are high and don't cause a select crash
can_cs = spibus.cs_make(PIN_CANCS)
acc_cs = spibus.cs_make(PIN_ACCCS)

#-----------------------
# interrupts setup 
#-----------------------

interrupts = INTS()

# pin0 button interrupt (on pin 0)
interrupts.add_falling_pin(PIN_LOAD,'btn')

# can interrupt on PIN_INTR1
# define this elsewhere
#interrupts.add_falling_pin(PIN_CANINT,'can')

# acc interrupt on PIN_INTR2
# define this elsewhere
#interrupts.add_falling_pin(PIN_ACCINT,'acc')

#-----------------------
# accelerometer 
#-----------------------

acc = device_lis3dh.LIS3DH(spibus,acc_cs)
acc.or_tipped = 10
acc.or_fallen = 30
acc.or_error  = 80
print('ACC CS:',PIN_ACCCS)
print('ACC INIT:',acc.spiok)

#-----------------------
# can bus
#-----------------------

can = device_mcp2515.MCP2515(spibus,can_cs,set_config=False)
can.osc = CAN_OSC
can.nbr = CAN_NBR
can.reset()
can.set_config()
print('CAN CS:',PIN_CANCS)

#-----------------------
# gps 
#-----------------------

gps = device_gps.L80R_Serial()
gps.port_open() # use detaults
gps.reset() # use detaults (hot)

#-----------------------
# board object 
#-----------------------

class BOARD:  

    def sleep(self,secs):

        # go to sleep()
        print('BOARD SLEEP (power save mode) for {} seconds.'.format(secs),end=' ')
        if secs >= 60:
            gps.sleep()
        can.set_mode('sleep')
        print('ASLEEP...',end=' ')
        time.sleep_ms(100)

        # sleep esp32
        lightsleep(int(max(1,secs)*1000-100))

        # wake
        print('WAKING...',end=' ')
        can.set_mode('normal')
        gps.wake()
        print('AWAKE')

    @property
    def orientation(self):
        return acc.orientation

    @property
    def name(self):
        return BOARD_NAME

    @property
    def date(self):
        return BOARD_DATE

    @property
    def temp(self):
        return acc.temp

    @property
    def tempf(self):
        return acc.tempf

    def set_temp(self,t):
        return acc.set_temp(t)

    def set_tempf(self,t):
        return acc.set_tempf(t)

    # pin values
    GPI36 = PIN_GPI36
    GPI39 = PIN_GPI39
    VSYS = PIN_VSYS
    CONINPUT = PIN_CONINPUT
    LED1 = PIN_LED1
    CANINT = PIN_CANINT
    CANCS = PIN_CANCS
    ACCINT = PIN_ACCINT
    ACCCS = PIN_ACCCS
    SCL = PIN_SCL
    MISO = PIN_MISO
    MOSI = PIN_MOSI
    MANRST = PIN_MANRST
    CONSINK = PIN_CONSINK
    LOAD = PIN_LOAD
    BUZZER = PIN_BUZZER
    RX1 = PIN_RX1
    TX1 = PIN_TX1
    SD_CS = PIN_SD_CS
    SD_SCL = PIN_SD_SCL
    SD_MISO = PIN_SD_MISO
    GPIO21 = PIN_GPIO21
    GPIO22 = PIN_GPIO22
    SD_MOSI = PIN_SD_MOSI

board = BOARD()

#-----------------------
# ready 
#-----------------------

# final garbage collect
gc.collect()

# let user know
print('BOARD IS READY')
beeper.jingle2()
led1.off()

#-----------------------
# end
#-----------------------
