# Posty Project: byte_socket.py
# Copyright (c) 2019 Clayton Darwin claytondarwin@gmail.com

# notify
print('LOAD: byte_socket.py')

#-----------------------------------------------
# posty_byte_syntax (see posty_esp2_a4899.py)
#-----------------------------------------------

# BYTE COMMANDS:

# typically controls are sent by single bytes
# each bit in the byte has a specific value/meaning

# bits: 765 4 3210
#       000 0 0000

# bits 7-5 are motor select (digital values 0-7)
# bit 4 is direction select (digital values 0-1)
# bits 3-0 are extra steps (digital values 0-15)

# all bytes for motors 1-7 cause a step, even if bits 3-0 == 0
# if bits 3-0 have a digital value from 1-15, additional steps are taken

# bytes for motor 0 are special commands
# special commands may use additional bytes

# BIT SELECT:

# int('11100000',2) = 224 selects motor
# int('00010000',2) = 16 selects direction
# int('00001111',2) = 15 selects additional steps

# motor       = (byte & 224) >> 5
# direction   = (byte & 16 ) >> 4
# extra_steps = (byte & 15 )

# SPECIAL COMMANDS:

# 00000000 =  0 = nop (no operation)
# 00000001 =  1 = ready for data
# 00000010 =  2 = end of data

# 00001010 = 10 = nop
# 00001011 = 11 = working (still working, do nothing, just don't close socket)
# 00001100 = 12 = timeout (end of data, close socket)
# 00001101 = 13 = disable (turn off output pins)
# 00001110 = 14 = enable (turn on output pins)

# 00010100 = 20 = nop - start of multi-byte commands
# 00010101 = 21 = user api key bytes are next 8 bytes 
# 00010110 = 22 = motor wait time in milliseconds to follow, next 3 bytes [motor,value,value] values Big Endian

# 00011100 = 28 = wait-at-least (from last wait-at-least), one extra byte required
# 00011101 = 29 = wait-for (from this byte being received), one extra byte required

# 00011110 = 30 = nop
# 00011111 = 31 = nop (max command value)

# BUILD key:

# keys are 8 bytes send MSB first
# the key sequence is bytes [21] + [k1,k2,k3,k4,k5,k6,k7,k8]
# send 21 followed by 8 key bytes of the key, MSB first

# BUILD motor speed:

# motor wait time is in milliseconds (_us) between state changes
# the key sequence is [22] + [motor] + [byte1,byte2]
# the 2-byte value is Big Endian, value = 256*byte1+byte2

# BUILD wait:

# a wait value is a single byte
# bits 7-3 represent a number 0-63
# bits 2-0 represent an exponent 0-7
# the exponent is a 10th power (10**exponent)
# the number * (10**exponent) == value
# the max value is 63*(10**7) = 630,000,000
# this is the microseconds to wait (time.ticks_us)
# wait values are within 10% of target using this method

# exponent = 0
# while n > maxvalue:
#     n /= 10
#     exponent += 1
# exponent = min(exponent,maxexponent)
# return (n << 3) + exponent

# ----------------------------------------------
# imports
# ----------------------------------------------

# standard library imports
import sys,time,traceback,socket,select

# ----------------------------------------------
# simple non-threaded socket client
# ----------------------------------------------

class Byte_Socket:

    # user defined variables
    server_ip = None
    server_port = None
    server_connect_timeout = 10 # how long to try and connect

    # process variables
    socket = None
    socket_buffer = []

    # codes
    rfd = 1 # read for data
    eod = 2 # end of data
    wfd = 11 # wait for data (working)
    
    # ----------------------------------------------
    # sugar
    # ----------------------------------------------

    def send10(self):
        return self.sendints(10)

    def sendEOD(self):
        return self.sendints(self.eod)

    def sendRFD(self):
        return self.sendints(self.rfd)

    def getto10(self):
        return self.gettoX(10)

    def gettoEOD(self):
        return self.gettoX(self.eod)

    def gettoRFD(self):
        return self.gettoX(self.rfd)

    def wait10(self,timeout=10,fail=False,show=False):
        return self.waitforX(10,timeout,fail,show)

    def waitEOD(self,timeout=10,fail=False,show=False):
        return self.waitforX(self.eod,timeout,fail,show)

    def waitRFD(self,timeout=10,fail=False,show=False):
        return self.waitforX(self.rfd,timeout,fail,show)

    def int22intlistbe(self,n):
        return list(int(min(65535,n)).to_bytes(2,'big'))

    # ----------------------------------------------
    # functions
    # ----------------------------------------------

    def connect(self):

        # try connect
        try:

            # clear data
            self.socket_buffer = []

            # close open socket
            self.disconnect()

            # create socket
            self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.socket.settimeout(0.0) # non-blocking

            # when to stop trying
            stop_at = time.time() + self.server_connect_timeout

            # try to connect
            while 1:

                if time.time() >= stop_at:
                    raise IOError('No route to host.')

                elif self.socket.connect_ex((self.server_ip,self.server_port)) == 0:
                    time.sleep(1)
                    print('SOCKET CONNECTED')
                    break

                else:
                    #print('CONNECT WAIT')
                    time.sleep(0.1)

            # done
            return True
            
        # connect failed
        except Exception as e:
            print(traceback.format_exc())
            self.disconnect() # may raise errors
            raise e

    def disconnect(self):

        # socket did exist
        if self.socket:

            # attempt to inform server
            try:
                self.socket.sendall(bytes([self.eod,10]))
                time.sleep(0.5) # wait a bit for send to happen
            except:
                pass

            # attempt to formally close socket                
            try:
                self.socket.close()
            except:
                pass

            # notify
            print('SOCKET CLOSED')

        # set socket to None
        self.socket = None

    def sendints(self,ints,timeout=10,fail=False,wait=0.1):

        # socket must be open
        if not self.socket:
            raise IOError('Socket is not open.')

        # an int
        if type(ints) == int:
            ints = [ints]

        # send single bytes
        # if it fails you can resend
        # otherwise you don't know which byte failed
        for i in ints:

            # when to stop trying
            stop_at = time.time() + timeout
            sent = False

            # loop
            while time.time() < stop_at:

                # this catches blocking errors
                # keeps trying until timeout
                try:
                    self.socket.sendall(bytes([i]))
                    sent = True
                    break

                except BlockingIOError:
                    time.sleep(wait)

            # timeout
            if not sent:
                if fail:
                    raise IOError('Timeout on sendint.')
                else:
                    return False

        # success
        return len(ints)

