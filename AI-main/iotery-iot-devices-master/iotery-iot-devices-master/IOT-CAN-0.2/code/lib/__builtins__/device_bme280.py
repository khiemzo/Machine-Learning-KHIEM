# this works for the BMP280 and BME280
# humidity for BMP280 will be zero
# this is set up in forced mode (sleep unless asked)
# formulas and compensation were borrowed from https://github.com/SebastianRoll/mpy_bme280_esp8266/blob/master/bme280.py

#-----------------------
# notify
#-----------------------

print('LOAD: device_bme280.py')

#-----------------------
# imports
#-----------------------

import time
from ustruct import unpack, unpack_from

#-----------------------
# bme280 class
#-----------------------

class BME280:

    #---------------------------
    # VARS
    #---------------------------

    # spi bus must be initialized on init
    # cs pin can be initialized or int (to initialize) or None (don't use)
    spi = None
    cs = None
    spiok = False

    # chip
    # BMP = 0x56 0x57 0x58 --> 0x58
    # BME = 0x60
    # set by get_chip()
    chip = 0
    chipname = None

    # calibration data
    dig_T1 = 0
    dig_T2 = 0
    dig_T3 = 0
    dig_P1 = 0
    dig_P2 = 0
    dig_P3 = 0
    dig_P4 = 0
    dig_P5 = 0
    dig_P6 = 0
    dig_P7 = 0
    dig_P8 = 0
    dig_P9 = 0
    dig_H1 = 0
    dig_H2 = 0
    dig_H3 = 0
    dig_H4 = 0
    dig_H5 = 0
    dig_H6 = 0
    dig_H7 = 0

    # elevation in meters
    # set to local elevation to get adjusted pressure
    # set to 0 to get non-adjusted
    # feet * 0.3048 = meters
    elevation = 0

    # config data
    ctrl_hum = None
    ctrl_meas = None
    config = None
    t_fine = None

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

        # reset
        # has time delay to let chip stabilize
        self.reset()

        # get chip ID
        # has multi-read to let bus stabilize
        self.get_chip()

        # set config variables
        # has multi-read to let bus stabilize
        self.set_config()

        # get calibration data
        self.get_calibration()

    # reset
    def reset(self):
        self.spi.writeread([self.to_write(0xE0),0xB6],cs=self.cs)
        time.sleep_ms(100) # stabilize

    #---------------------------
    # ADDRESS SETUP
    #---------------------------

    # format address to write
    # MSB set low = write
    def to_write(self,address):
        return address & 0b01111111

    # format address to read
    # MSB is set high == read
    def to_read(self,address):
        return address | 0b10000000

    #---------------------------
    # CONFIG
    #---------------------------

    # register 0xD0 = chip ID
    def get_chip(self):

        for x in range(10):
            cid = self.spi.writeread([self.to_read(0xD0),0],cs=self.cs)[1]

            if cid == 0x60:
                self.chip = 0x60
                self.chipname = 'BME'
                print('BME280 chip ID OKAY')
                self.spiok = True
                break
            elif cid in (0x56,0x57,0x58):
                self.chip = 0x58
                self.chipname = 'BMP'
                print('BMP280 chip ID OKAY')
                self.spiok = True
                break
            else:
                self.chip = 0
                self.chipname = None
                self.spiok = False
                print('BMx280 chip ID ERROR')
                time.sleep_ms(100)

        return self.chip,self.chipname

    # set configuration variables
    def set_config(self):

        # register 0xF2 = ctrl_hum = humidity control
        #      osrs_h     xxxxx001 = humidity oversampling, 001 recommended for weather
        self.ctrl_hum = 0b00000001

        # register 0xF# = status = write only

        # register 0xF4 = ctrl_meas = temp pressure control
        #       osrs_t     001xxxxx = temperature oversampling, 001 recommended for weather 
        #       osrs_p     xxx001xx = pressure oversampling, 001 recommended for weather
        #         mode     xxxxxx00 = sample mode = 00 = sleep
        self.ctrl_meas = 0b00100100

        # NOTE: some t_sb values vary between BMP and BME

        # register 0xF5 = config = timing filter spi-mode
        #      t_sb     101xxxxx = standby timing, 101 is 1 sec (for normal mode)
        #    filter     xxx000xx = filter, 000 is off
        #  spi3w_en     xxxxxxx0 = select spi 3-wire
        self.config = 0b10100000

        # write-check loop
        for x in range(10):

            # write
            self.spi.writeread([self.to_write(0xF2),self.ctrl_hum],cs=self.cs)
            self.spi.writeread([self.to_write(0xF4),self.ctrl_meas],cs=self.cs)
            self.spi.writeread([self.to_write(0xF5),self.config],cs=self.cs)

            # check
            values = self.spi.writeread([self.to_read(0xF2),0,0,0,0],cs=self.cs)[1:]
            if values[2] == self.ctrl_meas and values[3] == self.config:
                print('BME280 CONFIG:',list(values))
                self.spiok = True
                break
            print('BME280 CONFIG ERROR:',list(values[-2:]),'!=',[self.ctrl_meas,self.config])
            self.spiok = False
            time.sleep_ms(100)

        # done
        return self.spiok

    #---------------------------
    # CONFIG CHANGES
    #---------------------------

    #---------------------------
    # GET VALUES
    #---------------------------

    # register 0xD0 = chip ID
    def get_chip(self):

        cid = self.spi.writeread([self.to_read(0xD0),0],cs=self.cs)[1]

        if cid == 0x60:
            self.chip = 0x60
            self.chipname = 'BME'
            self.spiok = True
        elif cid in (0x56,0x57,0x58):
            self.chip = 0x58
            self.chipname = 'BMP'
            self.spiok = True
        else:
            self.chip = 0
            self.chipname = None
            self.spiok = False

        return cid,self.chipname

    # register 0x88 +26 = calibration data
    # register 0xE1 +16 = calibration data (humidity)
    def get_calibration(self):

        # read part 1 (26 values, starting at 0x88)
        data1 = self.spi.writeread([self.to_read(0x88)]+[0]*26,cs=self.cs)[1:]

        # unpack part 1
        self.dig_T1,self.dig_T2,self.dig_T3, \
        self.dig_P1,self.dig_P2,self.dig_P3, \
        self.dig_P4,self.dig_P5,self.dig_P6, \
        self.dig_P7,self.dig_P8,self.dig_P9, \
        junkbyte,self.dig_H1= unpack("<HhhHhhhhhhhhBB",data1)

        # read part 2 (7 values, starting at 0xE1)
        # all zeros on the BMP
        data2 = self.spi.writeread([self.to_read(0xE1)]+[0]*7,cs=self.cs)[1:]

        # unpack part2
        self.dig_H2,self.dig_H3 = unpack("<hB",data2)
        e4_sign = unpack_from("<b",data2,3)[0]
        e6_sign = unpack_from("<b",data2,5)[0]
        self.dig_H4 = (e4_sign << 4) | (data2[4] & 0xF)
        self.dig_H5 = (e6_sign << 4) | (data2[4] >> 4)
        self.dig_H6 = unpack_from("<b",data2,6)[0]

        ##print('DIG_T',[self.dig_T1,self.dig_T2,self.dig_T3])
        ##print('DIG_P',[self.dig_P1,self.dig_P2,self.dig_P3,self.dig_P4,self.dig_P5,self.dig_P6,self.dig_P7,self.dig_P8,self.dig_P9])
        ##print('DIG_H',[self.dig_H1,self.dig_H2,self.dig_H3,self.dig_H4,self.dig_H5,self.dig_H6])

    # get_raw_data (forced)
    def get_raw_data(self):

        # set mode to forced (mode=0b01|0b10)
        value = self.ctrl_meas | 0b00000001
        self.spi.writeread([self.to_write(0xF4),value],cs=self.cs)

        # wait for conversion
        timeout = 1000
        while timeout:
            ctrl_meas = self.spi.writeread([self.to_read(0xF4),0],cs=self.cs)[1]
            if ctrl_meas == self.ctrl_meas:
                break
            time.sleep_ms(1)
            timeout -= 1

        # read data
        data = self.spi.writeread([self.to_read(0xF7)]+[0]*8,cs=self.cs)[1:]

        # fix data
        # pressure(0xF7): ((msb << 16) | (lsb << 8) | xlsb) >> 4
        raw_press = ((data[0] << 16) | (data[1] << 8) | data[2]) >> 4
        # temperature(0xFA): ((msb << 16) | (lsb << 8) | xlsb) >> 4
        raw_temp = ((data[3] << 16) | (data[4] << 8) | data[5]) >> 4
        # humidity(0xFD): (msb << 8) | lsb
        raw_hum = (data[6] << 8) | data[7]

        # return
        return raw_temp,raw_press,raw_hum

    # get compenstated data
    def get_compensated_data(self):

        # get raw data
        raw_temp,raw_press,raw_hum = self.get_raw_data()

        # temperature
        var1 = ((raw_temp >> 3) - (self.dig_T1 << 1)) * (self.dig_T2 >> 11)
        var2 = (((((raw_temp >> 4) - self.dig_T1) *
                  ((raw_temp >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
        self.t_fine = var1 + var2
        temp = (self.t_fine * 5 + 128) >> 8

        # pressure
        var1 = self.t_fine - 128000
        var2 = var1 * var1 * self.dig_P6
        var2 = var2 + ((var1 * self.dig_P5) << 17)
        var2 = var2 + (self.dig_P4 << 35)
        var1 = (((var1 * var1 * self.dig_P3) >> 8) +
                ((var1 * self.dig_P2) << 12))
        var1 = (((1 << 47) + var1) * self.dig_P1) >> 33
        if var1 == 0:
            press = 0
        else:
            p = 1048576 - raw_press
            p = (((p << 31) - var2) * 3125) // var1
            var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
            var2 = (self.dig_P8 * p) >> 19
            press = ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)

        # humidity
        h = self.t_fine - 76800
        h = (((((raw_hum << 14) - (self.dig_H4 << 20) -
                (self.dig_H5 * h)) + 16384)
              >> 15) * (((((((h * self.dig_H6) >> 10) *
                            (((h * self.dig_H3) >> 11) + 32768)) >> 10) +
                          2097152) * self.dig_H2 + 8192) >> 14))
        h = h - (((((h >> 15) * (h >> 15)) >> 7) * self.dig_H1) >> 4)
        h = 0 if h < 0 else h
        h = 419430400 if h > 419430400 else h
        hum = h >> 12

        # done
        return temp,press,hum

    # get user values (legible, standard output)

    # metric
    @property
    def values(self):
        '''Full values: Temperature Celcius - Pressure Pascals - Humidity Percent'''

        # get compensated values
        t1,p1,h1 = self.get_compensated_data()

        # convert temp to C
        T = t1/100 # C (used for pressure adjust)

        # convert pressure to inches Hg
        # pressure is reported adjusted to sea level
        P = (p1/256) # pascals
        if self.elevation:
            P *= ( 1 - ( (0.0065*self.elevation) / (T + 0.0065*self.elevation + 273.15) ) )**-5.257 # sea level adjust formula

        # convert humidity to %
        H = h1/1024

        # done
        return T,P,H

    # standard
    @property
    def values_standard(self):
        '''Rounded 2: Temperature Fahrenheit - Pressure Inches Hg - Humidity Percent'''

        # get metric values
        t1,p1,h1 = self.values

        # done
        return round(t1*1.8+32,2), round(p1/3386.3887,2), round(h1,2)
    
#-----------------------
# end
#-----------------------
