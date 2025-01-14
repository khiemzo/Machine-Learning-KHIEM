# Posty Project: posty.py
# Copyright (c) 2019 Clayton Darwin claytondarwin@gmail.com

#-----------------------
# notify
#-----------------------

print('RUN: POSTY posty.py')

#-----------------------
# application
#-----------------------

essid = 'DARWIN-NET-3'
essid_password = 'what?'
dhcp_hostname = 'posty'

#-----------------------------------------------
# posty_byte_syntax
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

#-----------------------------------------------
# default PIN numbering
#-----------------------------------------------

# this is for the TTGO-style ESP32 Dev Board
# this is the pinout used for setup
#                     ----
#                    |    | RST
#                    |    | 3V
#                    |    | NC
#                    |    | GND
#                BAT |    | A00  G26 DAC2
#                 EN |    | A01  G25 DAC1  
#                USB |    | A02  G34 IN   --> Input
# 3 ENA  <-- G13 A12 |    | A03  G39 IN   --> Input
# 3 STEP <-- G12 A11 |    | A04  G36 IN   --> Input
# 3 DIR  <-- G27 A10 |    | A05  G04      --> 
# 2 ENA  <-- G33 A09 |    | SCK  G05      --> 
# 2 STEP <-- G15 A08 |    | MOSI G18      --> 
# 2 DIR  <-- G32 A07 |    | MISO G19      --> 
# 1 ENA  <-- G14 A06 |    | RX   G16      --> 
# 1 STEP <-- G22 SCL |    | TX   G17      --> 
# 1 DIR  <-- G23 SDA |    |      G21      --> 
#                     ----

#-----------------------------------------------
# imports
#-----------------------------------------------

# standard library imports
import sys,time,gc,socket,network
from machine import Pin

# post import cleanup
gc.collect()

#-----------------------------------------------
# self run part 1 (called at end)
#-----------------------------------------------

def main():

    while 1:

        # start
        print('Posty Application Starting')
        error = False

        # network connect
        wlan_connect(essid,essid_password,timeout=15)

        # posty
        posty = Posty()
        
        # server start
        try:
            posty.serve()
            return True
        except KeyboardInterrupt:
            return True
        except Exception as e:
            sys.print_exception(e)

        # network disconnect
        wlan_disconnect()

        # end
        print('Posty Application Ended')

        # pause on error
        time.sleep_ms(4000)


#-----------------------------------------------
# application
#-----------------------------------------------

