#-----------------------
# notify
#-----------------------

print('RUN: iotery_example.py')

#-----------------------
# starting 
#-----------------------

# device data (use your credentials)
mykey     = 'xxxx'
myserial  = 'xxxx'
mysecret  = 'xxxx'
myteam_id = 'xxxx'

# request size limit (not required, can be None)
# if given, will be added to all requests
# the default is 1536, which is known to work
myrequest_limit = 1536

# import
import iotery

# create api option 1
api = iotery.IOTERY(team_id=myteam_id,
                    serial=myserial,
                    key=mykey,
                    secret=mysecret,
                    request_limit=myrequest_limit)

# create api option 2
api = iotery.IOTERY()
api.device_key    = mykey
api.device_serial = myserial
api.device_secret = mysecret
api.team_id       = myteam_id
api.request_limit = myrequest_limit

# connect using given data (shortcut)
# this will set token and device data
api.connect()

# print data from api
print()
print('-'*48)
print('connected:',api.isconnected)
print('base_url:',api.base_url)
for item,value in api.headers.items():
    if len(value) > 64:
        value = value[:61]+'...'
    print('header:',[item,value[:]])
print('request_limit:',api.request_limit)
print('token:',api.token[:30]+'... '+api.token[-30:])
print('team_id:',api.team_id)
print('device_key:',api.device_key)
print('device_serial:',api.device_serial)
print('device_secret:',api.device_secret)
print('device_name:',api.device_name)
print('device_uuid:',api.device_uuid)
print('device_type_uuid:',api.device_type_uuid)
print('-'*48)
print()

# NOTE: for any command that is based on the above data,
# that data does not need to be supplied to the command

#-----------------------
# shortcut commands
#-----------------------

# api.connect()
# see example above
# this command used the following routes
# api.getDeviceTokenBasic()
# api.getMe()

# api.isconnected
# returns true if
# 1) a token is set
# 2) a device uuid is set

# api.set_token(token)
# usually not required
# this is called by the api.getDeviceTokenBasic() route
# sets token in api and 'Authorization' in api.headers

# api.post(data)
# post data and return unexecuted commands list
# this builds the outer {'packets':[]} data structure
# just pass in the dict you want to send
# set return_commands=True to get unexecuted commands
print()
print('-'*48)
print('TEST api.post_data')
data = {'testvalue':42} # always a dict
commands = api.post_data(data,return_commands=True)
for enum,CIuuid,CTuuid,timestamp,data in commands:
    print('COMMAND:',[enum,timestamp,CTuuid])

# api.make_data_post_packet(data)
# wrap data dice in minimum required packet structure

# api.get_commands()
# get a list of unexecuted commands
print()
print('-'*48)
print('TEST api.get_commands')
commands = api.get_commands()
for enum,command_uuid,command_type_uuid,timestamp,data in commands:
    print('COMMAND:',[enum,timestamp,command_type_uuid])

# api.clear_command(command_instance_uuid)
# clear the given command
print()
print('-'*48)
print('TEST api.clear_command')
for enum,command_uuid,command_type_uuid,timestamp,data in commands:
    print('CLEARING:',enum,api.clear_command(command_uuid))

#-----------------------
# routes
#-----------------------

# examples supply minimal data
# they assure data has been set in api
# see actual sdk/api file details

# initial

print()
print('-'*48)
print('TEST api.getDeviceTokenBasic')
st.pp(api.getDeviceTokenBasic())

print()
print('-'*48)
print('TEST api.getMe')
st.pp(api.getMe())

print()
print('-'*48)
print('TEST api.getDeviceUnexecutedCommandInstanceList')
st.pp(api.getDeviceUnexecutedCommandInstanceList())

print()
print('-'*48)
print('TEST api.getDeviceSettingList')
st.pp(api.getDeviceSettingList())

print()
print('-'*48)
print('TEST api.getNotificationTypePage')
st.pp(api.getNotificationTypePage())

print()
print('-'*48)
print('TEST api.getBrokerAddress')
st.pp(api.getBrokerAddress())

print()
print('-'*48)
print('TEST api.postData')
# this requires the correct packet structure
st.pp(api.postData(data=api.make_data_post_packet({'teststring':'this is a test string'})))

# these require specific values to use
#api.setCommandInstanceAsExecuted(commandInstanceUuid)
#api.setNotificationInstanceInactive(notificationInstanceUuid)

print()
print('-'*48)

#-----------------------
# end
#-----------------------

