import sys
import Adafruit_DHT
import time
from board import SCL, SDA
import busio
from adafruit_seesaw.seesaw import Seesaw

i2c_bus = busio.I2C(SCL, SDA)
ss = Seesaw(i2c_bus, addr=0x36)

# Parse command line parameters.
# sensor_args = { '11': Adafruit_DHT.DHT11,
#                 '22': Adafruit_DHT.DHT22,
#                 '2302': Adafruit_DHT.AM2302 }
# if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
#     sensor = sensor_args[sys.argv[1]]
#     pin = sys.argv[2]
# else:
#     print('Usage: sudo ./Adafruit_DHT.py [11|22|2302] <GPIO pin number>')
#     print('Example: sudo ./AdafruitDHT.py 2302 4 - Read from an AM2302 connected to GPIO pin #4')
#     sys.exit(1)
sensor = Adafruit_DHT.AM2302
pin = 4

# temperature = temperature * 9/5.0 + 32

while True:
    # read moisture level through capacitive touch pad
    touch = ss.moisture_read()

    # read temperature from the temperature sensor
    temp = ss.get_temp()
    
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

    print("temp: " + str(temp) + "  moisture: " + str(touch))
    time.sleep(1)

    if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
    else:
        print('Failed to get reading. Try again!')
        sys.exit(1)