class Posty:

    # application init variables
    application_key  = None # [1,2,3,4,5,6,7,8] # key, list of 8 byte ints OR None OR empty list
    application_rips = None # ['192.168.254.10'] # list of allowed remote IPs (for blocking) OR None
    application_name = 'Posty ESP32 1.1'

    # GPIO values
    # motorX_pins = (DIR,STEP,ENABLE)
    motor1_pins = (23,22,14)
    motor2_pins = (32,15,33)
    motor3_pins = (27,12,13)

    # state-changes per second
    motor1_default_sps = 400
    motor2_default_sps = 400
    motor3_default_sps = 400

    # user-defined server variables
    server_host = '0.0.0.0'
    server_port = 10240
    client_timeout = 10 # seconds after last data received
    
    # client auth variables
    auth_key = False
    auth_ip  = False
    auth_ok  = False # both auths

    # internal
    _motor_pins = {}
    _motor_waits = {}

    def pins_init(self):

        # deinit all pins
        self.pins_deinit()

        # clear, then set to outputs
        self._motor_pins = {}
        self._motor_pins[1] = self.pins_init_channel(self.motor1_pins)
        self._motor_pins[2] = self.pins_init_channel(self.motor2_pins)
        self._motor_pins[3] = self.pins_init_channel(self.motor3_pins)

        # clear waits
        self.clear_waits()

    def pins_deinit(self):

        # clear, then set to inputs
        self._motor_pins = {}
        self.pins_init_channel(self.motor1_pins)
        self.pins_init_channel(self.motor2_pins)
        self.pins_init_channel(self.motor3_pins)

    def pins_init_channel(self,pins):

        return (Pin(pins[0],Pin.OUT,value=0), # DIR low = normal forward 
                Pin(pins[1],Pin.OUT,value=0), # STEP low = wait, low-->high = step
                Pin(pins[2],Pin.OUT,value=1)  # ENABLE disabled = high
                )

    def pins_deinit_channel(self,pins):

        # set all pins to inputs
        # must pull DIR, STEP down or bridges may activate
        # pull ENABLE high to disable
        return (Pin(pins[0],Pin.IN,Pin.PULL_DOWN), # DIR low = normal forward 
                Pin(pins[1],Pin.IN,Pin.PULL_DOWN), # STEP low = wait, low-->high = step
                Pin(pins[2],Pin.IN,Pin.PULL_UP)    # ENABLE disabled = high
                )

    def motors_enable(self):
        for pin in self._motor_pins:
            self._motor_pins[pin][2].value(0)

    def motors_disable(self):
        for pin in self._motor_pins:
            self._motor_pins[pin][2].value(1)

    def clear_waits(self,set_defaults=True):

        # called on pins init
        # called on new client socket

        # setup
        for x in (1,2,3):
            if x not in self._motor_waits:
                self._motor_waits[x] = {}
        
        # wait us --> default values
        if set_defaults:
            self._motor_waits[1]['stepwaitus'] = int(1000000/self.motor1_default_sps)
            self._motor_waits[2]['stepwaitus'] = int(1000000/self.motor2_default_sps)
            self._motor_waits[3]['stepwaitus'] = int(1000000/self.motor3_default_sps)

        # last state change seconds
        self._motor_waits[1]['last'] = time.time()
        self._motor_waits[2]['last'] = time.time()
        self._motor_waits[3]['last'] = time.time()

        # last state change micro seconds
        self._motor_waits[1]['lastus'] = time.ticks_us()
        self._motor_waits[2]['lastus'] = time.ticks_us()
        self._motor_waits[3]['lastus'] = time.ticks_us()

        # wait-at-least
        self._motor_waits['check'] = time.time()
        self._motor_waits['checkus'] = time.ticks_us()

    def auth_set(self):

        rips = False
        key = False
        
        if not self.application_rips:
            rips = True
        elif self.auth_ip:
            rips = True

        if not self.application_key:
            key = True
        elif self.auth_key:
            key = True

        if rips and key:
            self.auth_ok = True
        else:
            self.auth_ok = False

    def auth_clear(self):
        self.auth_key = False
        self.auth_ip  = False
        self.auth_ok  = False

    def serve(self):

        # check server address outside of loop and catch
        self.server_address = socket.getaddrinfo(self.server_host,self.server_port)[0][-1]

        # client socket count
        csc = 0 

        # restart forever (except KeyboardInterrupt)
        while 1:

            # pin init
            self.pins_init()

            # catch all
            try:

                # open server socket
                server_socket = socket.socket()
                server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                server_socket.bind(self.server_address)
                server_socket.listen(1)
                print('Posty Socket Server listening on addr {}.'.format(self.server_address))

                # accept request loop
                while 1:

                    # accept a request
                    client_socket,client_address = server_socket.accept()
                    client_socket.settimeout(0) # 0 = non-blocking

                    # start variables
                    t1 = time.ticks_ms()
                    csc += 1

                    # notify
                    print('Client {} - OPEN - IP:{}'.format(csc,client_address[0]))

                    # reset auth data
                    self.auth_clear()

                    # check/set ip auth
                    if self.application_rips:
                        if client_address[0] in self.application_rips:
                            self.auth_ip = True
                            print('  IP AUTH OKAY')
                        else:
                            print('  IP AUTH ERROR')
                    self.auth_set()

                    # clear wait times
                    self.clear_waits()

                    # still working watchdog timer
                    swwt = time.time()

                    # count variables
                    sc = 0 # state count
                    sp = 0 # states processed
                    cc = 0 # command count
                    cp = 0 # commands processed

                    # input variables
                    timeout = time.ticks_add(self.client_timeout*1000,time.ticks_ms()) # updated after client transaction                    
                    bytes_in,bytes_out = 0,0
                    byte_buffer = [] # list of ints
                    byte_buffer_len = 0
                    new_bytes = 0
                    eod = False

                    # catch client socket errors
                    try:

                        # loop
                        while 1:

                            # read data (non-blocking, so it may be empty)
                            # move to line buffer (get out of socket buffer)
                            data = client_socket.read(256)
                            if data:
                                byte_buffer += list(data)
                                new_bytes = len(data)
                                bytes_in += new_bytes
                                timeout = time.ticks_add(self.client_timeout*1000,time.ticks_ms())

                            # no data
                            if not byte_buffer:

                                # timeout period since last read passed
                                if time.ticks_diff(time.ticks_ms(),timeout) >= 0:
                                    print('  SEND TMO 12 (no data for {} seconds)'.format(self.client_timeout))
                                    bytes_out += client_socket.write(bytes([12]))
                                    break

                                # wait and try again
                                else:
                                    time.sleep_ms(10)

                            # process data
                            else:

                                #-----------------------------------------------
                                # application
                                #-----------------------------------------------

                                while byte_buffer:

                                    # command byte
                                    cmd = byte_buffer[0]

                                    # motor commands
                                    if cmd >= 32:
                                        sc += 1

                                        # get byte
                                        b = byte_buffer.pop(0)

                                        # parse byte
                                        motor       = (b & 224) >> 5
                                        direction   = (b & 16 ) >> 4
                                        extra_steps =  b & 15

                                        # known motor
                                        if motor in (1,2,3):

                                            #print('  RECV STEP:',[motor,direction,extra_steps])

                                            # output pins
                                            dirpin,steppin,enapin = self._motor_pins[motor]

                                            # set direction
                                            dirpin.value(direction)
                                            time.sleep_us(1) # requires 200 ns

                                            # wait setup
                                            stepwaitus = self._motor_waits[motor]['stepwaitus']
                                            if time.time()-self._motor_waits[motor]['last'] > 10:
                                                self._motor_waits[motor]['lastus'] = time.ticks_us() - stepwaitus -1

                                            # steps
                                            lastus = self._motor_waits[motor]['lastus']
                                            for x in range(extra_steps+1):

                                                # wait
                                                while time.ticks_diff(time.ticks_us(),lastus) < stepwaitus:
                                                    #print('wait')
                                                    pass

                                                # step                                                
                                                steppin.value(1)
                                                time.sleep_us(2) # requires 1 us
                                                steppin.value(0)
                                                time.sleep_us(2) # requires 1 us
                                                sp += 1
                                                
                                                # reset local wait
                                                lastus = time.ticks_us()

                                            # full reset wait
                                            self._motor_waits[motor]['lastus'] = time.ticks_us()
                                            self._motor_waits[motor]['last'] = time.time()

                                        # unknown motor
                                        else:
                                            print('UNKNOWN MOTOR:',motor)

                                    # special commands

                                    # client sends wait-at-least pause
                                    # [28,value]
                                    elif cmd == 28:
                                        print('  RECV WAIT 28',end=' --> ')
                                        if len(byte_buffer) < 2:
                                            print('SHORT')
                                            time.sleep_ms(10)
                                            break
                                        else:
                                            value = byte_buffer[1]
                                            exponent = value & 7
                                            value >>= 3
                                            wait = min(10000000,value*10**exponent) # max 10 seconds
                                            print(wait,end=' ')
                                            if time.time()-self._motor_waits['check'] > 10:
                                                pass
                                            else:
                                                while time.ticks_diff(time.ticks_us(),self._motor_waits['checkus']) < wait:
                                                    pass
                                            time.sleep_us(wait)
                                            print('DONE')
                                            for x in range(2):
                                                byte_buffer.pop(0)
                                            cc += 1
                                            cp += 1

                                    # client sends wait-for pause
                                    # [29,value]
                                    # will clear wait times
                                    elif cmd == 29:
                                        print('  RECV WAIT 29',end=' --> ')
                                        if len(byte_buffer) < 2:
                                            print('SHORT')
                                            time.sleep_ms(10)
                                            break
                                        else:
                                            value = byte_buffer[1]
                                            exponent = value & 7
                                            value >>= 3
                                            wait = value * 10**exponent
                                            print(wait,end=' ')
                                            time.sleep_us(wait)
                                            # clear wait times
                                            self.clear_waits(set_defaults=False)
                                            print('CLEAR')
                                            for x in range(2):
                                                byte_buffer.pop(0)
                                            cc += 1
                                            cp += 1

                                    # end of data = 2 (don't notify client or app here)
                                    elif cmd == 2:
                                        print('  RECV EOD 2')
                                        byte_buffer.pop(0)
                                        eod = True
                                        cc += 1
                                        cp += 1
                                        break

                                    # ready for data = 1
                                    elif cmd == 1:
                                        print('  RECV RFD 1',end = ' ')
                                        byte_buffer.pop(0)
                                        bytes_out += client_socket.write(bytes([1]))
                                        print('~ SENT RFD')
                                        cc += 1
                                        cp += 1
                                        
                                    # client sends working = 11
                                    elif cmd == 11:
                                        print('  RECV WRK 11')
                                        byte_buffer.pop(0)
                                        cc += 1
                                        cp += 1

                                    # client sends timeout = 12
                                    elif cmd == 12:
                                        print('  RECV TMO 12')
                                        byte_buffer.pop(0)
                                        eod = True
                                        cc += 1
                                        cp += 1
                                        break

                                    # client sends disable = 13
                                    elif cmd == 13:
                                        print('  RECV DIS 13')
                                        self.motors_disable()
                                        byte_buffer.pop(0)
                                        cc += 1
                                        cp += 1
                                        
                                    # client sends enable = 14
                                    elif cmd == 14:
                                        print('  RECV ENA 14')
                                        self.motors_enable()
                                        byte_buffer.pop(0)
                                        cc += 1
                                        cp += 1
                                        
                                    # client sends key (8 bytes in key)
                                    # [21,byte,byte,byte,byte,byte,byte,byte,byte]
                                    elif cmd == 21:
                                        print('  RECV KEY 21',end=' ')
                                        if len(byte_buffer) < 9:
                                            print('SHORT')
                                            time.sleep_ms(10)
                                            break
                                        else:
                                            if byte_buffer[1:9] == self.application_key:
                                                self.auth_key = True
                                                self.auth_set()
                                                print('OKAY')
                                            else:
                                                print('ERROR')
                                            for x in range(9):
                                                byte_buffer.pop(0)
                                            cc += 1
                                            cp += 1

                                    # client motor wait time in us
                                    # old: client sends motor step speed (steps per second)
                                    # [22,motor,value,value] # Big Endian
                                    elif cmd == 22:
                                        print('  RECV SSP 22',end=' ')
                                        if len(byte_buffer) < 4:
                                            print('SHORT')
                                            time.sleep_ms(10)
                                            break
                                        else:
                                            motor,upper,lower = byte_buffer[1:4]
                                            print(motor,end=' = ')  
                                            if motor not in (1,2,3):
                                                print('bad motor number')
                                            else:
                                                value = upper*256+lower
                                                print(value,'us')
                                                # this was for value = steps per second
                                                # now value is just wait time in us
                                                #print(value,end=' --> ')
                                                #value = int(round(1000000/value,0))
                                                #print(value)
                                                self._motor_waits[motor]['stepwaitus'] = value
                                            for x in range(4):
                                                byte_buffer.pop(0)
                                            cc += 1
                                            cp += 1

                                    # unknown, just keep going
                                    else:
                                        print('  NOP:',byte_buffer.pop(0))                                        

                                    # notify
                                    if sp >= 10000 and sp % 10000 == 0:
                                        print('  STEPS:',sp)

                                    # still working watchdog timer
                                    if time.time() - swwt >= 10:
                                        print('  SEND WRK 11')
                                        bytes_out += client_socket.write(bytes([11]))
                                        swwt = time.time()

                                #-----------------------------------------------
                                # end application
                                #-----------------------------------------------
                                
                            # reset byte_buffer_len
                            new_bytes = 0
                            byte_buffer_len = len(byte_buffer)

                            # break on EOD
                            if eod:
                                break

                        # this point: only client EOD or TIMEOUT
                        # if data is left in the buffer, ignore/delete it

                        # send EOD to client = 2
                        print('  SEND EOD 2')
                        bytes_out += client_socket.write(bytes([2]))

                    # catch client socket errors
                    except OSError as e:
                        sys.print_exception(e)
                        print('Client socket error.')

                    # close client socket
                    client_socket.close()

                    # all pins off
                    self.motors_disable()

                    # notify
                    print('Client {} - CLOSED - IN:{} OUT:{} CMD:{}/{} STS:{}/{} SEC:{}'.format(csc,bytes_in,bytes_out,cp,cc,sc,sp,round(time.ticks_diff(time.ticks_ms(),t1)/1000.0,2)))

                    # clean up big stuff
                    client_socket,buffer,data,block = None,None,None,None
                    gc.collect()

            # keyboard kill
            except KeyboardInterrupt:
                print('KeyboardInterrupt: End server loop.')
                break

            # any other exception
            except Exception as e:
                sys.print_exception(e)
                print('Exception: Go to socket reset.')

            # close main socket
            server_socket.close()
            print('OpenSocket Server closed.')

            # all pins to inputs
            self.pins_deinit()

