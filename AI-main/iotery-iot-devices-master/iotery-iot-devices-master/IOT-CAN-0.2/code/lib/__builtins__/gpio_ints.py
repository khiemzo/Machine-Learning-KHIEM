#-----------------------
# notify
#-----------------------

print('LOAD: gpio_ints.py')

#-----------------------
# imports
#-----------------------

import time
from machine import Pin
from micropython import alloc_emergency_exception_buf

#-----------------------
# interrupt handler class
#-----------------------

class INTS:

    # interrupt dict {name:{'p':pin,'c':0,'t':0,'s':True,'cb1':<function>},'cb2':<function>}}
    # p = pin object
    # c = interrupt count since create|clear
    # t = last time.time() of interrupt
    # s = show
    # cb1 = local callback function (counter)
    # cb2 = second callback function
    interrupts = {}

    # temporary set of interrupt names being called locally
    # not using a pin, so you can't sample the pin state
    calling = set()

    # init
    def __init__(self):

        # needed for interrupt exception handling
        alloc_emergency_exception_buf(100)

    # add interrupt on falling pin
    def add_falling_pin(self,pin,name,samples=5,sample_period=10,callback2=None,show=True):
        self.interrupts[name] = {'c':0,'t':0}
        self.interrupts[name]['p'] = Pin(pin,Pin.IN,pull=Pin.PULL_UP)
        self.interrupts[name]['s'] = show
        self.interrupts[name]['cb1'] = lambda p: self.callback(p,name,0,samples,sample_period)
        self.interrupts[name]['cb2'] = callback2 or None
        self.interrupts[name]['p'].irq(trigger=Pin.IRQ_FALLING,handler=self.interrupts[name]['cb1'])
        print('INTERRUPT',name,'(falling) added on pin',pin)

    # add interrupt on rising pin
    def add_rising_pin(self,pin,name,samples=5,sample_period=10,callback2=None,show=True):
        self.interrupts[name] = {'c':0,'t':0}
        self.interrupts[name]['p'] = Pin(pin,Pin.IN,pull=Pin.PULL_DOWN)
        self.interrupts[name]['s'] = show
        self.interrupts[name]['cb1'] = lambda p: self.callback(p,name,1,samples,sample_period)
        self.interrupts[name]['cb2'] = callback2 or None
        self.interrupts[name]['p'].irq(trigger=Pin.IRQ_RISING,handler=self.interrupts[name]['cb1'])
        print('INTERRUPT',name,'(rising) added on pin',pin)

    # remove pin
    def remove(self,name):
        if name and name in self.interrupts:
            # how do you remove an irq assignment
            del self.interrupts[name]
            return True
        return False

    # clear
    def clear(self,name=None):
        if name == None:
            for name in self.interrupts:
                self.interrupts[name]['c'] = 0
                self.interrupts[name]['t'] = 0
            return True
        elif name in self.interrupts:
            self.interrupts[name]['c'] = 0
            self.interrupts[name]['t'] = 0
            return True
        return False

    # list of interrupt names
    def names(self):
        names = list(self.interrupts.keys())
        names.sort()
        return names

    # check - boolean, does named interrupt have a non-0 count
    # if name == None, does any   interrupt have a non-0 count
    def check(self,name=None):
        if name == None:
            return sum([self.interrupts[x]['c'] for x in self.interrupts]) is not 0
        elif name in self.interrupts:
            return self.interrupts[name]['c'] is not 0
        return False

    # get (count,time) for named interrupt or (None,None)
    def get(self,name):
        if name in self.interrupts:
            return self.interrupts[name]['c'],self.interrupts[name]['t']
        return None,None

    # call (i.e. activate) interrupt
    def call(self,name):
        if name in self.interrupts:
            self.calling.add(name)
            result = self.interrupts[name]['cb1'](self.interrupts[name]['p'])
            self.calling.remove(name)
            return result
        return False

    # change callback2 value
    def set_callback2(self,name,callback2=None):
        if name in self.interrupts:
            self.interrupts[name]['cb2'] = callback2
            return True
        return False        

    # generic callback with debounce
    def callback(self,pin,name=None,target=0,samples=5,sample_period=10):

        # what name
        if not name:
            name = str(pin)

        # must be known
        if name not in self.interrupts:
            return False

        # debounce (require target state for a given time)
        if samples and name not in self.calling:
            for x in range(samples):
                #print('SAMPLE:',pin.value() == target)
                time.sleep_ms(sample_period)
                if pin.value() != target:
                    return False

        # show
        show = self.interrupts[name]['s']

        # notify
        if show:
            print('INTERRUPT:',[name,pin,self.interrupts[name]['c'],self.interrupts[name]['t']],end=' ')

        # update
        self.interrupts[name]['c'] += 1
        self.interrupts[name]['t'] = time.time()

        # secondary callback
        if self.interrupts[name]['cb2']:
            self.interrupts[name]['cb2'](pin)
        elif show:
            print('NO CB2',end=' ')

        # notify
        if show:
            print('COMPLETE')

        # done
        return True

#-----------------------
# end
#-----------------------

