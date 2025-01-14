#-----------------------
# notify
#-----------------------

print('LOAD: system_rtc.py')

#-----------------------
# imports
#-----------------------

import sys,time
from machine import RTC

#-----------------------
# tools class
#-----------------------

class RTCTOOLS:

    #---------------------------
    # VARS
    #---------------------------

    last_update_time = None

    #---------------------------
    # INIT
    #---------------------------

    def __init__(self):

        self.rtc = RTC()

    #---------------------------
    # functions
    #---------------------------

    def ntp_set(self):

        try:
            from ntptime import settime
            settime()
            del settime
            self.last_update_time = time.time()
            print('RTC NTP OK')
            return True

        except Exception as e:
            #sys.print_exception(e)
            try:
                del settime
            except:
                pass
            print('RTC NTP NOT SET!')
            return False

    def set(self,datetime_tuple):
        '''datetime_tuple = (year,month,day,hours,minutes,seconds)'''

        # not well documented
        # RTC().datetime() = (year,month,day,
        #                     weekday,
        #                     hours,minutes,seconds,
        #                     subseconds)

        try:
            datetime_tuple = tuple(datetime_tuple)
            self.rtc.datetime(datetime_tuple[:3]+(0,)+datetime_tuple[3:6]+(0,))
            self.last_update_time = time.time()
            return True

        except Exception as e:
            #sys.print_exception(e)
            print('RTC TUPLE not set!')
            return False

    def get(self):
        '''return tuple (year,month,day,hours,minutes,seconds)'''

        # see "not well documented" in self.set

        datetime_tuple = self.rtc.datetime()
        return datetime_tuple[:3]+datetime_tuple[4:7]

    @property
    def linux_epoch(self):

        # embedded epoch is 2000-01-01
        # offset from linux epoch (1970)
        # time.gmtime(946684800) == time.struct_time(tm_year=2000, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=5, tm_yday=1, tm_isdst=0)

        return int(time.time()+946684800)

    @property
    def dtstamp(self):

        return '{:0>4}-{:0>2}-{:0>2} {:0>2}:{:0>2}:{:0>2} UTC'.format(*self.get())

#-----------------------
# end
#-----------------------
