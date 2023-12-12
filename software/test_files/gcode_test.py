import time
import serial

# COM4 115200
ser = serial.Serial('/dev/ttyUSB0', 115200)
time.sleep(2)
ser.write(str.encode("G90\r\n"))
time.sleep(1)
ser.write(str.encode("G0 Z5\r\n"))
time.sleep(1)
ser.write(str.encode("G0 Z0\r\n"))
time.sleep(1)
ser.write(str.encode("G0 Z5\r\n"))
