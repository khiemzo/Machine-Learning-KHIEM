#----------------------- 
# notify
#-----------------------

print('LOAD: iotery.py') 

#-----------------------
# imports
#-----------------------

# requires the rtc.linux_epoch builtin

import sys
try:
    import urequests as requests
    import ujson as json
except:
    import requests
    import json

#-----------------------
# iotery class
#-----------------------

class IOTERY:

    #-----------------------
    # variables
    #-----------------------

    # requests data
    base_url = 'https://api.iotery.io/v1/embedded'
    headers = {'Content-Type':'application/json'}
    request_limit = 1536
    page_size = 1
    page_order = 'asc'
    page_wait = 500 # ms

    # token data
    token = None

    # device data
    team_id = None
    device_key = None
    device_serial = None
    device_secret = None
    device_name = None
    device_uuid = None
    device_type_uuid = None

    #-----------------------
    # init
    #-----------------------

    def __init__(self,team_id=None,serial=None,key=None,secret=None,request_limit=None):

        self.team_id = team_id
        self.device_serial = serial
        self.device_key = key
        self.device_secret = secret

        if type(request_limit) == int:
            self.request_limit = request_limit
        elif type(request_limit) == str and request_limit.isdigit():
            self.request_limit = int(request_limit)

    #-----------------------
    # shortcut functions
    #-----------------------

    def connect(self):
        self.getDeviceTokenBasic()
        self.getMe()
        return self.isconnected

    @property
    def isconnected(self):
        if self.token and self.device_uuid:
            return True
        return False

    # used primarily by self.getDeviceTokenBasic()
    def set_token(self,token):
        if token:
            self.token = token
            self.headers['Authorization'] = 'Bearer '+self.token
            return True
        return False

    def iter_settings(self,page_size=None):
        for response in self.paged_response('GET','/devices/{}/settings'.format(self.device_uuid),page_size=page_size):
            for setting in response.get('settings',[]):
                yield setting

    def iter_notifications(self,page_size=None):
        for response in self.paged_response('GET','/notification-type-pages',page_size=page_size):
            yield response
