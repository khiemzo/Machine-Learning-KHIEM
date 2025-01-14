# Requirements

The `REPLace.py` script requires `pyserial`. If you want it to pre-compile your scrips for faster loading, you also need `mpy-cross`.

```
python3 -m pip install pyserial
python3 -m pip install mpy-cross
```

You will also need to have access to serial ports. For Linux, you will need to do something like the following (you have to log out and back in or reboot after changing dialout):
```
sudo adduser my_username dialout
```

You need to know where (what port) the FunBoard is connected. In Linux you can do something like this:
```
ls -hal /dev | grep ttyUSB
```

Change to the directory containing the `lib` diretory and the `REPLace.py` script.

# Pre-Load

You need to make sure the FunBoard isn't running any processes and is ready to accept input.

1. Connect to the FunBoard via your serial terminal.

1. Do a reboot `ctrl-d`.

1. Kill any running process `ctrl-c`.

1. Disconnect.

# Load All

Initially, you will want to load everything, particularly the `boot.py` file and everything in the `lib` directory. You can use the `-a` flag to do this (set the correct port):
```
./REPLace.py -p /dev/ttyUSB0 -a
```
Now push the **RESET** button. Ready to go.

# Load Selected Files

After the initial load, you can just load selected files. You can use the `-i` flag to do this (set the correct port):
```
./REPLace.py -p /dev/ttyUSB0 -i main.py somefile.py
```
Now push the **RESET** button. Ready to go.

# HELP

```
./REPLace.py -h
```





















