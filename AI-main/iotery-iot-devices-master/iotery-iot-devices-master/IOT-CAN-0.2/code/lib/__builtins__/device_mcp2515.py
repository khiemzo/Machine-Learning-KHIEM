#-----------------------
# notify
#-----------------------

print('LOAD: device_mcp2515.py')

#-----------------------
# imports
#-----------------------

import time,gc
from struct import unpack, unpack_from

#-----------------------
# mcp2515 class
#-----------------------

class MCP2515:

    # refs:
    # MCP2515 http://ww1.microchip.com/downloads/en/DeviceDoc/MCP2515-Stand-Alone-CAN-Controller-with-SPI-20001801J.pdf

    # notes:
    # tx buffer 2 seems to corrupt data, it is not being used (just 0 and 1)
    # this should be looked into further
    
    #---------------------------
    # VARS
    #---------------------------

    # spi bus must be initialized on init
    # cs pin can be initialized or int (to initialize) or None (don't use)
    spi = None
    cs = None
    spiok = False

    # can bit rate data
    osc = 16 # Mhz of oscillator
    nbr = 125 # target NBR (nominal bit rate)
    nbr_set_to = 0 # last set value

    # send timeout error
    # set to False if can not connected
    error_on_timeout = True

    #---------------------------
    # INIT
    #---------------------------

    def __init__(self,spi,cs=None,reset=True,set_config=False):

        # spi must be init already
        self.spi = spi

        # init cs pin
        if type(cs) == int:
            self.cs = self.spi.cs_make(cs)
        else:
            self.cs = cs

        # reset on init
        if reset:
            self.reset()

        # set config variables
        if set_config:
            self.set_config()

    # reset = send reset byte 0b11000000
    def reset(self):

        # this is the MCP2515 reset connamd
        self.spi.writeread([0b11000000],cs=self.cs)

        # there isn't a specific flag set on reset
        # CANSTAT 0x0E should be in configuration mode 0b10000000
        # CANCTRL 0x0F should be at start value 0b10000111
        if self.bit_check(0x0E,255,0b10000000) and self.bit_check(0x0F,255,0b10000111):
            return True

        return False

    #---------------------------
    # INTERRUPTS 
    #---------------------------

    # called after recv
    # can/should be re-defined
    def interrupt_clear(self):
        pass

    #---------------------------
    # SPECIAL SPI READ-WRITE
    #---------------------------
    # see Chapter 12

    # read from registries = 0b00000011
    def read(self,address,nbytes=1):
        return self.spi.writeread([0b00000011,address]+[0]*nbytes,cs=self.cs)[2:]

