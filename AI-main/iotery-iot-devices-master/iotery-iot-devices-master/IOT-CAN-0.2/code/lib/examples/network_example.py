#-----------------------
# notify
#-----------------------

print('RUN: network_example.py')

#-----------------------
# networking
#-----------------------

# a global network object "wlan" is created in boot.py
# this is how it is constructed (you don't need to make it again)
# from system_networks import WLAN
# wlan = WLAN()

# the wlan has a wifi connection mamager that will connect, or check, or reconnect
# you call it using wlan.make_ready()
# you can call it whenever you want, it will do what it needs to do

# the connection manager looks in 4 places for networks it is allowed to use

# precedence 1: direct wlan.connect(essid,password,hostname,macaddress)
# password, hostname and macaddress can be None    

# precedence 2: wlan.networks
# list of [(essid,password,hostname,macaddress),...]
# password, hostname and macaddress can be None
# use wlan.networks.append((essid,password,None,None)) or similar

# precedence 3: builtin config object constructed from config.json
# see config.template.json
# password, hostname and macaddress are not required

# precedence 4: networks.csv
# add essid,password,hostname,macaddress per line
# password, hostname and macaddress are not required

# in every location, you can set the hostname for a given net
# you can also set a global hostname and leave the other out
wlan.hostname = 'iotcan02'

# now, lets connect
# this will go through all the options until it can connect
# you can call it again at anytime you lose a connection
# or if you just want to make sure it is ready
# or you changed location
wlan.make_ready()

# you can check if your connection is good
wlan.isconnected()

# you can disconnect
#wlan.disconnect()

# other things
print('WLAN Connected:',wlan.isconnected)
print('WLAN Status:',wlan.status)
print('WLAN Signal:',wlan.rssi)
print('WLAN ESSID:',wlan.essid)
print('WLAN Hostname:',wlan.dhcp_hostname)
print('WLAN Mac Address:',wlan.mac_address)
print('WLAN IP Address:',wlan.ip_address)

#-----------------------
# rtc
#-----------------------

# there is alwo a real-time clock object created in boot.py
# import system_rtc
# rtc = system_rtc.RTCTOOLS()

# once you have internet, this will set it
rtc.ntp_set()

# here are your time stamps
print('DTSTAMP:',rtc.dtstamp)
print('LINUX EPOCH:',rtc.linux_epoch)

#-----------------------
# end
#-----------------------

