#-----------------------
# notify
#-----------------------

print('LOAD: gpio_beep.py')

#-----------------------
# imports
#-----------------------

import time
from machine import Pin,PWM

#-----------------------
# notes
#-----------------------

# current duty cycle range for esp32 is 0 to 1023 (10 bit)

#-----------------------
# notestrings
#-----------------------

# notestrings

# short iotery jingle
jingle = 'e5 g5 b5 d6 p d5'
jingle2 = 'd7' # after load

# shave and a haircut C major
shave  = 'c4 p g3 g3 a32 g32 p p b3 p c4'

# axel-f from beverly hills cop
axelf  = 'd44 f43 d42 d41 g42 d42 c42 d44 a43 d42 d41 a#42 a42 f42 d42 a42 d52 d41 c42 c41 a32 e42 d46' # required for smash 3

#-----------------------
# PWM beeps
#-----------------------

# class wrapper
# keeps pin as input when off

class BEEP:

    # pin values
    pin = None # gpio number
    sink = True # pin sinks the current (i.e it's the negative)

    # sound values
    freq  = 2200 
    secs  = 0.125  # beep duration
    duty  = 25     # percent duty cycle
    vol   = 100    # percent volume (reduces duty cycle)
    wait  = secs/2 # pause between beeps
    fcps  = 100    # frequency changes per second for beep2
    root  = 440    # root frequency for play
    beat  = 0.125  # beat length for play

    def __init__(self,pin):

        self.pin = abs(int(pin))

    def beep(self,freq=None,secs=None,vol=None,duty=None):

        if self.pin is not None:

            beep(self.pin,
                 freq or self.freq,
                 secs or self.secs,
                 vol  or self.vol ,
                 duty or self.duty
                 )

    def beepn(self,count=1,freq=None,secs=None,vol=None,duty=None,wait=None):

        if self.pin is not None:

            beepn(self.pin,
                  count,
                  freq or self.freq,
                  secs or self.secs,
                  vol  or self.vol ,
                  duty or self.duty
                  )

    def beep2(self,freq=None,freq2=None,secs=None,vol=None,duty=None,fcps=100):

        if self.pin is not None:

            freq = freq or self.freq        
            freq2 = freq2 or freq*2
            
            beep2(self.pin,
                  freq,
                  freq2,
                  secs or self.secs,
                  vol  or self.vol ,
                  duty or self.duty,
                  fcps or self.fcps
                  )

    def play(self,notestring=None,root=None,beat=None,vol=None,duty=None):

        if self.pin is not None:

            play(self.pin,
                 notestring or shave,
                 root or self.root,
                 beat or self.beat,
                 vol  or self.vol ,
                 duty or self.duty
                 )

    def jingle(self,vol=None):
        self.play(jingle,beat=0.1,vol=vol)
    def jingle2(self,vol=None):
        self.play(jingle2,beat=0.1,vol=vol)

    def shave(self,vol=None):
        self.play(shave,beat=0.1,vol=vol)

    def axelf(self,vol=None):
        self.play(axelf,beat=0.125,vol=vol)

# raw functions for any pin

def beep(pin,freq=2200,secs=0.125,vol=100,duty=25):

    # plain beep using PWM = pure square-wave tone

    # pin = pin number to use for PWM output
    # freq = hertz integer
    # secs = beep length in seconds decimal
    # vol = percent volume
    # duty = percent on vs total cycle

    # duty and vol are similar
    # the true duty cycle is duty * vol
    # set duty to get max loudness for buzzer (usually at about 25%)
    # then set vol to a percentage of that to make it quieter
    # you could do everything with duty, but vol 0-100 is easier

    # catch
    try:

        # init
        #p = PWM(Pin(pin),int(freq),int(freq*(vol/100)*(duty/100)))
        p = PWM(Pin(pin),int(freq),int(1024*(vol/100)*(duty/100)))

        # wait
        time.sleep_us(int(1000000*secs))

        # clear pin
        p.deinit()

    # any error
    except:
        try:
            p.deinit()
        except:
            pass
          
