#!/bin/sh
# lcd_driver.sh
# navigate to home directory, then to this directory, then execute python script, then back home

# cd /
# cd home/pi/bbt
# export DISPLAY=:0
# xhost +
/usr/bin/python3 /home/admin/printer/software/lcd_driver/lcd_driver.py
# cd /
