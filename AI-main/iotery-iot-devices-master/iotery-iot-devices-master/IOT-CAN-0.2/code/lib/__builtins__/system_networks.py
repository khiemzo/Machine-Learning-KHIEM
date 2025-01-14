#-----------------------
# notify
#-----------------------

print('LOAD: system_network.py')

#-----------------------
# imports
#-----------------------

import time,network
from ubinascii import hexlify
from system_tools import isfile

# see on-import network setup at bottom

#-----------------------
# connection manager class
#-----------------------

class WLAN:

    # allow connections to open networks
    allow_open = False
    using_open = False

    # connect_manager() networks
    # password, hostname and macaddress can always be None or not included

    # precedence 1
    # essid passed in to connect_manager()

    # precedence 2
    # local network list [(essid,password,hostname,macaddress),...]
    networks = []

    # precedence 3
    # config['networkList']

    # precedence 3
    # networks file
    # use a full path
    # has "essid,password,hostname,macaddress" per row (line)
    networks_file = 'networks.csv'

    # hostname to use
    hostname = 'iotery'

    # dns to use
    dns = '8.8.8.8'

    # connection object
    wlan = None

    # timeout seconds
    timeout = 10

    # network status values
    net_stat_map = {
    200: 'STAT_BEACON_TIMEOUT',
    201: 'STAT_NO_AP_FOUND',
    202: 'STAT_WRONG_PASSWORD',
    203: 'STAT_ASSOC_FAIL',
    204: 'STAT_HANDSHAKE_TIMEOUT',
    1000: 'STAT_IDLE',
    1001: 'STAT_CONNECTING',
    1010: 'STAT_GOT_IP'}

    def __init__(self):
        self.disconnect()

    # check|make ready
    def make_ready(self):

        if not self.isconnected:
            return self.connect_manager()

        # must be okay
        return True

    # scan
    def scan(self,nets=None,show=True):

        if show:
            print('Network Scan')

        if not self.wlan:
            self.wlan = network.WLAN(network.STA_IF)
        current_state = self.wlan.active()
        self.wlan.active(True)

        aps = {}
        for ssid,bssid,channel,RSSI,authmode,hidden in self.wlan.scan():
            ssid = ssid.decode('ascii')
            if nets and ssid not in nets:
                continue
            bssid = hexlify(bssid).decode('ascii')
            if len(bssid) == 12:
                bssid = ':'.join([bssid[x:x+2] for x in range(0,12,2)])
            authmode = ('OPEN','WEP','WPA-PSK','WPA2-PSK','WPA/WPA2-PSK')[min(4,max(0,authmode))]
            if hidden:
                hidden = True
            else:
                hidden = False
            aps[ssid] = (bssid,channel,RSSI,authmode,hidden)
            if show:
                print('Network AP:',[ssid,bssid,channel,RSSI,authmode,hidden])

        self.wlan.active(current_state)

        return aps

    # network iterator (should be REPLACED)
    def network_iterator(self):

        for essid,password,hostname,macaddress in self.networks:
            print('NETLIST:',[essid,password,hostname,macaddress])
            yield essid,password,hostname,macaddress

        if config:
            for nw in config.get('networkList',[]):
                essid = nw.get('essid',nw.get('ssid',None))
                if essid:
                    password,hostname,macaddress = nw.get('password',None),nw.get('hostname',None),nw.get('macaddress',None)
                    print('NETCONF:',[essid,password,hostname,macaddress])
                    yield essid,password,hostname,macaddress

        if self.networks_file and isfile(self.networks_file):
            with open(self.networks_file) as f:
                for line in f:
                    line = line.strip()
                    if line and line[0] != '#': # required for smash 3
                        essid,password,hostname,macaddress = ([x.strip() or None for x in line.split(',')]+[None,None,None,None])[:4]
                        print('NETFILE:',[essid,password,hostname,macaddress])
                        yield essid,password,hostname,macaddress
                f.close()

    # connect manager
    def connect_manager(self,essid=None,password=None,hostname=None,macaddress=None):

        # start with disconnect
        self.disconnect(show=False)

        # get all networks
        current_networks = self.scan(show=False)

        # use given credentials
        if essid and essid in current_networks and self.connect(essid,password,hostname,macaddress):
            return True
        else:
            self.disconnect(show=False)

        # try to connect to known networks
        for e,p,h,m in self.network_iterator():
            if e in current_networks:
                if self.connect(e,p,h,m):
                    return True
                else:
                    self.disconnect(show=False)

        # try open networks
        if self.allow_open:
            for e,(b,c,r,a,h) in current_networks.items():
                if a == 'OPEN':
                    if self.connect(e):
                        return True
                    else:
                        self.disconnect(show=False)

        # didn't work
        print('Network Connect: FAIL')
        return False

    # connect function
    def connect(self,essid,password=None,hostname=None,dns=None,macaddress=None,timeout=None,show=True):

        # get hostname
        if hostname and hostname.strip():
            hostname = hostname.strip()
        elif config and 'hostname' in config and config['hostname'].strip():
            hostname = config['hostname'].strip()
        elif self.hostname and self.hostname.strip():
            hostname = self.hostname.strip()
        else:
            hostname = None

        # notify
        if not password:
            print('Network Connect to OPEN Network:',essid,'as',self.hostname)
        elif show:
            print('Network Connect:',essid,'as',self.hostname)

        # bring up wlan
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

        # disconnect
        if self.wlan.isconnected():
            self.disconnect(show=False)

        # set hostname
        if hostname:
            self.wlan.config(dhcp_hostname=hostname)

        # connect
        connected = False
        self.wlan.connect(essid,password,bssid=macaddress)
        time.sleep(0.1)
        for x in range(timeout or self.timeout):
            if self.wlan.isconnected():
                connected = True
                self.using_open = False
                if not password:
                    self.using_open = True
                break
            time.sleep(1)

        # reset dns
        if self.dns:
            ifc = list(self.wlan.ifconfig())
            ifc[-1] = self.dns
            self.wlan.ifconfig(ifc)

        # notify
        if show or not password:
            print('Network Connect',connected)

        # done
        return connected

    # disconnect
    def disconnect(self,timeout=None,show=True):

        # notify
        if show:
            print('Network Disconnect')

        if not self.wlan:
            self.wlan = network.WLAN(network.STA_IF)

        return_value = True

        if self.wlan.active():
            if self.wlan.isconnected():
                self.wlan.disconnect()
                time.sleep(0.1)
                for x in range(timeout or self.timeout):
                    if not self.wlan.isconnected():
                        break
                    time.sleep(1)
                return_value = not self.wlan.isconnected()

        self.wlan.active(False)
        self.wlan = None
        self.using_open = False

        # notify
        if show:
            print('Network Disonnect:',return_value)

        # done
        return return_value # True|False

    # connection up status
    @property
    def isconnected(self):
        if self.wlan and self.wlan.active() and self.wlan.isconnected():
            return True
        return False

    # status
    @property
    def status(self):
        if not self.wlan:
            return 'STAT_NONE'
        status_number = self.wlan.status()
        return self.net_stat_map.get(status_number,'STAT_{}'.format(status_number))

    # rssi (signal strength)
    @property
    def rssi(self):
        if not self.wlan:
            return 0
        return self.wlan.status('rssi')

    # connected essid
    @property
    def essid(self):
        if not self.wlan:
            return ''
        return self.wlan.config('essid')

    # dhcp hostname
    @property
    def dhcp_hostname(self):
        if not self.wlan:
            return ''
        return self.wlan.config('dhcp_hostname')

    # mac address
    @property
    def mac_address(self):
        if not self.wlan:
            return ''
        return hexlify(self.wlan.config('mac')).decode('ascii')

    # ip address
    @property
    def ip_address(self):
        if not self.wlan:
            return ''
        return self.wlan.ifconfig()[0]

