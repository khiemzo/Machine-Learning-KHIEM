#-----------------------
# notify
#-----------------------

print('LOAD: gpio_adc.py')

#-----------------------
# imports
#-----------------------

from machine import Pin, ADC
import time

#-----------------------
# voltage
#-----------------------

# adc steps per volt at 3.3v
spv = 1060
spv_file_name = 'board_voltage.config'
try:
    with open(spv_file_name) as f:
        spv = float(f.read().strip())
        f.close()
    print('ADC SPV: loaded',spv)
except:
    print('ADC SPV: not loaded, default is',spv)

def calibrate(pin,voltage=2.8,refv=3.3):

    global spv

    adc = ADC(Pin(pin))
    adc.width(ADC.WIDTH_12BIT)
    adc.atten(ADC.ATTN_11DB)

    value = 0
    for x in range(1000):
        value += adc.read()
        time.sleep_ms(1)

    value = value/1000
    value = value/voltage

    if refv != 3.3:
        value *= 1.515152

    spv = value

    with open(spv_file_name,'w') as f:
        f.write(str(spv)+'\n')
        f.close()

    print('ADC SPV:',spv)

    return spv    

def watch_voltage(pin,ref5=False,samples=10,wait_ms=10):
    while 1:
        print('{:1.4f}'.format(avg_voltage(pin,ref5,samples,wait_ms)))

def avg_voltage(pin,ref5=False,samples=10,wait_ms=100):
    t = voltage(pin,ref5)
    for x in range(samples-1):
        time.sleep_ms(wait_ms)
        t += voltage(pin,ref5)
    return t/samples

def voltage(pin,ref5=False):

    adc = ADC(Pin(pin))
    adc.width(ADC.WIDTH_12BIT)
    adc.atten(ADC.ATTN_11DB)

    value = adc.read()/spv

    # calculate voltage
    if ref5:
        return 1.515152 * value
    else:
        return value

    # this generally within 10%
    # anything else will probably require a table

#-----------------------
# end
#-----------------------

