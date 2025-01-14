#-----------------------
# notify
#-----------------------

print('LOAD: device_gps.py')

#-----------------------
# imports
#-----------------------

import sys,time
from machine import UART

#-----------------------
# generic UART GPS class
#-----------------------

class GENERIC_Serial:

    #---------------------------
    # VARS
    #---------------------------

    # serial setup
    baudrate = 9600
    bits = 8
    parity = None
    stop = 1
    timeout = 1024 # micro seconds
    tx = 17
    rx = 16
    txbuf = 256
    rxbuf = 1024

    # port
    port = None

    # buffer = list of byte lines
    buffer = []
    bufferline = b''

    # satellites
    sats_in_use = 0
    gps_sats_in_view = 0
    gns_sats_in_view = 0
    sats_in_use_time = 0
    gps_sats_in_view_time = 0
    gns_sats_in_view_time = 0
    sats_valid_time = 60 # seconds until sat data is old

    # basic gps data
    #         0    1     2    3    4      5      6    7    8      9     10   11
    # data = [year,month,day ,hour,minute,second,lat ,long,course,knots,kph ,mph ]
    data   = [None,None ,None,None,None  ,None  ,None,None,None  ,None ,None,None]
    data_time = 0
    data_valid = False
    data_valid_time = 60 # seconds until data is invalid
    show = False

    #---------------------------
    # port functions
    #---------------------------

    def port_open(self,port=1):

        # make port
        self.port = UART(port,baudrate=self.baudrate,bits=self.bits,parity=self.parity,stop=self.stop,timeout=self.timeout,tx=self.tx,rx=self.rx,rxbuf=self.rxbuf,txbuf=self.txbuf)

        # try a flush:
        self.port_flush()

        print('GPS UART:',self.baudrate,'RX',self.rx,'TX',self.tx)

    def port_flush(self):

        self.port.read(self.port.any())

    def port_close(self):

        self.port.deinit()

        del self.port

    def port_lines(self,timeout=2,show=False):

        self.bufferline += self.port.read(self.port.any())
        #print('GPSB:',self.bufferline)

        while b'\r' in self.bufferline:
            line,self.bufferline = self.bufferline.split(b'\r',1)
            try:
                if show or self.show:
                    parse = parse_nmea_bytes(line,check=True,numbers=False)
                    print('    GPS PARSE:',str(parse)[:120])
                    yield parse
                else:
                    yield parse_nmea_bytes(line,check=True,numbers=False)
            except:
                print('    GPS ERROR:',line)

    def print_lines(self):
        for x,y in self.port_lines(show=True):
            pass

    def update_data(self,show=False):

        # example lines from BN-180 GPS
        ##    GPS PARSE: (['GNRMC', '204255.00', 'A', '3407.83074', 'N', '08307.94663', 'W', '0.036', '', '220720', '', '', 'D'], True)
        ##    GPS PARSE: (['GNVTG', '', 'T', '', 'M', '0.036', 'N', '0.066', 'K', 'D'], True)
        ##    GPS PARSE: (['GNGGA', '204255.00', '3407.83074', 'N', '08307.94663', 'W', '2', '09', '1.06', '226.3', 'M', '-31.8', 'M', '', '0000'
        ##    GPS PARSE: (['GNGSA', 'A', '3', '02', '05', '25', '51', '29', '13', '15', '', '', '', '', '', '2.30', '1.06', '2.05'], True)
        ##    GPS PARSE: (['GNGSA', 'A', '3', '84', '85', '', '', '', '', '', '', '', '', '', '', '2.30', '1.06', '2.05'], True)
        ##    GPS PARSE: (['GPGSV', '4', '1', '15', '02', '37', '094', '31', '05', '50', '038', '23', '06', '00', '105', '', '12', '07', '203', '
        ##    GPS PARSE: (['GPGSV', '4', '2', '15', '13', '52', '125', '31', '15', '45', '180', '30', '18', '20', '301', '', '20', '07', '252', '
        ##    GPS PARSE: (['GPGSV', '4', '3', '15', '23', '04', '245', '', '25', '14', '232', '09', '26', '02', '315', '', '29', '66', '292', '30
        ##    GPS PARSE: (['GPGSV', '4', '4', '15', '30', '02', '074', '', '46', '27', '242', '', '51', '43', '219', '31'], True)
        ##    GPS PARSE: (['GLGSV', '2', '1', '07', '68', '05', '032', '', '69', '54', '028', '', '70', '59', '222', '', '71', '10', '214', ''],
        ##    GPS PARSE: (['GLGSV', '2', '2', '07', '83', '13', '129', '', '84', '65', '087', '23', '85', '40', '335', '30'], True)
        ##    GPS PARSE: (['GNGLL', '3407.83074', 'N', '08307.94663', 'W', '204255.00', 'A', 'D'], True)

        # look for new data
        for x,y in self.port_lines(show=show):
            if x and y and x[0]:

                # RMC is main data source
                # GN prefix means it has some GLONASS data
                # data[2] indicates validity of data, 'A' is valid, 'V' is invalid
                if x[0][-3:] == 'RMC':
                    if len(x) >= 10:
                        if x[2] == 'A':
                            self.data = build_rmc_data(x)
                            self.data_valid = True
                            self.data_time = time.time()
                        else:
                            self.data_valid = False

                # GGA has sats in use
                # GN prefix means it has some GLONASS data
                elif x[0][-3:] == 'GGA':
                    if len(x) >= 8 and x[7].isdigit() and int(x[7]):
                        self.sats_in_use = int(x[7])
                        self.sats_in_use_time = time.time()

                ### GMA has sats in use
                #elif x[0][-3:] == 'GNA':
                #    if len(x) >= 8 and x[7].isdigit():
                #        self.sats_in_use = int(x[7])
                #        self.sats_in_use_time = time.ticks_ms()

                # xxGSV has sats in view
                # only need the first line (sat count the same in all lines)
                elif x[0][-3:] == 'GSV':
                    if len(x) >= 4 and x[2] == '1' and x[3].isdigit():

                        # GPS
                        if x[0][:2] == 'GP':
                            self.gps_sats_in_view = int(x[3])
                            self.gps_sats_in_view_time = time.time()

                        # GLONASS
                        elif x[0][:2] == 'GN':
                            self.gns_sats_in_view = int(x[3])
                            self.gns_sats_in_view_time = time.time()

        # reset data valid flag
        if time.time() - self.data_time > self.data_valid_time:
            self.data_valid = False

        # reset sats in use time (too old)
