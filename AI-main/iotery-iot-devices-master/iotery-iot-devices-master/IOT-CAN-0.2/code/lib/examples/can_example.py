#-----------------------
# notify
#-----------------------

print('LOAD: can_example.py')

#-----------------------
# networking
#-----------------------

# the global can object is set up in boot.py
# this is how it works (doesn't hurt to do it again)

# insure can is functional on spi bus
while not can.reset():
    time.sleep_ms(10)

# set nominal bit rate (can speed)
# the can.set_nbr() function will be run in can.set_config()
can.nbr = 125

# run config 
can.set_config()

# at this point you can can.recv and can.send

# HOWEVER: the can device buffer size is only 2
# so you risk losing a lot of messages
# if the device buffer fills, it stops receiving

# BEST METHOD: is to start the interal buffer thread
# this will read the device and store the messages
# then can.send and can.recv work from the buffers

# you can set the buffer sizes, the default is 100
can.recv_buffer_size = 100
can.send_buffer_size = 100

# now start the can buffer thread
can.start_buffer_thread()

# wait until it is running
for x in range(10):
    if can.buffer_thread_running:
        break
    time.sleep_ms(100)

# now you can can.send and can.recv
# and it will use the buffers
# the thread will send/recv using the device

# NOTE: if the internal recv buffer fills up
# it will stop receiving until you clear space
# you do this by...
# processing some can.recv
# or can.recv_buffer_clear()
# or taking a slice off of the start of can.recv_buffer

# MESSAGES:
# the can device uses standard 13 byte messages
# can.recv and can.send use the same message size
# to make message construction and deconstruction easier
# this module provides several simple message functions

# to build/parse a standard messages:

# this will return a list of 13 integers that can be passed to can.send
message = can.build_message(address=0,extended_address=0,data=[up_to_8_bytes_of_data])

# this will return (address,extended_address,[datalist]) from a message
# use this to deconstruct a message from can.recv
address,extended_address,data = can.parse_message(message)

# if you want to build a canopen format message use this
message = can.build_canopen(address=0,function_code=0,data=[up_to_8_bytes_of_data])

# to parse a canopen format message use this
address,function_code,data = can.parse_canopen(message)

# SENDING:
# the can.send takes a message, a timeout in seconds, and a return_value, and a timeout_value
# the default is can.send(message,timeout=10,return_value=True,timeout_value='error')
# if the message is sent before timeout, the return_value is returned
# if timeout occurs, and timeout_value='error', and Exception is raised
# otherwise if timeout occurs, the timeout_value is returned

# if the buffer thread is running, can.send is trying to put the message in the buffer
# if the buffer is full, it will continue to try until timeout

# if the buffer thread is not running, can.send is trying to put the message into the device
# the device only has 2 send buffers, so it can get filled up quickly
# if the buffer is full, it will continue to try until timeout

# you can send in one line like this
okay = can.send(can.build_message(address,0,data))
okay = can.send(can.build_canopen(address,fc,data=data))

# RECEIVING:
# the can.recv takes a target number, a blocking flag, and a timeout in seconds
# the defaults are can.recv(n=1,blocking=True,timeout=0)
# the return is always a list, but it may not be length n, see below

# thread-buffer non-blocking:
# immediate return of up to n messages if they are in can.recv_buffer
# otherwise return a smaller number or []

# thread-buffer blocking:
# wait until n messages are available, then return exactly n messages
# if timeout is 0, wait forever (that's dangerous)
# if timeout is positive, wait and then raise an Exception

# direct device access:
# if not using the buffer thread, can.recv is reading from the device itself
# the device has 2 recv buffers, and these are always read together
# so... if you ask for an odd number n, the return may have one extra message
# otherwise, the behavior is the same as when using the threaded buffer

# handling recv:
# if thread-buffer and blocking and timeout = 0 you can get a list with 1 message
# otherwise it is best to iterate over the returned list because size can vary
for message in can.recv(100,blocking=False):
    print('STANDRD PARSE:',can.parse_message(message))
    print('CANOPEN PARSE:',can.parse_canopen(message))

# when you are finished, stop the buffer thread
can.stop_buffer_thread()

# now clear the buffers to free memory
#can.recv_buffer_clear()
#can.send_buffer_clear()
can.clear_buffers()

#-----------------------
# end
#-----------------------

while 1:
    c += 1
    can.send(can.build_message(c%256,c%256,[c%256,7,6,5,4,3,2,1]),return_value=None)
    can.send(can.build_canopen(c%128,c%16 ,[c%256,2,3,4,5,6,7,8]),return_value=None)
    for message in can.recv(100,blocking=False):
        if message[-1] == 1:
            print('S-MESSAGE:',can.parse_message(message))
        else:
            print('O-MESSAGE:',can.parse_canopen(message))
        led1.blink()
        time.sleep_ms(500)
        

