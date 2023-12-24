import time
import serial

# COM4 115200
ser = serial.Serial('/dev/ttyACM0', 115200)
time.sleep(1)
# ser.write(str.encode("M106 P0 S255\r\n"))
# ser.write(str.encode("M106 P0 S0\r\n"))
# ser.write(str.encode("G28 Z\r\n"))
# ser.write(str.encode("G0 Z50 F1000\r\n"))

# ser.write(str.encode("M211 S0\r\n"))
# ser.write(str.encode("M500\r\n"))

ser.write(str.encode("M106 P0 S0\r\n"))
# ser.write(str.encode("M106 P0 S255\r\n"))



# while True:
#     response = ser.read_until().decode('ascii').rstrip('\n')
#     print(response)
