#-----------------------
# notify
#-----------------------

print('RUN: board_example.py')

#-----------------------
# networking
#-----------------------

# see /examples/network_example.py

# this is based on config.json and networks.csv
wlan.make_ready()

print('WLAN Connected:',wlan.isconnected)
print('WLAN Status:',wlan.status)
print('WLAN Signal:',wlan.rssi)
print('WLAN ESSID:',wlan.essid)
print('WLAN Hostname:',wlan.dhcp_hostname)
print('WLAN Mac Address:',wlan.mac_address)
print('WLAN IP Address:',wlan.ip_address)

# this is a good idea after you have www access
rtc.ntp_set()  

print('DTSTAMP:',rtc.dtstamp)
print('LINUX EPOCH:',rtc.linux_epoch)

#-----------------------
# sdcard
#-----------------------

# all functions are limited to sdcard
# sdcard.? won't write to flash

# sdcard should be FAT32 formated
# do this on your desktop

# if inserted at boot, it should already be mounted
sdcard.mount()

# list content
sdcard.tree()

# open file
try:
    with sdcard.open('testfile.txt','w') as f:
        f.write('This is the testfile line1.\nThis is line 2.\nThis is line 3.\n')
        f.close()
except:
    sdcard.error()

# print file = pf
sdcard.pf('testfile.txt')

# remove
sdcard.remove('testfile.txt')

# other functions
# sdcard.unmount()
# sdcard.mkdir(d)
# sdcard.rmdir(d) is dangerous
# sdcard.remove(f)
# sdcard.exists(fd)
# sdcard.isdir(d)
# sdcard.isfile(f)

#-----------------------
# led1
#-----------------------

print('BLINKING LED1')

led1.on()
led1.off()
led1.blink(10)

#-----------------------
# buzzer
#-----------------------

print('SOUNDS ON BEEPER')

import time

# beep one time
beeper.beep()
time.sleep_ms(500)

# beep n times
beeper.beepn(3)
time.sleep_ms(500)

# use a specific freq, duration, and %volume
beeper.beep(freq=880,secs=1,vol=50)
time.sleep_ms(500)

# beep that changes between 2 freqs
# you can also set secs and vol
beeper.beep2(1760,3520)
time.sleep_ms(100)
# freq2 = freq1 * 2
beeper.beep2(1760)
time.sleep_ms(500)

# play shave and a haircut (default)
beeper.play(vol=20)
time.sleep_ms(500)
# beeper.jingle()
# beeper.shave()
# beeper.axelf() (or crazy frog)

# play a string of note+octave+beats values
# you can also set root, beat (length), vol
# detaults are octave 4, beats 1, root=440, beat=0.125 secs
# C Major scale with a 2-beat pause and 2-beat end notes
beeper.play('c d e f g a b42 p2 c52',vol=20)

#-----------------------
# esp32
#-----------------------

print('ESP32 TEMP C:',esp32.temp)
print('ESP32 TEMP F:',esp32.tempf)
print('ESP32 HALL:',esp32.hall)
print('ESP32 MEMORY:',esp32.memory)
print('ESP32 FLASH:',esp32.flash)

# also esp32.reset

#-----------------------
# board
#-----------------------

print('BOARD NAME:',board.name)
print('BOARD DATE:',board.date)
print('BOARD TEMP C:',board.temp)
print('BOARD TEMP F:',board.tempf)
print('BOARD ORIENTATION:',board.orientation)

# low power sleep
board.sleep(5)

#-----------------------
# accelerometer
#-----------------------

print('ACC G-FORCES:',acc.gforces)
print('ACC ACCELERATION:',acc.acceleration)
print('ACC ANGLES:',acc.angles)

#-----------------------
# gps
#-----------------------

print('GPS LOCATION',gps.location)

#-----------------------
# can
#-----------------------

# see /examples/can_example.py

#-----------------------
# interrupts
#-----------------------

# three interrupts are set up for the board
# 'btn' is the button SW2 (GPIO0, PIN_LOAD)
# 'can' is the CAN interrupt (GPIO34, PIN_INTR1)
# 'acc' is the ACC interrupt (GPIO35, PIN_INTR2)
print('INT NAMES:',interrupts.names())

# using 'btn' as an example, the interrupt was created using
# >>> interrupts.add_falling_pin(PIN_LOAD,name='btn',samples=5,sample_period=10,callback2=None,show=True)
# it has a debounce function which takes 5 samples spaced 10ms apart
# push WS2 and you can see it on the REPL screen (show=True)
# it does not have a secondary callback function

# the primary callback augments the count in the dict interrupts.interrupts['btn']
print('INT btn CHECK:',interrupts.check('btn')) # boolean check for interrupts
print('INT btn GET:',interrupts.get('btn')) # get interrupt count and last time.time()

# you can artifically call an interrupt
print('INT btn CALL:',interrupts.call('btn'))
print('INT btn CHECK:',interrupts.check('btn'))
print('INT btn GET:',interrupts.get('btn'))

# you can add a secondary callback function
# the callback MUST accept a pin argument
callback2_function = lambda pin: print("LET'S ROCK N' ROLL!",end=' ')
print('INT btn MAKE CALLBACK2:',interrupts.set_callback2('btn',callback2=callback2_function))
print('INT btn CALL:',interrupts.call('btn'))
print('INT btn CHECK:',interrupts.check('btn'))
print('INT btn GET:',interrupts.get('btn'))

# undo secondary callback (set to None)
print('INT btn X CALLBACK2:',interrupts.set_callback2('btn',callback2=None))
del callback2_function

# clear
print('INT btn CLEAR:',interrupts.clear('btn'))
print('INT btn CHECK:',interrupts.check('btn'))
print('INT btn GET:',interrupts.get('btn'))
print('INT CLEAR ALL:',interrupts.clear())

# change raw interrupts dict
interrupts.interrupts['btn']['s']   = False # turn show (print to repl) off
interrupts.interrupts['btn']['s']   = True  # turn show (print to repl) on
interrupts.interrupts['btn']['cb2'] = None  # set callback2 to None
# don't mess with the rest

#-----------------------
# end
#-----------------------
