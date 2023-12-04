from RPLCD.i2c import CharLCD
from RPi import GPIO
from time import sleep
# from state_machine import StateMachine
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)
lcd.clear()

lcd.write_string('Hello, World1!')

clk = 17
dt = 18
sw = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)

counter = 0
clkLastState = GPIO.input(clk)

try:
    while True:
        # print(GPIO.input(sw))
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
        if clkState != clkLastState:
            if dtState != clkState:
                counter += 1
            else:
                counter -= 1
            print(counter)
        clkLastState = clkState
        sleep(0.01)
finally:
    GPIO.cleanup()
