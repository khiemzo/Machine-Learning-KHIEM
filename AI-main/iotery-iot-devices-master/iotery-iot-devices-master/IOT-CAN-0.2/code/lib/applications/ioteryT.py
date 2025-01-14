#----------------------- 
# notify
#-----------------------

print('LOAD: ioteryT.py')

#-----------------------
# imports
#-----------------------

# requires the rtc.linux_epoch builtin
# requires the wlan.make_ready builtin

import sys
import time
import _thread

from iotery import IOTERY, IoteryException

#-----------------------
# iotery-threaded class
#-----------------------

class IOTERYT(IOTERY):

    #-----------------------
    # variables
    #-----------------------

    # buffer variables
    thread_data_buffer = []
    thread_command_buffer = []
    thread_command_clear_buffer = []

    # loop variables
    thread_loop_every = 600 # seconds
    thread_update = False # override thread_loop_every
    thread_buffer_max = 100
    thread_kill = True
    thread_started = False
    thread_time = 0
    thread_stamp = 0
    thread_loops = 0
    thread_status = 'NONE' # NONE|OKAY|ERROR:?|KILLED

    #-----------------------
    # init
    #-----------------------
 
    def __init__(self,team_id,serial,key,secret,set_request_limit=False,start=True):

        self.team_id = team_id
        self.device_serial = serial
        self.device_key = key
        self.device_secret = secret
        
        if set_request_limit != False:
            self.request_limit = set_request_limit

        # start thread
        if start:
            self.thread_start()

    #-----------------------
    # thread functions
    #-----------------------

    # start thread
    def thread_start(self,wait=0):
        self.thread_kill = False
        self.thread_loops = 0
        _thread.start_new_thread(self.thread_loop_forever,())
        if wait and wait > 0:
            for x in range(int(wait)):
                time.sleep_ms(1000)
                if self.thread_started:
                    return True
            return False
        else:
            return None

    # stop thread
    def thread_stop(self,wait=0):
        self.thread_kill = True
        self.thread_update = True
        if wait and wait > 0:
            for x in range(int(wait)):
                time.sleep_ms(1000)
                if not self.thread_started:
                    return True
            return False
        else:
            return None

    # this is the outer thread loop
    # this loop never fails
    def thread_loop_forever(self):

        while 1:

            #print('THREAD OUTER LOOP')

            # kill signal
            if self.thread_kill or ('thread_kill' in globals() and thread_kill):
                self.thread_started = False
                self.thread_status = 'KILLED'
                #print('THREAD OUTER LOOP BREAK')
                break

            # reset variables
            #print('THREAD OUTER LOOP RESET')
            self.thread_started = True
            self.thread_time = 0
            self.thread_stamp = 0

            # connect to wlan
            if wlan.make_ready():

                # connect to iotery
                if self.connect():

                    # run process loop with catch
                    try:
                        self.thread_loop()
                    except Exception as e:
                        sys.print_exception(e)
                        pass
                
                # no iotery
                else:
                    self.thread_status = 'ERROR: no iotery connection'

            # no wlan
            else:
                self.thread_status = 'ERROR: no wlan connection'

            # wait until try again
            if self.thread_status.startswith('ERROR'):
                print('IOTERY THREAD',self.thread_status)
            time.sleep_ms(2000)

    # function loop (inner loop)
    # this fails for anything
    def thread_loop(self):

        # start variables
        nextloop = time.ticks_ms() # now

        # loop
        while 1:

            #print('THREAD INNER LOOP')

            # kill
            if self.thread_kill or ('thread_kill' in globals() and thread_kill):
                self.thread_status = 'KILLED'
                #print('THREAD INNER LOOP BREAK 1')
                break

            # wait for loop time
            while (not self.thread_update) and time.ticks_diff(nextloop,time.ticks_ms()) > 0:
                time.sleep_ms(int(self.thread_loop_every*100))
            nextloop = time.ticks_add(nextloop,int(self.thread_loop_every*1000))
            self.thread_update = False

            # kill (after wait)
            if self.thread_kill:
                self.thread_status = 'KILLED'
                #print('THREAD INNER LOOP BREAK 2')
                break

            # loop data update
            self.thread_loops += 1
            self.thread_time = rtc.linux_epoch
            self.thread_stamp = rtc.dtstamp
            self.thread_status = 'OKAY'

            # clear commands
            while self.thread_command_clear_buffer:
                if self.clear_command(self.thread_command_clear_buffer[0]):
                    self.thread_command_clear_buffer.pop(0)
                else:
                    self.thread_status = 'ERROR: Unable to clear command: {}'.format(self.thread_command_clear_buffer[0])
                    raise IoteryException('Unable to clear command: {}'.format(self.thread_command_clear_buffer[0]))

            # get commands
            commands = self.get_commands()
            if commands == False:
                self.thread_status = 'ERROR: Unable to read commands.'
                raise IoteryException('Unable to read commands.')
            else:
                for command in commands:
                    uuid = command[1]
                    for previous in self.thread_command_buffer:
                        if uuid == previous[1]:
                            uuid = None
                            break
                    if uuid:                    
                        self.thread_command_buffer.append(command)

            # post data
            while self.thread_data_buffer:
                if self.post_data(self.thread_data_buffer[0],return_commands=False):
                    self.thread_data_buffer.pop(0)
                else:
                    self.thread_status = 'ERROR: Unable to post data.'
                    raise IoteryException('Unable to post data.')

#-----------------------
# end
#-----------------------