#-----------------------
# on import
#-----------------------

# setup on import
network.WLAN(network.STA_IF).active(False)
network.WLAN(network.AP_IF).active(False)

#-----------------------
# end
#-----------------------

###-----------------------
### access point server
###-----------------------
##
##def access_point_server(essid='IOTERY_AP',username='admin',password='admin'):
##
##    # start over
##    network.WLAN(network.STA_IF).active(False)
##    network.WLAN(network.AP_IF).active(False)
##
##    #

#-----------------------
# older functions
#-----------------------

### network status values
##net_stat_map = {
##200: 'STAT_BEACON_TIMEOUT',
##201: 'STAT_NO_AP_FOUND',
##202: 'STAT_WRONG_PASSWORD',
##203: 'STAT_ASSOC_FAIL',
##204: 'STAT_HANDSHAKE_TIMEOUT',
##1000: 'STAT_IDLE',
##1001: 'STAT_CONNECTING',
##1010: 'STAT_GOT_IP'}
##
### scan for WiFi LANs (access points)
##def wlan_scan():
##    from ubinascii import hexlify as temphex
##    wlan = network.WLAN(network.STA_IF)
##    state = wlan.active() # save current state
##    wlan.active(True) # set state active
##    for ssid,bssid,channel,RSSI,authmode,hidden in wlan.scan():
##        ssid = ssid.decode('ascii')
##        bssid = temphex(bssid).decode('ascii')
##        if len(bssid) == 12:
##            bssid = ':'.join([bssid[x:x+2] for x in range(0,12,2)])
##        authmode = ('OPEN','WEP','WPA-PSK','WPA2-PSK','WPA/WPA2-PSK')[min(4,max(0,authmode))]
##        if hidden:
##            hidden = True
##        else:
##            False
##        #hidden = (False,True)[min(1,max(0,hidden))]
##        print('Network AP:',[ssid,bssid,channel,RSSI,authmode,hidden])
##    wlan.active(state) # return to pervious state
##    del temphex
##
### connect to WiFi AP
##def wlan_connect(essid,password=None,hostname=None,timeout=15):
##    print('Network Connect:',essid,hostname)
##    wlan = network.WLAN(network.STA_IF)
##    wlan.active(True)
##    if hostname:
##        wlan.config(dhcp_hostname=hostname)
##    ipdata = [None,'0.0.0.0','0.0.0.0','0.0.0.0','0.0.0.0'] # return value
##    if not wlan.isconnected():
##        wlan.connect(essid,password)
##        time.sleep(0.1)
##        for x in range(timeout):
##            if wlan.isconnected():
##                ipdata = list(wlan.ifconfig())
##                ipdata.insert(0,wlan.config('dhcp_hostname'))
##                break
##            time.sleep(1)
##    print('Network Connect:',essid,ipdata)
##    return ipdata # [hostname, ip, subnet, gateway, dns]
##
### disconnect from WiFi AP
##def wlan_disconnect(timeout=15):
##    print('Network Disconnect')
##    wlan = network.WLAN(network.STA_IF)
##    return_value = True
##    if wlan.active():
##        if wlan.isconnected():
##            wlan.disconnect()
##            time.sleep(0.1)
##            for x in range(timeout):
##                if not wlan.isconnected():
##                    break
##                time.sleep(1)
##            return_value = not wlan.isconnected()
##    wlan.active(False)
##    print('Network Disonnect:',return_value)
##    return return_value # True|False