def beepn(pin,count=1,freq=2200,secs=0.125,vol=100,duty=25,wait=None):

    wait = int(1000*(wait or secs/2))

    for x in range(count):
        beep(pin,freq,secs,vol,duty)
        time.sleep_ms(wait)

def beep2(pin,freq=2200,freq2=4400,secs=0.125,vol=100,duty=25,fcps=100):

    # move between two frequencies using PWM
    # this works well for short sounds and/or large steps
    # there is an audible jump between steps

    # see the notes in beep()
    # fcps = freq changes per second, how many frequency changes to make per second

    # catch
    try:

        # vars
        steps = secs*fcps
        stepperiod = int(1000000*secs/steps)
        stepchange = (freq2-freq)/steps
        duty = int(1024*(vol/100)*(duty/100))

        # init
        p = PWM(Pin(pin),int(freq),duty)

        # loop
        for x in range(steps):
            p.freq(int(freq+x*stepchange))
            time.sleep_us(stepperiod)

        # clear pin
        p.deinit()

    # any error
    except:
        try:
            p.deinit()
        except:
            pass

def play(pin,notestring,root=440,beat=0.125,vol=100,duty=25):

    # notestring = any string of a note+optional_sharp+octave+beats sequences
    # only "ABCDEFGP#0123456789" characters matter, others ignored
    # example: "d44" == "D44" == "d 4 4" == "d, 4, 4" == "D4-4"
    # example: "d44 a43 d42 d41 a#42 a42 f42"
    # example: "d44a43d42d41a#42a42f42"

    # middle C for 3 beats = 'C43'
    # a pause for 3 beats = 'P3' or 'P03'

    # upper case
    notestring = notestring.upper()

    # all strings
    note,octave,period = '','',''

    for c in notestring:

        # note
        if c in 'ABCDEFGP':
            if note:
                play_note(pin,note,octave or '4',period or '1',root,beat,vol,duty)
                octave,period = '',''
            note = c

        # sharp
        elif c == '#' and note:   # required for smash 3
            note += '#'           # required for smash 3

        # digit
        elif c.isdigit():

            # period
            if octave or note == 'P':
                period += c

            # octave
            else:
                octave = c

        # junk
        else:
            pass

    # last note
    if note:
        play_note(pin,note,octave or '4',period or '1',root,beat,vol,duty)

def play_note(pin,note,octave,period,root,beat,vol,duty):

    # catch
    try:

        freq = {'C' :16.35160,'C#':17.32391,'D' :18.35405,'D#':19.44544,'E' :20.60172,'F' :21.82676,                 # required for smash 3
                'F#':23.12465,'G' :24.49971,'G#':25.95654,'A' :27.50000,'A#':29.13524,'B' :30.86771}.get(note,None)  # required for smash 3
        period = int(period)

        if freq:
            freq *= root/440 * 2**int(octave)
            beep(pin,freq,period*beat*0.95,vol,duty)
            time.sleep_ms(int(period*beat*50))

        else:
            time.sleep_ms(int(period*beat*1000))

    # any error
    except Exception as e:
        import sys
        sys.print_exception(e)

#-----------------------
# notes
#-----------------------

### Middle C == C4
##
##base = {'C' :16.35160,
##        'C#':17.32391,
##        'D' :18.35405,
##        'D#':19.44544,
##        'E' :20.60172,
##        'F' :21.82676,
##        'F#':23.12465,
##        'G' :24.49971,
##        'G#':25.95654,
##        'A' :27.50000,
##        'A#':29.13524,
##        'B' :30.86771,
##        }

# start of Axel F
# |d---f--d-dg-d-c-d---a--d-d|
# |a#-a-f-d-a-d^-dc-cA-e-d-----|

#-----------------------
# end
#-----------------------