##        if time.ticks_diff(time.ticks_ms(),self.sats_in_use_time) > self.sats_time*1000:
        if time.time() - self.sats_in_use_time > self.sats_valid_time:
            self.sats_in_use = 0

        # reset GPS sats in view time (too old)
##        if time.ticks_diff(time.ticks_ms(),self.gps_sats_in_view_time) > self.sats_time*1000:
        if time.time() - self.gps_sats_in_view_time > self.sats_valid_time:
            self.gps_sats_in_view = 0

        # reset GLONASS sats in view time (too old)
##        if time.ticks_diff(time.ticks_ms(),self.gns_sats_in_view_time) > self.sats_time*1000:
        if time.time() - self.gns_sats_in_view_time > self.sats_valid_time:
            self.gns_sats_in_view = 0

        # return data + validity + sats
        return self.data + [self.data_valid,time.time()-self.data_time,self.sats_in_use,max(self.gps_sats_in_view,self.gns_sats_in_view)]

    def watch(self):
        while 1:
            print()
            for x in self.port_lines(show=True):
                pass
            time.sleep(1)

#-----------------------
# L80-R class
#-----------------------

class L80R_Serial(GENERIC_Serial):

    def reset(self,mode='hot',set_defaults=True,wait=0):

        print('GPS RESET: MODE',str(mode).upper(),'DEFAULTS',set_defaults,'WAIT',wait)

        # Table 3: Default Configurations
        # 9600bps
        # datum = WGS84
        # rate 1Hz
        # DGPS mode off
        # EASYTM enabled
        # NMEA output messages RMC, VTG, GGA, GSA, GSV and GLL

        # do a restart
        mode = {'hot':'101','warm':'102','cold':'103','full':'104'}.get(mode.lower(),'101')
        message = make_nmea_bytes('PMTK'+mode)
        self.port.write(message)

        # defaults
        if set_defaults:
            self.defaults()

        # wait
        time.sleep_ms(wait*1000)

        # done
        return True

    def defaults(self):
        return self.set_messages() and self.easy() and self.dgps()

    def set_messages(self):

        # set NMEA output messages to RMC, GGA, GSV only
        # GGA and GSV only every 5 position fixes
        message = make_nmea_bytes('PMTK314,0,1,0,5,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0')
        self.port.write(message);time.sleep_ms(100)

        # done
        return True

    def easy(self):
        message = make_nmea_bytes('PMTK869,1,1')
        self.port.write(message);time.sleep_ms(100)
        return True

    def easy_off(self):
        message = make_nmea_bytes('PMTK869,1,0')
        self.port.write(message);time.sleep_ms(100)
        return True

    def dgps(self):
        message = make_nmea_bytes('PMTK301,1')
        self.port.write(message);time.sleep_ms(100)
        return True

    def dgps_off(self):
        message = make_nmea_bytes('PMTK301,0')
        self.port.write(message);time.sleep_ms(100)
        return True

    def sleep(self):
        message = make_nmea_bytes('PMTK161')
        self.port.write(message);time.sleep_ms(100)
        return True

    def wake(self,wait_for=0.1):
        # any uart activity
        #message = make_nmea_bytes('PMTK400') # get rate of position fixing
        #message = make_nmea_bytes('PMTK401') # get dpsg mode
        message = make_nmea_bytes('PMTK414') # get nmea output
        #message = make_nmea_bytes('PMTK605') # get hardware release
        self.port.write(message)
        time.sleep_ms(int(wait_for*1000))
        return True

    #                0    1     2   3    4      5      6   7    8      9     10  11    12    13    14        15
    # update_data = [year,month,day,hour,minute,second,lat,long,course,knots,kph,mph]+[valid,age]+[sats_used,sats_in_view]
    items =         'year month day hour minute second lat long course knots kph mph   fixed age   sats_used sats_in_view'.split()

    @property
    def rawdata(self):
        return self.update_data()

    @property
    def hasfix(self):
        return self.data_valid

    @property
    def fulldata(self):
        return dict(zip(self.items,self.update_data()))
    
    @property
    def datetime(self):
        items = self.items
        data = self.update_data()
        return dict(zip(self.items[:6]+self.items[12:14],data[:6]+data[12:14]))

    @property
    def location(self):
        items = self.items
        data = self.update_data()
        return dict(zip(self.items[6:8]+self.items[12:14],data[6:8]+data[12:14]))

    @property
    def course(self):
        items = self.items
        data = self.update_data()
        return dict(zip(self.items[8:14],data[8:14]))

    @property
    def sats(self):
        data = self.update_data()
        return dict(zip(self.items[14:16],data[14:16]))

