# Requirements

You will also need to have access to serial ports. For Linux, you will need to do something like this:
```
sudo adduser my_username dialout
```
You have to log out and back in or reboot after changing dialout.

You need the `esptool.py' module from Espressif:

```
python3 -m pip install esptool
```

You need to know where (what port) the FunBoard is connected. In Linux you can do something like this:
```
ls -hal /dev | grep ttyUSB
```

Change to the directory containing the `bin` file.

# Erase the Flash

To put the FunBoard into program mode, hold down the **PROG** button and while holding it down, push the **RESET** button.

You can now erase the flash using the following (set the correct port):
```
esptool.py --port /dev/ttyUSB0 erase_flash
```

Now push the **RESET** button.

# Load The Image

To put the FunBoard into program mode, hold down the **PROG** button and while holding it down, push the **RESET** button. 

Now you can write/re-write the image using the following (set the correct port):
```
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect -z 0x1000 esp32-idf3-20210202-v1.14.bin
```
Now push the **RESET** button. Ready to go.




