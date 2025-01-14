#-----------------------
# notify
#-----------------------

print('RUN: boot.py')

#-----------------------
# board setup
#-----------------------

import sys
for path in (
    '/lib',
    '/lib/__builtins__',
    '/lib/examples',
    '/lib/applications'):
    if not path in sys.path:
        sys.path.append(path)

# basic setup of board devices
import board_iotcan02 as _board

# make board devices available everywhere
# adds devices to highest-level namespace
import builtins

builtins.esp32      = _board.esp32      # class
builtins.board      = _board.board      # class
builtins.led1       = _board.led1       # class
builtins.beeper     = _board.beeper     # class
builtins.sdcard     = _board.sdcard     # class
builtins.spibus     = _board.spibus     # class
builtins.interrupts = _board.interrupts # class
builtins.acc        = _board.acc        # class
builtins.can        = _board.can        # class
builtins.gps        = _board.gps        # class

#-----------------------
# wlan object setup
#-----------------------

from system_networks import WLAN
builtins.wlan = WLAN()

import system_rtc
builtins.rtc = system_rtc.RTCTOOLS()

#-----------------------
# sockethop.com setup
#-----------------------

import system_sockethop
builtins.hop = system_sockethop.RSOCK()

#-----------------------
# system tools setup
#-----------------------

import system_tools as st
builtins.st = st 

#-----------------------
# config setup
#-----------------------

builtins.config = {}
if st.isfile('config.json'):
    import ujson as json
    try:
        with open('config.json') as f:
            config = json.load(f)
        builtins.config = config
    except:
        builtins.config = {}
        print('ERROR: global config.json did not parse.')
    del json

#-----------------------
# user sys setup/cleanup
#-----------------------

del builtins

st.memp()

#-----------------------
# end
#-----------------------
