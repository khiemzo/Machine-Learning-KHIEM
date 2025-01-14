#-----------------------
# notify
#-----------------------

print('LOAD: device_lis3dh.py')

#-----------------------
# imports
#-----------------------

import os,sys,time
from math import asin, degrees
from ustruct import unpack, unpack_from

#-----------------------
# lsi3dh class
#-----------------------

class LIS3DH:

    #---------------------------
    # VARS
    #---------------------------

    # spi bus must be initialized on init
    # cs pin can be initialized or int (to initialize) or None (don't use)
    spi = None
    cs = None
    spiok = False

    # chip
    who_am_i = False

    # conversion values
    standard_gravity = 9.806
    high_resolution = None
    low_power = None
    grange = None
    rate = None
    fifo = None
    sensitivity = None
    temp_offset = 0

    # orientation
    or_tipped = 10
    or_fallen = 30
    or_error  = 80

    #---------------------------
    # INIT
    #---------------------------

    def __init__(self,spi,cs=None):

        # spi must be init already
        self.spi = spi

        # init cs pin
        if type(cs) == int:
            self.cs = self.spi.cs_make(cs)
        else:
            self.cs = cs

        # load temp offset
        self.temp_offset_load()

        # reset
        # has time delay to let chip stabilize
        self.reset()

        # get who-am-i byte
        # has multi-read to let bus stabilize
        self.get_chip()

        # set config variables
        # has multi-read to let bus stabilize
        self.set_config()

    # reset
    def reset(self):
        # not defined by chip
        time.sleep_ms(100) # stabilize

    #---------------------------
    # ADDRESS SETUP
    #---------------------------

    # format address to write
    # MSB0 set low = write
    # MSB1 set high = advance address on write
    # MSB2-7 = address
    def to_write(self,address,advance=True):
        if advance:
            return address & 0b01111111 | 0b01000000
        else:
            return address & 0b00111111

    # format address to read
    # MSB0 is set high == read
    # MSB1 set high = advance address on read
    # MSB2-7 = address
    def to_read(self,address,advance=True):
        if advance:
            return address | 0b11000000
        else:
            return address | 0b10000000 & 0b10111111

    #---------------------------
    # CONFIG
    #---------------------------

    # register 0x0F = chip who-am-i byte
    def get_chip(self):

        for x in range(10):
            cid = self.spi.writeread([self.to_read(0x0F),0],cs=self.cs)[1]
            if cid == 0b00110011:
                self.who_am_i = True
                print('ACC who-am-i OKAY')
                self.spiok = True
                break
            print('ACC who-am-i ERROR:',[cid])
            time.sleep_ms(100)
            self.spiok = False

    # set configuration variables
    def set_config(self):

        # CTRL_REG0 (0x1E)
        # SDO pull-up resistor disable
        ctrl_reg0 = 0b10010000

        # TEMP_CFG_REG (0x1F)
        # ADC and temp
        adc_temp = 0b11000000

        # CTRL_REG1 (0x20)
        # data rates, axis enables, power mode
        # 10hz + low power = 3 uA
        # all axes enabled
        ctrl_reg1 = 0b00101111
        self.rate = 100
        self.low_power = True

        # CTRL_REG2 (0x21)
        # high pass filter
        ctrl_reg2 = 0b00000000

        # CTRL_REG3 (0x22)
        # INT1 select
        ctrl_reg3 = 0b00000000

        # CTRL_REG4 (0x23)
        # block data update, endian, resolution, scale, self-text, spi3w
        # BDU set to 1 for ADC, little endian
        # range 00 = 2g
        # high resolution disabled
        ctrl_reg4 = 0b10000000
        self.high_resolution = 0
        self.grange = 2

        # CTRL_REG5 (0x24)
        # boot, fifo, int latches
        ctrl_reg5 = 0b00000000 # FIFO disabled
        self.fifo = 0

        # CTRL_REG6 (0x25)
        # INT2 select
        ctrl_reg6 = 0b00000000

        # write-check loop
        for x in range(10):

            # write
            self.spi.writeread([self.to_write(0x1E),
                                ctrl_reg0,
                                adc_temp,
                                ctrl_reg1,ctrl_reg2,ctrl_reg3,
                                ctrl_reg4,ctrl_reg5,ctrl_reg6,

                                ],cs=self.cs)

            # check (just first 2 values)
            values = list(self.spi.writeread([self.to_read(0x1F),0,0],cs=self.cs)[1:])
            if [adc_temp,ctrl_reg1] == list(self.spi.writeread([self.to_read(0x1F),0,0],cs=self.cs)[1:]):
                print('ACC CONFIG: OKAY')
                self.spiok = True
                break
            print('ACC CONFIG ERROR:')
            self.spiok = False
            time.sleep_ms(100)

        # reset sensitivity
        self.set_sensitivity()

        # done
        return self.spiok

    #---------------------------
    # CONFIG CHANGES
    #---------------------------

    def set_sensitivity(self):

        # page 10 table 4

        # shift
        # high_resolution = 12 bit
        if self.high_resolution:
            if self.fifo: # fifo = max 10 bits
                self.shift = 6
            else:
                self.shift = 4
        # low power = 8 bit
        elif self.low_power:
            self.shift = 8
        # normal = 10 bit
        else:
            self.shift = 6

        # 4G
        if self.grange == 4:
            if self.high_resolution:
                self.sensitivity = 2
            elif self.low_power:
                self.sensitivity = 32
            else: # normal
                self.sensitivity = 8

        # 8G
        elif self.grange == 8:
            if self.high_resolution:
                self.sensitivity = 4
            elif self.low_power:
                self.sensitivity = 64
            else: # normal
                self.sensitivity = 16

        # 16G
        elif self.grange == 16:
            if self.high_resolution:
                self.sensitivity = 12
            elif self.low_power:
                self.sensitivity = 48
            else: # normal
                self.sensitivity = 192

        # 2G
        else:
            if self.high_resolution:
                self.sensitivity = 1
            elif self.low_power:
                self.sensitivity = 16
            else: # normal
                self.sensitivity = 4

    def set_grange(self,R=2):

        # register 23 bits 5:4

        # bit value
        value = {2:0b00000000,4:0b00010000,8:0b00100000,16:0b00110000}.get(R,0)

        # read current
        reg4byte = self.spi.writeread([self.to_read(0x23),0],cs=self.cs)[1]

        # modify
        value = (reg4byte & 0b11001111) | value

        # write modified value
        self.spi.writeread([self.to_write(0x23),value],cs=self.cs)

        # verify and save locally
        reg4byte = self.spi.writeread([self.to_read(0x23),0],cs=self.cs)[1]
        self.grange = {0:2,1:4,2:8,3:16}.get((reg4byte & 0b00110000) >> 4)

        # reset sensitivity
        self.set_sensitivity()

        # return check
        return self.high_resolution == R

    def set_high_resolution(self,R=0):

        # register 23 bit 3

        if R:
            R = 1
            value = 0b00001000
        else:
            R = 0
            value = 0b00000000

        # read current
        reg4byte = self.spi.writeread([self.to_read(0x23),0],cs=self.cs)[1]

        # modify
        value = (reg4byte & 0b11110111) | value

        # write modified value
        self.spi.writeread([self.to_write(0x23),value],cs=self.cs)

        # verify and save locally
        reg4byte = self.spi.writeread([self.to_read(0x23),0],cs=self.cs)[1]
        self.high_resolution = (reg4byte & 0b00001000) >> 3

        # reset sensitivity
        self.set_sensitivity()

        # return check
        return self.high_resolution == R

    def set_low_power(self,LP=0):

        # register 20 bit 3

        if LP:
            LP = 1
            value = 0b00001000
        else:
            LP = 0
            value = 0b00000000

        # read current
        reg1byte = self.spi.writeread([self.to_read(0x20),0],cs=self.cs)[1]

        # modify
        value = (reg1byte & 0b11110111) | value

        # write modified value
        self.spi.writeread([self.to_write(0x20),value],cs=self.cs)

        # verify and save locally
        reg1byte = self.spi.writeread([self.to_read(0x20),0],cs=self.cs)[1]
        self.low_power = (reg1byte & 0b00001000) >> 3

        # reset sensitivity
        self.set_sensitivity()

        # return check
        return self.low_power == LP

    def set_rate(self,R=0):

        # register 20 bits 7:4

        # bit value
        value = {0:0,1:1,10:2,25:3,50:4,100:5,200:6,400:7,1600:8,1344:9,5376:9}.get(R,0)
        value <<= 4

        # read current
        reg1byte = self.spi.writeread([self.to_read(0x20),0],cs=self.cs)[1]

        # modify
        value = (reg1byte & 0b00001111) | value

        # write modified value
        self.spi.writeread([self.to_write(0x20),value],cs=self.cs)

        # verify and save locally
        reg1byte = self.spi.writeread([self.to_read(0x20),0],cs=self.cs)[1]
        self.rate = {0:0,1:1,2:10,3:25,4:50,5:100,6:200,7:400,8:1600,9:1344}.get((reg1byte & 0b11110000) >> 4)

        # reset sensitivity
        self.set_sensitivity()

        # return check
        return self.rate == R

    #---------------------------
    # GET/SET TEMP OFFSET
    #---------------------------

    temp_offset_file_name = 'board_temp.config'

    def temp_offset_load(self):
        try:
            with open(self.temp_offset_file_name) as f:
                offset = float(f.read().strip())
                f.close()
            self.temp_offset = offset
            print('TEMP OFFSET:',self.temp_offset,'C')
            return True
        except Exception as e:
            #sys.print_exception(e)
            print('TEMP OFFSET: not loaded')
            print('TEMP OFFSET:',self.temp_offset,'C')
            return False

    def set_temp(self,t):
        try:
            t = float(t)
            print('SET TEMP:',t)
            c = 0
            for x in range(100):
                c += self.get_adc_raw()[2]
                time.sleep_ms(10)
            c = (c/100)/100
            offset = t-c
            with open(self.temp_offset_file_name,'w') as f:
                f.write(str(offset)+'\n')
                f.close()            
            self.temp_offset = offset
            print('TEMP OFFSET:',self.temp_offset,'C')
            return True
        except Exception as e:
            sys.print_exception(e)
            print('TEMP OFFSET: not set')
            print('TEMP OFFSET:',self.temp_offset,'C')
            return False

    def set_tempf(self,t):
        return self.set_temp((t-32)/1.8)

    #---------------------------
    # GET VALUES
    #---------------------------

    def get_status(self,value=None):

        # status register aux 07
        status1 = self.spi.writeread([self.to_read(0x07),0],cs=self.cs)[1]

        # status register 27
        status2 = self.spi.writeread([self.to_read(0x27),0],cs=self.cs)[1]

        # make status dict
        d = {
            '321OR': status1 & 128 != 0,
            '3OR'  : status1 &  64 != 0,
            '2OR'  : status1 &  32 != 0,
            '1OR'  : status1 &  16 != 0,
            '321DA': status1 &   8 != 0,
            '3DA'  : status1 &   4 != 0,
            '2DA'  : status1 &   2 != 0,
            '1DA'  : status1 &   1 != 0,

            'ZYXOR': status2 & 128 != 0,
            'ZOR'  : status2 &  64 != 0,
            'YOR'  : status2 &  32 != 0,
            'XOR'  : status2 &  16 != 0,
            'XYZDA': status2 &   8 != 0,
            'ZDA'  : status2 &   4 != 0,
            'YDA'  : status2 &   2 != 0,
            'XDA'  : status2 &   1 != 0
            }

        if value:
            return d.get(value)

        return d

    def get_adc_raw(self):

        # read
        values = self.spi.writeread([self.to_read(0x08),0,0,0,0,0,0],cs=self.cs)[1:]

        # convert
        return unpack('<hhh',values)

    def get_adc(self):

        # raw values
        adc1,adc2,temp = self.get_adc_raw()

        # Datasheet:

        # The input range is 1200 mV ±400 mV and the data output is expressed in 2's complement left-aligned.
        # 800 - 1600

        # The ADC resolution is 10 bits if the LPen (bit 3) in CTRL_REG1 (20h) is cleared
        # otherwise, in low-power mode, the ADC resolution is 8-bit.

        # shift data (assume 10 bit)
        adc1 >>= 6
        adc2 >>= 6
        # not required. just interpret it as 16 bit data

        # borrowed: https://github.com/adafruit/Adafruit_CircuitPython_LIS3DH
        # ADC can only measure voltages in the range of ~900-1200mV!
        # Interpolate between 900mV and 1800mV ## this is wrong see above
        # see: # https://learn.adafruit.com/adafruit-lis3dh-triple-axis-accelerometer-breakout/wiring-and-test#reading-the-3-adc-pins
        # This is a simplified linear interpolation of:
        # return y0 + (x-x0)*((y1-y0)/(x1-x0))
        # Where:
        #   x = ADC value
        #   x0 = -32512
        #   x1 = 32512
        #   y0 = 1800
        #   y1 = 900

        # changed
        adc1 = 1.6 + (adc1 + 512) * (-0.8 / (1024))
        adc2 = 1.6 + (adc2 + 512) * (-0.8 / (1024))

        # temp
        temp = (temp/100) + self.temp_offset

        return adc1,adc2,temp

    def xyz(self):

        return unpack("<hhh",self.spi.writeread([self.to_read(0x28),0,0,0,0,0,0],cs=self.cs)[1:])

    def gforces_data(self):

        ##https://community.st.com/s/question/0D50X00009XkY9f/lis3dh-acceleration-data-interpretation
        ##Miroslav BATEK (ST Employee)
        ##
        ##Edited by ST Community July 21, 2018 at 5:53 PM
        ##Posted on October 26, 2017 at 14:57
        ##
        ##1. The value which describes relation between raw data and acceleration in g is sensitivity.
        ##You can find the values in Table 4 for all full scales and modes.
        ##
        ##The output value is left justified in the output 16 bit register, so you have to first shift
        ##the value right according to selected mode (8, 10, 12 bit).
        ##
        ##2. The FIFO stores only 10 bits values see chapter 3.6 in datasheet
        ##
        ##3. The conversion in the table 8 in AN3308 is correct, maybe the rounding 1.024 to 1g can be misleading.
        ##You made one mistake in the following line "+1g =   1  / 1mg =  1000 = 0x4E8h"
        ##BUT it is given as 0x040h  which is 64.
        ##
        ##The value in the table is 0x4000. The output is 12 bit (high-resolution) so you can shift
        ##it by 4 bits (or divide by 16) and you will get 0x400 which is 1024.
        ##
        ##4. The conversion can be done very simply in C using for example following code:
        ##
        ##int16_t result_lsb;
        ##
        ##result_lsb = ((int16_t)high_byte<<8)+(uint16_t)low_byte;
        ##
        ##result_lsb = result>>4; // in case of high resolution mode = 12bit output
        ##
        ##result_mg = result_lsb * sensitivity; // LSB to mg, see sensitivity in datasheet

        # get values
        x,y,z = self.xyz()

        # shift values
        x >>= self.shift
        y >>= self.shift
        z >>= self.shift

        # return adjusted to full g
        return x*self.sensitivity/1000,y*self.sensitivity/1000,z*self.sensitivity/1000

    def angles_data(self):

        # get g values
        x,y,z = self.gforces_data()

        # adjust
        return (degrees(asin(max(-1.0,min(1.0,x)))),
                degrees(asin(max(-1.0,min(1.0,y)))),
                degrees(asin(max(-1.0,min(1.0,z)))))        

    @property
    def temp(self):

        t = 0
        for x in range(100):
            t += self.get_adc_raw()[2]
            time.sleep_us(2500)
        return self.temp_offset + (t/100)/100


        #return self.temp_offset + (sum([self.get_adc_raw()[2] for x in range(100)])/100)/100

    @property
    def tempf(self):

        return self.temp * 1.8 + 32

    @property
    def gforces(self):

        return dict(zip(('x','y','z'),self.gforces_data()))

    @property
    def acceleration(self):

        # current all axes in meters per second per second
        # standard gravity = 9.806 meters per second per second

        # get g values
        x,y,z = self.gforces_data()

        # return adjusted
        return {'x':x*self.standard_gravity,'y':y*self.standard_gravity,'z':z*self.standard_gravity}

    @property
    def angles(self):

        return dict(zip(('x','y','z'),self.angles_data()))

    @property
    def orientation(self):
        
        # 10 degrees == tipped
        # 45 degrees == fallen

        x,y,z = self.angles_data()

        if abs(x) < self.or_tipped and abs(y) < self.or_tipped:
            return 'UPRIGHT'

        elif abs(x) < self.or_fallen and abs(y) < self.or_fallen:
            return 'TIPPED'

        elif abs(z) + max(abs(x),abs(y)) < self.or_error:
            return 'ERROR'

        else:
            return 'FALLEN'


#-----------------------
# end
#-----------------------