##        # make byte string
##        ints = bytes(ints)

##        # when to stop trying
##        stop_at = time.time() + timeout
##
##        # loop
##        wc = 0
##        while time.time() < stop_at:
##
##            # this options will raise errors
##            # only blocking errors are allowd
##
##            try:
##                self.socket.sendall(ints)
##                return len(ints)
##
##            except BlockingIOError:
##                time.sleep(wait)
##
##            # this doesn't detect errors
##            ### clear to send if wlist: rlist,wlist,xlist = select.select([],[self.socket],[],0.01)
##            ##if select.select([],[self.socket],[],0.01)[1]:
##            ##    self.socket.sendall(ints)
##            ##    return len(ints)
##            ##
##            ### wait
##            ##else:
##            ##    time.sleep(wait)
##
##        # timeout
##        if fail:
##            raise IOError('Timeout on sendints.')
##        else:
##            return False     

    def get(self,n=1024):

        # check availability and read
        rlist,wlist,xlist = select.select([self.socket],[],[],0.01)
        if rlist:
            bts = self.socket.recv(n)
            if bts:
                self.socket_buffer += list(bts)

    def getint(self,force=False):

        # socket must be open
        if not self.socket:
            raise IOError('Socket is not open.')

        # just pop and go
        if (not force) and self.socket_buffer:
            return self.socket_buffer.pop(0)

        # read from socket
        self.get()

        # pop
        if self.socket_buffer:
            return self.socket_buffer.pop(0)

        # None
        return None

    def getints(self,n=0,force=False):

        # socket must be open
        if not self.socket:
            raise IOError('Socket is not open.')

        # get all
        if not n:
            if force:
                self.get()
            temp = self.socket_buffer[:]
            self.socket_buffer = []
            return temp

        # just pop and go
        if (not force) and len(self.socket_buffer) >= n:
            temp = self.socket_buffer[:n]
            self.socket_buffer = self.socket_buffer[n:]
            return temp

        # read from socket
        self.get()

        # pop
        temp = self.socket_buffer[:n]
        self.socket_buffer = self.socket_buffer[n:]
        return temp

    def gettoX(self,X=10):

        # socket must be open
        if not self.socket:
            raise IOError('Socket is not open.')

        # just pop and go
        if X in self.socket_buffer:
            index = self.socket_buffer.index(X)+1
            temp = self.socket_buffer[:index]
            self.socket_buffer = self.socket_buffer[index:]
            return temp

        # read from socket
        self.get()

        # pop
        if X in self.socket_buffer:
            index = self.socket_buffer.index(X)+1
            temp = self.socket_buffer[:index]
            self.socket_buffer = self.socket_buffer[index:]
            return temp

        # not there
        return []

    def waitforX(self,X=10,timeout=10,fail=False,show=False):

        # socket must be open
        if not self.socket:
            raise IOError('Socket is not open.')

        # when to stop trying
        stop_at = time.time() + timeout

        # loop
        while time.time() < stop_at:

            # read
            if X not in self.socket_buffer:
                self.get()

            # flush all
            if X not in self.socket_buffer:

                # still working watchdog timer
                if self.wfd in self.socket_buffer:
                    stop_at = stop_at + timeout
                    if show:
                        print('    WORKING')
                while self.socket_buffer:
                    if show:
                        print('    WAIT1:',self.socket_buffer[:16])
                    self.socket_buffer = self.socket_buffer[16:]

            # flush up to X+1
            # return True
            else:
                index = self.socket_buffer.index(X)+1
                if show:
                    for x in range(0,index,16):
                        print('    WAIT2:',self.socket_buffer[x:x+16])
                self.socket_buffer = self.socket_buffer[index:]
                return True

        # timeout
        if fail:
            raise IOError('Timeout on waitX.')
        else:
            return False

    def flush(self,show=True):
        while 1:
            ints = self.getints(16,force=True)
            if show and ints:
                print('    FLUSH:',ints)
            if not ints:
                break

# ----------------------------------------------
# end
# ----------------------------------------------