#-----------------------------------------------
# networks
#-----------------------------------------------

# setup on import
network.WLAN(network.STA_IF).active(False)
network.WLAN(network.AP_IF).active(False)

# connect to WiFi AP
def wlan_connect(essid,password,timeout=15):
    print('Network Connect:',essid)
    wlan = network.WLAN(network.STA_IF)
    try:
        wlan.config(hostname=dhcp_hostname)
    except:
        pass
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(essid,password)
        time.sleep(0.1)
        for x in range(timeout):
            if wlan.isconnected():
                break
            time.sleep(1)
    return_value = wlan.isconnected()
    ipaddr = wlan.ifconfig()[0]
    print('Network Connect:',essid,return_value,ipaddr)
    return return_value

# disconnect from WiFi AP
def wlan_disconnect(timeout=15):
    print('Network Disconnect')
    wlan = network.WLAN(network.STA_IF)
    return_value = True
    if wlan.active():
        if wlan.isconnected():
            wlan.disconnect()
            time.sleep(0.1)
            for x in range(timeout):
                if not wlan.isconnected():
                    break
                time.sleep(1)
            return_value = not wlan.isconnected()
    wlan.active(False)
    print('Network Disonnect:',return_value)
    return return_value

#-----------------------------------------------
# self run part 2
#-----------------------------------------------

if __name__ in('__main__','posty_esp32_a4899'):
    main()

#-----------------------------------------------
# end
#-----------------------------------------------
