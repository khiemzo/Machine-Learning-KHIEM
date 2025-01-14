#-----------------------
# notify
#-----------------------

print('RUN: main.py')

#-----------------------
# general imports
#-----------------------

import os
import sys
import time

# add other imports here

#-----------------------
# protect main.py
#-----------------------

# main.py is called by uPython after boot.py
# this prevents main.py from failing and
# keeps the above imports available on the REPL

try:

    #-----------------------
    # network connect
    #-----------------------

    # see /lib/examples/network_example.py

    for x in range(3):
        if wlan.make_ready():
            break
        time.sleep_ms(100)

    for x in range(3):
        if rtc.ntp_set():
            break
        time.sleep_ms(500)

    #-----------------------
    # your scripts here
    #-----------------------

    beeper.shave(vol=50)

    while 1:
        led1.blink(1)
        time.sleep_ms(100)


        







    #-----------------------
    # end of scripts
    #-----------------------

    pass # placeholder

except KeyboardInterrupt:
    print('Keyboard Interrupt: main.py ending.')
    
except Exception as e:
    import sys
    sys.print_exception(e)
    print('Exception: main.py ending.')

#-----------------------
# end
#-----------------------