#-----------------------
# NMEA functions
#-----------------------

# make a NMEA string from string, numbers, list, or tuple
def make_nmea_bytes(data):

    # lists and tuples
    if type(data) in (list,tuple):
        data = ','.join([str(x).strip() for x in data])

    # others
    else:
        data = str(data).strip()

    return bytearray('$' + data + '*' + xor(data) + '\r\n','latin1','?')

# parse a NMEA line (string) to a list
def parse_nmea_bytes(data,check=False,numbers=False):

    string = data.decode('latin1','replace').strip().lstrip('$')
    string,checksum1 = (string+'*').split('*')[:2]

    data = []

    for x in string.split(','):

        x = x.strip()

        # empty
        if not x:
            data.append(x)

        # number option
        elif numbers and x[-1].isdigit():
            try:
                data.append(int(x))
            except ValueError:
                try:
                    data.append(float(x))
                except ValueError:
                    data.append(x)

        # string
        else:
            data.append(x)

    if not check:
        return data,None

    checksum2 = xor(string)

    if checksum2 == checksum1:
        return data,True

    else:
        return data,False

# xor of string
def xor(s):

    check = 0

    for c in s:
        check ^= ord(c)

    return ('0'+hex(check)[2:])[-2:].upper()

# parce NMEA RMC line
# RMC = Recommended Minimum Data
def build_rmc_data(rmc_line_list):

    # start data (None = no data)
    # datetime = UTC
    # lat and long are degrees (float values)
    # minutes and seconds are converted to degrees in the decimal portion
    # negative lat is south
    # negative long is west
    # course is degrees
    #         0    1     2    3    4      5      6    7    8      9     10   11
    # data = [year,month,day ,hour,minute,second,lat ,long,course,knots,kph ,mph ]
    data   = [None,None ,None,None,None  ,None  ,None,None,None  ,None ,None,None]

    # basic checks
    if len(rmc_line_list) >= 10:
        if rmc_line_list[0][-3:] == 'RMC':

            # go as far as you can
            try:

                # saparate line
                xxRMC,utc,status,lat,NS,long,EW,knots,cog,date = [x.strip() for x in rmc_line_list[:10]]

                # date
                isdate = False
                if date and date[:6].isdigit():
                    data[2] = int(date[:2])
                    data[1] = int(date[2:4])
                    data[0] = int(date[4:6])+2000

                # time
                istime = False
                if utc and utc[:6].isdigit():
                    data[3] = int(utc[:2])
                    data[4] = int(utc[2:4])
                    data[5] = int(utc[4:6])

                # lat
                if lat:
                    data[6] = int(lat[:2]) + float(lat[2:])/60
                    if NS == 'S':
                        data[6] *= -1

                # long
                if long:
                    data[7] = int(long[:3]) + float(long[3:])/60
                    if EW == 'W':
                        data[7] *= -1

                # course over ground (degrees)
                if cog:
                    data[8] = float(cog)

                # speed
                if knots:
                    knots = float(knots)
                    data[9] = knots
                    data[10] = knots*1.852
                    data[11] = knots*1.150779

            # no worries
            except:
                pass

    # done
    return data

#-----------------------
# end
#-----------------------
