# this is a threaded wrapper for the iotery SDK
# once started, this runs in the background
# interact with it mainly by reading/writing to buffers
# there are also some variables you can set/check

# for more info, see the iotery_example.py

#-----------------------
# notify
#-----------------------

print('RUN: iotery_threaded_example.py')

#-----------------------
# starting 
#-----------------------

# device data
mykey     = 'ESP321'
myserial  = 'ESP321'
mysecret  = 'ESP321'
myteam_id = '524a5a27-cb7c-11ea-874b-d283610663ec'

# import threaded wrapper
import time,ioteryT

# create threaded api
# this will start the thread and connect (default)
# or you can use keyword start=False, and later api.thread_start()
api = ioteryT.IOTERYT(
    team_id=myteam_id,
    serial=myserial,
    key=mykey,
    secret=mysecret)

# set how often the api-sdk loops
# i.e. checks in and updates with iotery
api.thread_loop_every = 600 # seconds

# you can force an update at any time
api.thread_update = True

# this loop illustrates how to use the buffers/variables
loops = 0
while 1:
    loops += 1
    
    print()
    print('MAIN LOOP:',loops)

    # read variables
    print('  TIME:   ',api.thread_time)    # last loop epoch
    print('  STAMP:  ',api.thread_stamp)   # last loop time
    print('  LOOPS:  ',api.thread_loops)   # number of thread loops 
    print('  STATUS: ',api.thread_status)  # last status of loop NONE|OKAY|ERROR:?|KILLED
    print('  STARTED:',api.thread_started) # is the thread started
    print('  KILL:   ',api.thread_kill)    # is the thread_kill set

    # the buffers are lists, so you can check them like you would lists
    for x in api.thread_data_buffer:
        print('  DATA BUFFER:',x)
    for x in api.thread_command_buffer:
        print('  COMMAND BUFFER:',x)
    for x in api.thread_command_clear_buffer:
        print('  CLEAR BUFFER:',x)

    # check commands buffer (commands from iotery)
    # once you do the command, remove it from the api.thread_command_buffer
    # also add the command uuid to the api.thread_command_clear_buffer
    # this will clear it at iotery (otherwise you will keep getting it)
    while api.thread_command_buffer:
        command = api.thread_command_buffer.pop(0)
        # do something with command
        # command = (enum,command_uuid,type_uuid,timestamp,data)
        api.thread_command_clear_buffer.append(command[1])

    # send some data (always a dict)
    # just put it in the api.thread_data_buffer
    api.thread_data_buffer.append({'event':'test ioteryT','main loops':loops})

    # force api to update (otherwise wait for loop time)
    api.thread_update = True

    # wait a bit and then loop back and check/set buffers
    time.sleep_ms(4000)

    # you can also stop the thread
    # we'll stop after 20 loops here
    if loops >= 20:
        # the wait (if you use it) waits for api.thread_started == False
        # it will return True|False depending on the condition being met in time
        # if not used, it just sets api.thread_kill = True and returns None
        api.thread_stop(wait=10)

    # and we'll kill this loop based on the api status
    if loops > 5 and not api.thread_started:
        break

#-----------------------
# end
#-----------------------