##    # this is not used currently, see below
##    # read from rx buffer (auto clear of RXnIF in CANINTF)
##    def rx_read(self,buffer=0,skip_id=0,nbytes=0):
##
##        # read rx buffer 0 or 1
##        # if skip_id, return 8 bytes (8 data)
##        # else return 13 byte frame (5 ctrl + 8 data)
##        # OR return nbytes
##
##        # determine address command
##        if buffer == 1:
##            if skip_id:
##                address = 0b10010110 # reads at address 0x76
##                if not nbytes:
##                    nbytes = 8
##            else:
##                address = 0b10010100 # reads at address 0x71
##                if not nbytes:
##                    nbytes = 13
##        elif skip_id:
##            address = 0b10010010 # reads at address 0x66
##            if not nbytes:
##                nbytes = 8
##        else:
##            address = 0b10010000 # reads at address 0x61
##            if not nbytes:
##                nbytes = 13
##
##        # interrupt clear
##        self.interrupt_clear()
##
##        # read using special address
##        return self.spi.writeread([address]+[0]*nbytes,cs=self.cs)[1:]

    # read as much as you can
    # return list of full 13-byte messages
    def rx_read_full_all(self):

        # return data
        rdata = []

        # rx_status return a special byte
        # the CANINTF RX0IN and RX1IN are in bit 6 and 7
        status = self.rx_status()

        # read is a special function that clears int flags

        # buffer 0
        if status & 0b01000000:
            rdata.append(list(self.spi.writeread([0b10010000]+[0]*13,cs=self.cs)[1:]))

        # buffer 1
        if status & 0b10000000:
            rdata.append(list(self.spi.writeread([0b10010100]+[0]*13,cs=self.cs)[1:]))

        # interrupt clear
        self.interrupt_clear()

        #for x in rdata:
        #    print('RXBU:',x)

        # done
        return rdata

    # read status message
    def read_status(self):
        return self.spi.writeread([0b10100000,0],cs=self.cs)[1]

    # read rx status message
    def rx_status(self):
        return self.spi.writeread([0b10110000,0],cs=self.cs)[1]

    # write to registries = 0b00000010
    def write(self,address,somebytes):
        return len(self.spi.writeread([0b00000010,address]+list(somebytes),cs=self.cs))-2

    # write to tx buffer
    def tx_buffer(self,buffer=0,skip_id=0,data=None):

        # write data to tx buffer 0,1,2
        # if skip_id, start at data, up to 8 bytes
        # else, start with id, up to 13 bytes (5 are ctrl)

        # determine address command
        if buffer == 2:
            if skip_id:
                address = 0b01000101 # writes at address 0x56
                nbytes = 8
            else:
                address = 0b01000100 # writes at address 0x51
                nbytes = 13
        if buffer == 1:
            if skip_id:
                address = 0b01000011 # writes at address 0x46
                nbytes = 8
            else:
                address = 0b01000010 # writes at address 0x41
                nbytes = 13
        elif skip_id:
            address = 0b01000001 # writes at address 0x36
            nbytes = 8
        else:
            address = 0b01000000 # writes at address 0x31
            nbytes = 13

        # fix data
        if data:
            data = list(data)[:nbytes]
        else:
            data = [0]*nbytes

        #print('TXBU:',[buffer],[data])

        # write using special address
        return len(self.spi.writeread([address]+data,cs=self.cs))-1

    # request to send
    def tx_rts(self,buffer=0):

        address = 0b10000000

        if buffer == 2:
            address += 0b00000100
        elif buffer == 1:
            address += 0b00000010
        else:
            address += 0b00000001

        self.spi.writeread([address],cs=self.cs)

    # bit modify = 0b00000101
    def bit_modify(self,address,mask,value,check=0):

        # input == integers

        # modify the bits in address with the bits in value where the mask bit is 1
        # bit modify only works for CNF*, CANIN*, EFLG, and *CTRL registers
        # otherwise the mask is 0b11111111 and the full register will be set to value
        # this is a byte modify (better to use normal write)

        self.spi.writeread([0b00000101,address,mask,value],cs=self.cs)

        if not check:
            return None

        return self.bit_check(address,mask,value)

    # bit check (not a MCP2515 function)
    def bit_check(self,address,mask,value):

        # get register value and apply mask
        r = self.read(address,1)[0] & mask

        # also apply mask to test value
        v = value & mask

        if r == v:
            return True

        return False

    #---------------------------
    # CONFIG
    #---------------------------

    def set_config(self):

        # set configuration
        # return False if any check fails

        #---------------------------
        # Enter CONFIG MODE
        #---------------------------

        success = self.set_mode('config')
        print('MCP2515 Set Config Mode:',success)
        if not success:
            return False

        #---------------------------
        # TX ~ Chapter 3
        #---------------------------

        # register TXRTSCTRL 0x0D [2-0]
        # set pins to act as digital inputs
        success = self.bit_modify(0x0D,0b00000111,0,check=True)
        print('MCP2515 Set RTS pins to IO:',success)
        if not success:
            return False

        # registers TXBnCTRL 0x30 0x40 0x50 [1-0] priority bits
        success = self.bit_modify(0x30,0b00000011,0b00000011,check=True) and\
                  self.bit_modify(0x40,0b00000011,0b00000011,check=True) and\
                  self.bit_modify(0x50,0b00000011,0b00000011,check=True)
        print('MCP2515 TX0-2 high priority:',success)
        if not success:
            return False

        # TX one-shot mode turned off
        # see below MODES ~ Chapter 10

        # TX interrupts
        # see below Interrupts ~ Chapter 7

        #---------------------------
        # RX ~ Chapter 4
        #---------------------------

        # register BFPCTRL 0x0C [3-2][1-0]
        # set pins to act as digital outputs and disable
        success = self.bit_modify(0x0C,0b00001111,0,check=True)
        print('MCP2515 Set RXBI pins 0:',success)
        if not success:
            return False

        # register RXB0CTRL 0x60
        # [6-5] receive all messages
        # [3] no remote transfer
        # [2] rollover to buffer 1
        success = self.bit_modify(0x60,0b01101100,0b01100100,check=True)
        print('MCP2515 Set RXB0 Control:',success)
        if not success:
            return False

        # register RXB1CTRL 0x70
        # [6-5] receive all messages
        # [3] no remote transfer
        success = self.bit_modify(0x70,0b01101000,0b01100000,check=True)
        print('MCP2515 Set RXB1 Control:',success)
        if not success:
            return False

        # set RX filters
        # initially set to receive all for testing
        # change filters later

        #---------------------------
        # Bit Timing ~ Chapter 5
        #---------------------------

        # registers 0x28 0x29 0x2A CFN1-CFN3
        success = self.set_nbr(self.nbr,set_mode=False)
        if not success:
            return False

        #---------------------------
        # Error Detection ~ Chapter 6
        #---------------------------

        # EFLG 0x2D [7-6]
        # see clear_overflow_flags
        # clear to start
        success = self.clear_overflow_flags()
        print('MCP2515 Clear RX overflow flags:',success)
        if not success:
            return False

        #---------------------------
        # Interrupts ~ Chapter 7
        #---------------------------

        # register 0x2B CANINTE interrupt enable
        # set recv buffer interrupts to ON
        # all others OFF
        success = self.bit_modify(0x2B,0b11111111,0b00000011,check=True)
        print('MCP2515 Set recv interrupts to ON:',success)
        if not success:
            return False

        # register 0x2C CANINTF interrupt flags
        # clear all interrupts
        success = self.bit_modify(0x2C,0b11111111,0b00000000,check=True)
        print('MCP2515 Clear all interrupts:',success)
        if not success:
            return False

        #---------------------------
        # Oscillator ~ Chapter 8
        #---------------------------

        # clock-out, clock prescaler CANCTRL 0x0F [2][1-0]
        # disable
        success = self.bit_modify(0x0F,0b00000111,0,check=True)
        print('MCP2515 Disable Clock-Out:',success)
        if not success:
            return False

        #---------------------------
        # RESET ~ Chapter 9
        #---------------------------

        # see reset function

        #---------------------------
        # MODES ~ Chapter 10
        #---------------------------

        # see set_mode function

        # disable one-shot mode in CANCTRL 0x0F [3]
        print('MCP2515 Disable One-Shot Mode:',self.bit_modify(0x0F,0b00001000,0,check=True))
        if not success:
            return False

        #---------------------------
        # Exit CONFIG MODE
        #---------------------------

        success = self.set_mode('normal')
        print('MCP2515 Set Normal Mode:',success)
        if not success:
            return False

        # done
        return True

    #---------------------------
    # CONFIG CHANGES
    #---------------------------

    # set operation mode CANCTRL 0x0F [7-5]
    def set_mode(self,mode='normal'):

        mode = {'normal':0b00000000,
                'sleep' :0b00100000,
                'loopba':0b01000000,
                'listen':0b01100000,
                'config':0b10000000,
                }.get(mode.lower()[:6],0b00000000) # default to normal mode

        return self.bit_modify(0x0F,0b11100000,mode,check=True)

    # clear RX overflow flags EFLG 0x2D [7-6]
    def clear_overflow_flags(self):
        return self.bit_modify(0x2D,0b11000000,0,check=True)

    # set bus speed (bit timing)
    # ref: MCP2515 http://ww1.microchip.com/downloads/en/DeviceDoc/MCP2515-Stand-Alone-CAN-Controller-with-SPI-20001801J.pdf

    def set_nbr(self,nbr,set_mode=True):

        #---------------------------------------------------------------------------------
        # ref: KVASER Bit Timing Calculator https://www.kvaser.com/support/calculators/bit-timing-calculator/
        # calculated for MCP2510 ~ sample at 75% of bit ~ one sample per bit ~ 8Mhz oscillator
        #---------------------------------------------------------------------------------
        #  TQ pre  TQ pst   TQ     sample
        #  sample  sample   total  percent     sjw     nbr   error    CNF1    CNF2    CNF3
        #---------------------------------------------------------------------------------
        #      12       4      16       75       1     125       0      01      ac      03 <<
        #      12       4      16       75       2     125       0      41      ac      03
        #      12       4      16       75       3     125       0      81      ac      03
        #      12       4      16       75       4     125       0      c1      ac      03
        #---------------------------------------------------------------------------------
        #      12       4      16       75       1     250       0      00      ac      03 <<
        #      12       4      16       75       2     250       0      40      ac      03
        #      12       4      16       75       3     250       0      80      ac      03
        #      12       4      16       75       4     250       0      c0      ac      03
        #---------------------------------------------------------------------------------
        #       6       2       8       75       1     500       0      00      91      01 <<
        #       6       2       8       75       2     500       0      40      91      01
        #       6       2       8       75       3     500       0      80      91      01
        #       6       2       8       75       4     500       0      c0      91      01
        #---------------------------------------------------------------------------------
        # not able to use 1000kbs
        #---------------------------------------------------------------------------------

        #---------------------------------------------------------------------------------
        # ref: KVASER Bit Timing Calculator https://www.kvaser.com/support/calculators/bit-timing-calculator/
        # calculated for MCP2510 ~ sample at 75% of bit ~ one sample per bit ~ 16Mhz oscillator
        #---------------------------------------------------------------------------------
        #  TQ pre  TQ pst   TQ     sample
        #  sample  sample   total  percent     sjw     nbr   error    CNF1    CNF2    CNF3
        #---------------------------------------------------------------------------------
        #      12       4      16       75       1     125       0      03      ac      03 <<
        #      12       4      16       75       2     125       0      43      ac      03
        #      12       4      16       75       3     125       0      83      ac      03
        #      12       4      16       75       4     125       0      c3      ac      03
        #---------------------------------------------------------------------------------
        #      12       4      16       75       1     250       0      01      ac      03 << validate
        #      12       4      16       75       2     250       0      41      ac      03
        #      12       4      16       75       3     250       0      81      ac      03
        #      12       4      16       75       4     250       0      c1      ac      03
        #---------------------------------------------------------------------------------
        #      12       4      16       75       1     500       0      00      ac      03 <<
        #      12       4      16       75       2     500       0      40      ac      03
        #      12       4      16       75       3     500       0      80      ac      03
        #      12       4      16       75       4     500       0      c0      ac      03
        #---------------------------------------------------------------------------------
        #       6       2       8       75       1    1000       0      00      91      01 <<
        #       6       2       8       75       2    1000       0      40      91      01
        #       6       2       8       75       3    1000       0      80      91      01
        #       6       2       8       75       4    1000       0      c0      91      01
        #---------------------------------------------------------------------------------

        #---------------------------------------------------------------------------------
        # ref: AN754 http://ww1.microchip.com/downloads/en/appnotes/00754.pdf
        #---------------------------------------------------------------------------------
        # validation at 250kbs NBR using 16Mhz oscillator
        #---------------------------------------------------------------------------------
        # fosc = 16000000 # oscillator frequency
        # tosc = 1/fosc   # oscillator period (time)
        # tclk = tosc * 2 # BRP clock period (two osc periods)
        # fbit = 250000   # bit frequency (from NBR)
        # tbit = 1/fbit   # bit period (time)
        # ttq  = tbit/16  # usign 16 TQ per bit
        # brp  = ttq/tclk # pre-scaler value
        # brp  = 2.0      # calculated BRP
        #---------------------------------------------------------------------------------
        # the KVASER CFN1 value is 0x01 or 0b 00 000001
        # this is the value for SJW=1 and BRP=2
        # BRP == 2 == OKAY
        #---------------------------------------------------------------------------------
        # using 12 + 4 TQ == sample at 75%
        # SYNC  == 1 TQ (fixed by CAN standard)
        # PRSEG == N + PS1   == 11
        # PS1   == N + PRSEG == 11
        # PS2   == 4 TQ (fixed at 25% of 16, i.e. post sample)
        #---------------------------------------------------------------------------------
        # the KVASER CFN2 value is 0xAC or 0b 10 101 100
        # this is the value for BLT=1, SAM=0, PS1=6, PRSEG=5
        # 6 + 5 == 11 == OKAY
        #---------------------------------------------------------------------------------
        # the KVASER CFN3 value is 0x03 or 0b x0xxx 011
        # this is the value for WAKFIL=0 and PS2=4
        # PS2 == 4 == OKAY
        #---------------------------------------------------------------------------------
        # validation == OKAY
        #---------------------------------------------------------------------------------

        # get 8Mhz values (see table above)
        if self.osc in (8,8000):
            self.osc = 8
            if nbr in (500,500000):
                nbr = 500
                cfn1,cfn2,cfn3 = 0x00,0x91,0x01
            elif nbr in (250,250000):
                nbr = 250
                cfn1,cfn2,cfn3 = 0x00,0xAC,0x03
            elif nbr in (125,125000):
                nbr = 125
                cfn1,cfn2,cfn3 = 0x01,0xAC,0x03
            else:
                print('MCP2515 NBR out of range.')
                return False

        # get 16Mhz values (see table above)
        elif self.osc in (16,16000):
            self.osc = 16
            if nbr in (1000,1000000):
                nbr = 1000
                cfn1,cfn2,cfn3 = 0x00,0x91,0x01
            elif nbr in (500,500000):
                nbr = 500
                cfn1,cfn2,cfn3 = 0x00,0xAC,0x03
            elif nbr in (250,250000):
                nbr = 250
                cfn1,cfn2,cfn3 = 0x01,0xAC,0x03
            elif nbr in (125,125000):
                nbr = 125
                cfn1,cfn2,cfn3 = 0x03,0xAC,0x03
            else:
                print('MCP2515 NBR out of range.')
                return False

        # not defined
        else:
            print('MCP2515 OSC out of range.')
            return False

        # ready
        print('MCP2515 Set NBR to {}kbs (using {}Mhz):'.format(nbr,self.osc),end=' ')

        # must be in config mode
        if set_mode:
            self.set_mode('config')

        # set values
        success = self.bit_modify(0x2A,0b11111111,cfn1,check=True) and\
                  self.bit_modify(0x29,0b11111111,cfn2,check=True) and\
                  self.bit_modify(0x28,0b00000111,cfn3,check=True)
        print(success)

        # back to normal mode
        if set_mode:
            self.set_mode('normal')

        # save nbr value
        if success:
            self.nbr = nbr
            self.nbr_set_to = nbr

        # done
        return success

    #---------------------------
    # Functions
    #---------------------------

    def testbit(self,integer,bit):
        '''check integer and see if bit is set (i.e. 1)
           integer and bit can be any integer >= 0
           bits are numbered right to left from 0'''
        # do not confuse this with self.bit_check(address,mask,value)
        return (integer & (1<<bit)) != 0

    def bitisset(self,register,bit):

        # get register
        value = self.read(register)[0]

        # shift register
        value >>= bit

        # check
        return value & 1 == 1

    def sending(self,buffer):

        # TXBnCTRL buffers are 0b00110000 == 3<<4 so (3+0|1|2) << 4
        # TXREQ bit is 3

        # fix buffer
        buffer = min(2,max(0,buffer))

        return self.bitisset((3+buffer)<<4,3)

    # buffer values
    buffer_thread_running = False
    buffer_thread_kill = True
    recv_buffer = []
    send_buffer = []
    recv_buffer_size = 100
    send_buffer_size = 100

    def clear_recv_buffer(self):
        self.recv_buffer = []

    def clear_send_buffer(self):
        self.send_buffer = []

    def clear_buffers(self):
        self.recv_buffer = []
        self.send_buffer = []

    def start_buffer_thread(self):

        self.buffer_thread_kill = False
        
        if self.buffer_thread_running:
            return False

        import _thread
        _thread.start_new_thread(self.buffer_thread,())

        return True

    def stop_buffer_thread(self,timeout=10):

        self.buffer_thread_kill = True

        start_time = time.time()
        while start_time + timeout > time.time():
            if not self.buffer_thread_running:
                return True
            time.sleep_ms(10)

        return False

    def buffer_thread(self):

        print('CAN Start Buffer Thread')
        self.buffer_thread_running = True

        try:
        
            # init values
            self.recv_buffer = []
            self.send_buffer = []

            while 1:

                # kill
                if self.buffer_thread_kill:
                    break

                # recv if able (empty all device recv buffers)
                if len(self.recv_buffer) < self.recv_buffer_size:
                    self.recv_buffer += self.rx_read_full_all()
                    
                # send if able (fill device send buffers)
                if self.send_buffer:
                    # only sending with buffers 0 and 1
                    # buffer 2 seems to modify the address
                    for buffer in (0,1):
                        if not self.send_buffer:
                            break
                        if not self.sending(buffer):
                            # pop local buffer and load device buffer
                            self.tx_buffer(buffer=buffer,data=self.send_buffer.pop(0))
                            # set send flag
                            self.tx_rts(buffer)

                # brief pause
                time.sleep_ms(10)

            # error and about to close
            self.buffer_thread_running = False

        except Exception as e:
            self.buffer_thread_running = False
            sys.print_exception(e)
            print('CAN Buffer Tread ERROR.')
        
        print('CAN End Buffer Thread:',len(self.send_buffer),len(self.recv_buffer))

    def recv(self,n=1,blocking=True,timeout=0,timeout_value='error'):

        # return a list of n data packets or timeout
        # timeout is seconds decimal
        # if not blocking: return immeiately (even with a short buffer)
        # if timeout_value == 'error': raise an error on timeout
        # else: return buffer (i.e. block until timeout)
        # non blocking may return []
        # a direct read may return 2 data packets even if n=1

        # return buffer
        buffer = []

        # timeout loop
        if timeout:
            timeout = int(abs(timeout)*1000)
        startticks = time.ticks_ms()
        while (not timeout) or time.ticks_diff(time.ticks_ms(),timeout) < startticks:

            # use thread buffer
            if self.buffer_thread_running:

                # non blocking
                if not blocking:
                    for x in range(n):
                        if self.recv_buffer:
                            buffer.append(self.recv_buffer.pop(0))
                        else:
                            break
                    return buffer

                # blocking
                else:
                    if len(self.recv_buffer) >= n:
                        for x in range(n):
                            buffer.append(self.recv_buffer.pop(0))
                        return buffer

            # direct read from device
            else:

                # read all you can
                buffer += self.rx_read_full_all()

                # non blocking
                if not blocking:
                    return buffer

                # blocking but already enough
                if len(buffer) >= n:
                    return buffer

            # pause before trying again
            time.sleep_ms(10)

        # timeout
        if timeout_value == 'error':
            raise Exception('CAN recv timeout.')
        return buffer

    def send(self,message,timeout=10,return_value=True,timeout_value='error'):

        # timeout is a seconds decimal
        
        if type(message) != list or len(message) != 13:
            raise Exception('Send message format error.')

        # timeout loop
        if timeout:
            timeout = int(abs(timeout)*1000)
        startticks = time.ticks_ms()
        while (not timeout) or time.ticks_diff(time.ticks_ms(),timeout) < startticks:

            # use thread buffer
            if self.buffer_thread_running:
                if len(self.send_buffer) < self.send_buffer_size:
                    self.send_buffer.append(message)
                    return return_value

            # direct write
            else:

                # only sending with buffers 0 and 1
                # buffer 2 seems to modify the address
                for buffer in (0,1):
                    if not self.sending(buffer):
                        self.tx_buffer(buffer=buffer,data=message)
                        self.tx_rts(buffer)
                        return return_value

            # pause before trying again
            time.sleep_ms(10)

        # timeout
        if timeout_value == 'error' and self.error_on_timeout:
            raise Exception('CAN send timeout.')
        return timeout_value

    def bounce(self,N=1):

        try:
            while not self.reset():
                time.sleep_ms(10)
            self.set_config()
            self.start_buffer_thread()
            for x in range(10):
                if self.buffer_thread_running:
                    break
                time.sleep_ms(100)
            while 1:
                for message in self.recv(1024,blocking=False):
                    while 1:
                        sent = 0                        
                        for x in range(N):
                            success = self.send(message)
                            print('BOUNCE{}:'.format(x),message,success)
                            if success:
                                sent += 1
                        if sent >= N:
                            break
                        time.sleep_ms(10)
                    time.sleep_ms(10)
                time.sleep_ms(10)

        except:
            self.stop_buffer_thread()

    #---------------------------
    # Messages
    #---------------------------

    def build_message(self,address=0,extended=0,data=[]):

        # return a list of 13 bytes
        # 5 bytes addressing + 8 bytes data
        # this will load to the send buffers

        # standard address is 11 bits
        # it is shifted left in the first 2 bytes (low,high)
        # max value = 2**11 - 1 = 2047
        # shift 5 left, get bytes
        high,low = (min(2047,address) << 5).to_bytes(2,'big')

        # no extended
        if not extended:
            ehigh,elow = 0,0

        # extended address
        else:

            # set EXIDE bit 3 in "low" to 1
            # this flags that extended address will be sent
            low |= 0b00001000

            # extended address is 18 bits shifted right
            # the 2 highest bits are are the 2 low bits of "low"
            # max value = 2**18 - 1 = 262143
            ebits,ehigh,elow = min(262143,extended).to_bytes(3,'big')

            # add ebits to low
            low |= ebits

        # fix data to list of up to 8 bytes
        data = list(bytearray(data))[:8]

        # done
        return [high,low,ehigh,elow,len(data)] + data

    def parse_message(self,message):

        # parse a 13 byte message into (address,extended,[data])
        # ignore remote requests (bit 4 in address low)

        # split out values
        high,low,ehigh,elow,dlen,*data = message

        # address
        # isolate upper 3 bits from low
        alow = low & 0b11100000
        address = int.from_bytes(bytes((high,alow)),'big')
        address >>= 5  # shift right

        # extended address
        # check flag bit
        if low & 0b00001000:

            # get ebits
            ebits = low & 0b00000011

            # make extended address
            extended = int.from_bytes(bytes((ebits,ehigh,elow)),'big')

        # no extended, use zero
        # raw message may have junk in ehigh, elow
        else:
            extended = 0

        # data
        dlen = min(8,dlen)
        data = data[:dlen] + [0]*(8-dlen)

        # done
        return address,extended,data

    def build_canopen(self,address=0,function_code=0,data=[]):

        ### address is 7 bits or 2**7 -1 = 127
        ##address = min(127,address)
        ##
        ### function code = 4 bits or 2**4 -1 = 15
        ##function_code = min(15,function_code)
        ##
        ### build true address
        ##address = (function_code << 7) + address
        ##
        ### shift to upper 11 bits
        ##address <<= 5
        ##
        ### make bytes
        ##high,low = (address).to_bytes(2,'big')
        
        # all together now
        high,low = ((min(15,function_code)<<12)+(min(127,address)<<5)).to_bytes(2,'big')

        # fix data to list of up to 8 bytes
        data = list(bytearray(data))[:8]

        # done
        return [high,low,0,0,len(data)] + data

    def parse_canopen(self,message):

        # parse a 13 byte message into (address,function_code,[data])
        # ignore remote, extended, and all other data

        # split out values
        high,low,_,_,dlen,*data = message

        # isolate upper 3 bits from low
        # the others are not used in canopen
        low &= 0b11100000

        # make full id bytes (2), these are shifted left
        idbits = int.from_bytes(bytes((high,low)),'big')

        # top 4 bits are function code
        function_code = (idbits & 0b1111000000000000) >> 12

        # next 7 bits are address
        address = (idbits & 0b0000111111100000) >> 5

        # data
        dlen = min(8,dlen)
        data = data[:dlen] + [0]*(8-dlen)

        # done
        return address,function_code,data

    # J1939 --> extended CAN frame --> MCP2515 
    #          |-------------------------------- 32 bits ------------------------------|
    #                 |------------------------- 29 bits ------------------------------|
    #          |----- byte0 -----|----- byte1 -----|----- byte2 -----|----- byte3 -----|
    #          |-7-6-5-4-3-2-1-0-|-7-6-5-4-3-2-1-0-|-7-6-5-4-3-2-1-0-|-7-6-5-4-3-2-1-0-|
    # PUD1-A1: |      |prio3|rsv2| PDU Format Byte | Destination ID  |--- Source ID ---|
    # PSU2-B : |      |pri03|--- Parameter Group Number (PGN) 18 ----|--- Source ID ---|
    #          |-------------------------------- 32 bits ------------------------------|
    # CANEXT : |----- address11<<5 -----|crlt3|------------- extended18 ---------------|
    # MCP2515: |----- byte0 -----|----- byte1 -----|----- byte2 -----|----- byte3 -----|
    # MCP2515: |----- high8 -----| low3 |crtl3|ebt2|----- ehigh8 ----|----- elow8 -----| datalen | data

    def build_j1939(self,
                    priority=6,
                    reserved=0,
                    datapage=0,
                    pduformat=0,
                    target=0,
                    source=0,
                    pgn=None,
                    data=[]):

        # priority  = PR = priority bits (3) values 0-6 (0=high,6=low)
        # reserved  = R  = reserved bit value 0 (typical)
        # datapage  = DP = data page bit value 0 (typical) 
        # pduformat = PF = PDU Format value 0-239 = PDU1, 240-255 = PDU2
        # target    = PS = PDU Specific ~ PDU1 = destination address, PDU2 = group extension
        # source    = SA = source address (message producer)
        # pgn       = PGN = pre-formatted PGN, use this instead of R,DP,PF,PS
        # data      = DATA = 8 bytes of data

        # pgn given (precedence)
        # parse into individual values
        if pgn != None:
            reserved  = (pgn & 0b100000000000000000) >> 17 
            datapage  = (pgn & 0b010000000000000000) >> 16
            pduformat = (pgn & 0b001111111100000000) >>  8
            target    =  pgn & 0b000000000011111111

        # use values to build MCP2515 bytes

        # put pr into bits 7-5 (upper 3) of byte0
        byte0 = min(6,abs(priority)) << 5

        # R goes into bit 4 of byte0
        if reserved:
            byte0 |= 0b00010000

        # DP goes into bit 3 of byte 0
        if datapage:
            byte0 |= 0b00001000

        # bits 2-0 are bits 7-5 (upper 3) of PF
        pduformat = min(255,abs(pduformat))
        byte0 += pduformat >> 5

        # that's 8 bits for byte0
        # need 3 more for standard address

        # start byte1 with bits 4-2 from PF
        # this makes 11 bits for standard address
        byte1 = (pduformat & 0b00011100) << 3

        # add extended address flag to byte1
        # this is the EXIDE bit (bit 3)
        byte1 |= 0b00001000

        # end byte1 with bits 1-0 (bottom 2) from PF
        byte1 |= pduformat & 0b00000011

        # destination/group address byte
        # direct write from PS byte
        target = min(target,255)

        # source address byte
        # this is always byte3
        source = min(source,255)

        # fix data (always 8 bytes)
        data = list(bytearray(data))[:8]
        data = data + [0]*(8-len(data))

        # done
        return [byte0,byte1,target,source,8] + data

    def parse_j1939(self,message,as_dict=False):

        # split out values
        high,low,target,source,dlen,*data = message

        # priority
        priority = (high & 0b11100000) >> 5

        # reserved
        reserved  = (high & 0b00010000) >> 4

        # data page
        datapage = (high & 0b00001000) >> 3

        # pdu format
        pduformat  = (high & 0b00000111) << 5
        pduformat += (low  & 0b11100000) >> 3
        pduformat += (low  & 0b00000011) >> 0

        # rebuild pgn
        pgn = (reserved << 17) + (datapage << 16) + (pduformat << 8) + target

        # data
        dlen = min(8,dlen)
        data = data[:dlen] + [0]*(8-dlen)

        # done
        if as_dict:
            return {'priority':pr,'reserved':r,'datapage':dp,'pduformat':pf,
                    'target':ps,'source':sa,'pgn':pgn,'data':data}
        return priority,reserved,datapage,pduformat,target,source,pgn,data

    def parse_29data(self,message):

        # split out values
        high,low,ehigh,elow,dlen,*data = message

        # isolate upper 3 bits from low
        alow = low & 0b11100000

        # make 11 bit address
        address = int.from_bytes(bytes((high,alow)),'big')

        # shift left to make room for 18 bits extended
        # it's already 5 bits left
        address <<= 13

        # get ebits (lower 2 bits in low)
        ebits = low & 0b00000011

        # make/add extended address
        address += int.from_bytes(bytes((ebits,ehigh,elow)),'big')

        # data
        dlen = min(8,dlen)
        data = data[:dlen] + [0]*(8-dlen)

        # done
        return address,data

#-----------------------
# end
#-----------------------