##            for setting in response.get('settings',[]):
##                yield setting

    def post_data(self,data,return_commands=True):

        # convert data to packet format
        data = self.make_data_post_packet(data)

        # get response
        rdata = self.postData(data=data)

        # check
        if rdata.get('status',None) != 'success':
            return False        

        # return commands (may be empty list)
        if return_commands:
            commands = []
            if 'unexecutedCommands' in rdata:
                for command_instance in rdata['unexecutedCommands']['device']:
                    commands.append((command_instance['commandTypeEnum'],
                                     command_instance['uuid'],
                                     command_instance['commandTypeUuid'],
                                     command_instance['timestamp'],
                                     command_instance.get('_data',[])))
            return commands

        # okay
        return True

    def make_data_post_packet(self,data={}):
        return {'packets':[{'timestamp': rtc.linux_epoch,
                            'deviceUuid': self.device_uuid,
                            'deviceTypeUuid': self.device_type_uuid,
                            'data': data}]}

    def get_commands(self):

        # get response
        rdata = self.getDeviceUnexecutedCommandInstanceList()

        # check
        if rdata.get('status',None) != 'success':
            return False        

        # return commands (may be empty list)
        commands = [] 
        for command_instance in rdata['commands']:
            commands.append((command_instance['commandType']['enum'],
                             command_instance['uuid'],
                             command_instance['commandType']['uuid'],
                             command_instance['timestamp'],
                             command_instance.get('_data',[])))
        return commands

    def clear_command(self,command_uuid):
        
        # get response
        rdata = self.setCommandInstanceAsExecuted(command_uuid)
        
        # check
        if rdata.get('status',None) != 'success':
            return False
        
        # okay
        return True

    #-----------------------
    # routes
    #-----------------------

    # GETs

    def getMe(self,query=None):
        rdata = self.get_response('GET','/me',query)
        self.device_name = rdata.get('name',None)
        self.device_uuid = rdata.get('uuid',None)
        self.device_type_uuid = rdata.get('deviceType',{}).get('uuid',None)
        return rdata

    def getDeviceUnexecutedCommandInstanceList(self,query=None):
        return self.get_response('GET','/devices/{}/unexecuted-commands'.format(self.device_uuid),query)

    def getDeviceSettingList(self,query=None):
        return self.get_response('GET','/devices/{}/settings'.format(self.device_uuid),query)

    def getNotificationTypePage(self,query=None):
        return self.get_response('GET','/notification-type-pages',query)

    def getBrokerAddress(self,query=None):
        return self.get_response('GET','/broker-address',query)

    # POSTs

    def getDeviceTokenBasic(self,data=None,query=None):
        if not data:
            data={'key':self.device_key,'serial':self.device_serial,
                  'secret':self.device_secret,'teamUuid':self.team_id}
        rdata = self.get_response('POST','/basic/get-token',query,data)
        self.set_token(rdata.get('token',None))
        return rdata

    def postData(self,data={},query=None):
        return self.get_response('POST','/devices/{}/data'.format(self.device_uuid),query,data)
        
    # PATCHes

    def setCommandInstanceAsExecuted(self,commandInstanceUuid,data={},query=None):
        if not data:
            data = {'timestamp':rtc.linux_epoch}
        return self.get_response('PATCH','/command-instances/{}/executed'.format(commandInstanceUuid),query,data)

    def setNotificationInstanceInactive(self,notificationInstanceUuid,data={},query=None):
        if not data:
            data = {'timestamp':rtc.linux_epoch}
        return self.get_response('PATCH','/notification-instances/{}/inactive'.format(notificationInstanceUuid),query,data)

    #-----------------------
    # urequest functions
    #-----------------------

    def paged_response(self,method='GET',url=None,query=None,data=None,headers=None,page_size=None):

        # first query
        query = query or {}
        query['limit'] = page_size or self.page_size
        query['order'] = self.page_order
        response = self.get_response(method,url,query,data,headers)
        yield response

        # more
        # ['paging']['next'] will be None before ['paging']['cursors']['after']
        while 'paging' in response and response['paging']['next']:
            query['after'] = response['paging']['cursors']['after']
            response = self.get_response(method,url,query,data,headers)
            yield response
    
    def get_response(self,method='GET',url=None,query=None,data=None,headers=None):

        # method
        method = method.upper()
        assert method in ('HEAD','GET','POST','PUT','PATCH','DELETE')

        # url
        if url and url.lower().startswith('http'):
            pass
        elif url and url.strip():
            url = self.base_url+url
        else:
            url = self.base_url

        # query parameters (adds request limit)
        url2 = []
        if query:
            url2 = ['{}={}'.format(item,value) for item,value in query.items()]
        if self.request_limit and ((not query) or 'resSizeLimit' not in query):
            url2.append('resSizeLimit={}'.format(self.request_limit))
        if url2:
            url += '?'+'&'.join(url2)

        # data --> json
        if data != None:
            data = json.dumps(data)

        # headers
        if not headers:
            headers = self.headers

        ##print('METHOD',[method])
        ##print('URL',[url])
        ##print('DATA',[data])
        ##print('HEADERS',[headers])

        # make request, get response, make json 
        response = None
        status_code = None
        try:
            response = requests.request(method,url,data=data,headers=headers)
            status_code = response.status_code
            jdata = json.loads(response.content)
        except Exception as e:
            sys.print_exception(e)
            print('IOTERY ERROR: response data would not load as JSON')
            jdata = {'error':'response data would not load as JSON','status':status_code}
        try:
            if response != None:
                response.close()
        except Exception as e:
            sys.print_exception(e)
            print('IOTERY ERROR: unable to close urequest response')

        # error code
        if (not status_code) or status_code >= 400:
            raise IoteryException('RESPONSE DATA: '+str([status_code,jdata]))

        # all good
        return jdata

#-----------------------
# iotery exception class
#-----------------------

class IoteryException(Exception):

    def __init__(self,m):
        self.message = m

    def __str__(self):
        return json.dumps(self.message)

#-----------------------
# end
#-----------------------

##    # not required, consumes memory
##    @property
##    def current_data(self):
##        return {'base_url':self.base_url,
##                'headers':self.headers,
##                'request_limit':self.request_limit,
##                'token':self.token,
##                'team_id':self.team_id,
##                'device_key':self.device_key,
##                'device_serial':self.device_serial,
##                'device_secret':self.device_secret,
##                'device_name':self.device_name,
##                'device_uuid':self.device_uuid,
##                'device_type_uuid':self.device_type_uuid,
##                }

