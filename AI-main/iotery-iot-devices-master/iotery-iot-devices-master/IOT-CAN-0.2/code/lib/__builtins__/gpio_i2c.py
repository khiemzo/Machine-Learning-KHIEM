#-----------------------
# notify
#-----------------------

print('LOAD: gpio_i2c.py')

fail

# this is not functional
# will update when needed

#-----------------------
# pin out
#-----------------------

pinout = '''

any IO pins will work

'''

#-----------------------
# imports
#-----------------------

from machine import Pin, I2C

#-----------------------
# default i2c bus
#-----------------------

class I2CBUS:

    bus = None
    i2cid = 0
    scl = None
    sda = None
    freq = 400000

    def __init__(self):
        pass

    def open(self):
        return self.openbus()

    def openbus(self):

        self.bus = I2C(self.i2cid,
                       scl=Pin(self.scl),
                       sda=Pin(self.sda),
                       freq=self.freq)
        return True

    def close(self):
        return self.closebus()

    def closebus(self):
        try:
            self.bus.deinit() # not available for all devices
        except:
            pass

    def cs_make(self,pin,value=1):
        # spi function
        # i2c cs = address
        return True

    def cs_unmake(self,pin,pull=None):
        # spi function
        # i2c cs = address
        return True

    def scan(self):
        return self.bus.scan()

    def writeread(self,writebuffer,readbuffer=None,cs=None):

        # if not readbuffer, make one the same size as writebuffer
        # otherwise, readbuffer must be same length as writebuffer

        self.write(cs,writebuffer)

        # adding
        return b'\x00' + self.read(cs,len(writebuffer))

        if cs:
            cs.value(0)

        if readbuffer == None:
            readbuffer = bytearray(len(writebuffer))

        rvalue = self.bus.write_readinto(bytearray(writebuffer),readbuffer)

        if cs:
            cs.value(1)

        return readbuffer

    def write(self,cs=None,somebytes=b''):

        # cs = address

        return self.bus.writeto(cs,bytearray(somebytes),stop=True)

    def read(self,cs=None,nbytes=1):

        # cs = address

        return self.bus.readfrom(cs,nbytes,stop=True)








