#-----------------------
# notify
#-----------------------

print('LOAD: gpio_spi.py')

#-----------------------
# pin out
#-----------------------

pinout = '''

14 SCLK-SCL HSPI-1
12 MISO-SDA HSPI-1
13 MOSI-SDO HSPI-1

18 SCLK-SCL VSPI-2
19 MISO-SDA VSPI-2
23 MOSI-SDO VSPI-2

'''

#-----------------------
# imports
#-----------------------

from machine import Pin, SPI

#-----------------------
# default spi bus
#-----------------------

class SPIBUS:

    bus = None

    # default is HSPI (ID=1)
    # sck=14, miso=12, mosi=13
    spiid = 1
    slck = 14
    mosi = 13
    miso = 12

    #baudrate = 1000000 # super slow for connecting, testing, and long distance
    baudrate = 10000000 # default slow (most spi devices support this)
    #baudrate = 40000000 # all gpio pins support this
    #baudrate = 80000000 # max allowed if using HSPI (id=1) or VSPI (id=2)

    polarity = 0
    phase = 0
    bits = 8
    firstbit = SPI.MSB

    def __init__(self):

        # on start, kill an open bus
        # otherwise you get strange things happening
        try:
            SPI(self.spiid).deinit()
        except:
            pass

    def open(self):
        return self.openbus()

    def openbus(self):

        self.bus = SPI(self.spiid,
                       baudrate=self.baudrate,
                       polarity=self.polarity,
                       phase=self.phase,
                       bits=self.bits,
                       firstbit=self.firstbit,
                       sck =Pin(self.slck),
                       mosi=Pin(self.mosi),
                       miso=Pin(self.miso))
        print('SPI BUS:',[self.baudrate,'SCL',self.slck,'MOSI',self.mosi,'MISO',self.miso])
        return True

    def close(self):
        return self.closebus()

    def closebus(self):
        self.bus.deinit()

    def cs_make(self,pin,value=1):

        return Pin(pin,Pin.OUT,value=value)

    def cs_unmake(self,pin,pull=None):

        return Pin(pin,Pin.IN,pull=pull)

    def writeread(self,writebuffer,readbuffer=None,cs=None):

        # if not readbuffer, make one the same size as writebuffer
        # otherwise, readbuffer must be same length as writebuffer

        if cs:
            cs.value(0)

        if readbuffer == None:
            readbuffer = bytearray(len(writebuffer))

        rvalue = self.bus.write_readinto(bytearray(writebuffer),readbuffer)

        if cs:
            cs.value(1)

        return readbuffer

    def write(self,cs=None,somebytes=b''):

        return self.readwrite(somebytes,cs=cs)

    def read(self,cs=None,nbytes=1):

        return

        if cs:
            cs.value(0)

        buffer = self.bus.read(nbytes)

        if cs:
            cs.value(1)

        return buffer

#-----------------------
# end
#-----------------------
