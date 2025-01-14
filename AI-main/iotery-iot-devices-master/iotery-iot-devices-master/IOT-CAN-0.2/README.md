# Documentation



## Connecting

### Putty

Coming soon to a theater near you.

### Picocom

In Linux, you must add your username to the `dialout` group and then **log out** or **reboot**.
```
sudo adduser your_username dialout
```

Install:
```
sudo apt install picocom
```

Connect:
```
picocom -b 115200 /dev/ttyUSB1
```
Be sure to set your port to the correct one.

Disconnect:

Use `ctrl-a crtl-x` to exit picocom and return to the command prompt.

### Python + PySerial

Ref: [PySerial Docs](https://pythonhosted.org/pyserial/)

Add your username to the `dialout` group and then **log out** or **reboot**.
```
sudo adduser your_username dialout
```

Add the PySerial module from the command line:
```
python3 -m pip install pyserial
```

Basic usage in Python:
```
uart = serial.Serial('/dev/ttyUSB1',115200) # 9600,8,N,1 is default

uart.open()
uart.read(1024)
uart.write(b'some bytes')
uart.close()
```

Or this:
```
uart = serial.Serial()
uart.baudrate = 115200
uart.port = '/dev/ttyUSB1'
uart.timeout = 0

uart.open()
uart.read(1024)
uart.write(b'some bytes')
uart.close()
```

## Built In Functions

### esp32 - ESP32 Module
- `esp32.reset`
- `esp32.temp`
- `esp32.tempf`
- `esp32.hall`
- `esp32.memory`
- `esp32.flash`

### board - Iotery Board Functions
- `board.sleep(secs)`
- `board.orientation()`
- `board.name`
- `board.date`
- `board.temp`
- `board.tempf`
- `board.set_temp(t)`
- `board.set_tempf(t)`

### gps - Global Positioning System
- `gps.reset(mode='hot',set_defaults=True,wait=0)`
- `gps.defaults()`
- `gps.set_messages()`
- `gps.easy()`
- `gps.easy_off()`
- `gps.dgps()`
- `gps.dgps_off()`
- `gps.sleep()`
- `gps.wake(wait_for=0.1)`
- `gps.rawdata`
- `gps.hasfix`
- `gps.fulldata`
- `gps.datetime`
- `gps.location`
- `gps.course`
- `gps.sats`

### acc - LIS3DH Accelerometer
- `acc.reset()`
- `acc.to_write(address,advance=True)`
- `acc.to_read(address,advance=True)`
- `acc.get_chip()`
- `acc.set_config()`
- `acc.set_sensitivity()`
- `acc.set_grange(R=2)`
- `acc.set_high_resolution(R=0)`
- `acc.set_low_power(LP=0)`
- `acc.set_rate(R=0)`
- `acc.temp_offset_load()`
- `acc.set_temp(t)`
- `acc.set_tempf(t)`
- `acc.get_status(value=None)`
- `acc.get_adc_raw()`
- `acc.get_adc()`
- `acc.xyz()`
- `acc.gforces_data()`
- `acc.angles_data()`
- `acc.temp`
- `acc.tempf`
- `acc.gforces`
- `acc.acceleration`
- `acc.angles`
- `acc.orientation`

### can - MCP2515 Controller Area Network Interface
- `can.reset()`
- `can.interrupt_clear()`
- `can.read(address,nbytes=1)`
- `can.read_buffers()`
- `can.read_status()`
- `can.read_rx_status()`
- `can.write(address,somebytes)`
- `can.write_tx_buffer(buffer=0,skip_id=0,data=None)`
- `can.send_tx_buffer(buffer=0)`
- `can.bit_modify(address,mask,value,check=0)`
- `can.bit_check(address,mask,value)`
- `can.set_config()`
- `can.set_mode(mode='normal')`
- `can.clear_overflow_flags()`
- `can.set_filter(f=[0,0,0,0],m=[0,0,0,0])`
- `can.clear_filter()`
- `can.set_nbr(nbr,set_mode=True)`
- `can.testbit(integer,bit)`
- `can.bitisset(register,bit)`
- `can.sending(buffer)`
- `can.clear_recv_buffer()`
- `can.clear_send_buffer()`
- `can.clear_buffers()`
- `can.start_buffer_thread()`
- `can.stop_buffer_thread(timeout=10)`
- `can.buffer_thread()`
- `can.recv_fast(mn=0,mx=1000,to=1000)`
- `can.recv(n=1,blocking=True,timeout=0,timeout_value='error')`
- `can.send(message,timeout=10,return_value=True,timeout_value='error')`
- `can.bounce(N=1)`
- `can.build_message(address=0,extended=0,data=[])`
- `can.parse_message(message)`
- `can.build_canopen(address=0,function_code=0,data=[])`
- `can.parse_canopen(message)`
- `can.build_j1939(priority=6,reserved=0,datapage=0,pduformat=0,target=0,source=0,pgn=None,data=[])`
- `can.parse_j1939(message,as_dict=False)`
- `can.parse_29data(message)`

### sdcard - Micro SD Card
- `sdcard.error(e=None,s='SDCard not mounted.',unmount=False)`
- `sdcard.sdpath(path=None)`
- `sdcard.mount()`
- `sdcard.unmount(show=True)`
- `sdcard.format(warn=True)`
- `sdcard.tree(d=None)`
- `sdcard.mkdir(d)`
- `sdcard.rmdir(d)`
- `sdcard.remove(f)`
- `sdcard.isfile(f)`
- `sdcard.isdir(d)`
- `sdcard.exists(fd)`
- `sdcard.pf(f)`
- `sdcard.open(f,mode='r',encoding='utf8')`

### beeper - Buzzer Sounds
- `beeper.beep(freq=None,secs=None,vol=None,duty=None)`
- `beeper.beepn(count=1,freq=None,secs=None,vol=None,duty=None,wait=None)`
- `beeper.beep2(freq=None,freq2=None,secs=None,vol=None,duty=None,fcps=100)`
- `beeper.play(notestring=None,root=None,beat=None,vol=None,duty=None)`
- `beeper.jingle(vol=None)`
- `beeper.jingle2(vol=None)`
- `beeper.shave(vol=None)`
- `beeper.axelf(vol=None)`

### interrupts - 
- `interrupts.add_falling_pin(pin,name,samples=5,sample_period=10,callback2=None,show=True)`
- `interrupts.add_rising_pin(pin,name,samples=5,sample_period=10,callback2=None,show=True)`
- `interrupts.remove(name)`
- `interrupts.clear(name=None)`
- `interrupts.names()`
- `interrupts.check(name=None)`
- `interrupts.get(name)`
- `interrupts.call(name)`
- `interrupts.set_callback2(name,callback2=None)`
- `interrupts.callback(pin,name=None,target=0,samples=5,sample_period=10)`

### led1 - Blue Board LED
- `led1.on()`
- `led1.off()`
- `led1.blink(count=1,ontime=None,offtime=None)`

### wlan - WiFi Network Connect
- `wlan.make_ready()`
- `wlan.scan(nets=None,show=True)`
- `wlan.network_iterator()`
- `wlan.connect_manager(essid=None,password=None,hostname=None,macaddress=None)`
- `wlan.connect(essid,password=None,hostname=None,dns=None,macaddress=None,timeout=None,show=True)`
- `wlan.disconnect(timeout=None,show=True)`
- `wlan.isconnected`
- `wlan.status`
- `wlan.rssi`
- `wlan.essid`
- `wlan.dhcp_hostname`
- `wlan.mac_address`
- `wlan.ip_address`

### rtc - Real Time Clock
- `rtc.ntp_set()`
- `rtc.set(datetime_tuple)`
- `rtc.get()`
- `rtc.linux_epoch`
- `rtc.dtstamp`

### hop - SocketHop Service
- `hop.creds`
- `hop.open(username=None,password=None,email=None)`
- `hop.close(show=True)`

### st - System Tools
- `st.abspath(fd=None)`
- `st.isfile(f)`
- `st.isdir(d)`
- `st.exists(fd)`
- `st.tree(d=None,i=0)`
- `st.mkdir(d)`
- `st.remove(f)`
- `st.rmdir(d,root=False)`
- `st.pf(f)`
- `st.printfile(f)`
- `st.pp(obj,depth=0,indentline=True,newline=True,end='\n')`
- `st.ps(obj,depth=0,indentline=True,newline=True,jsonify=False)`
- `st.reload(module)`
- `st.du(d=None,h='MB',show=True,rt=False)`
- `st.memp(show=True,collect=True,rt=False)`
