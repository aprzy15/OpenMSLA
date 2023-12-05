# Hardware Overview

### Donor Printer
The majority of the printer mechanical components are salvaged from a Phrozen Sonic Mighty 4K. At ~$400 the Sonic Mighty strikes a good balance between cost, quality and size. The LCD base plate, Z actuation arm, build plate, vat, and LED array are salvaged from the Sonic Mighty for use in this project. Unfortuately the LCD that comes with the Sonic mighty directly connects to the main control board via a MIPI cable. Due to the cloased source nature of the Phrozen control board running Chitubox firmware, reverse engineering the communication protocol between the board and the LCD mask would be a significant effort. The easier route is to purchase a new LCD mask off the shelf along with a dedicated LCD driver that allows for connection to a host PC over HDMI.

### Electrical Block Diagram

<p align="center" width="100%">
    <img width="90%" src="https://github.com/aprzy15/OpenMSLA/assets/14866378/b24b2e78-6ec9-4f5b-8759-257b7d0c41b7">
</p>

The OpenMSLA printer uses a Raspberry Pi which runs that main control software. The Pi interfaces with an SKR v1.4 Turbo control board running a flavor of Marlin to control the position of the Z axis actuator and the LCD driver board to display images to the LCD mask. The 24V LED curing array is controlled by a spare 5V fan PWM port on the SKR board via the solid state relay. The printer can be operated remotely over a local network or directly through the user interface mounted on the front of the printer which consists of a character LCD display and an encoder wheel for user input. One of the Pi's usb ports is exposed on the front panel to allow for insertion of a USB drive.

### TODO
- Covers need to be extended around the perimeter of the frame to prevent light bleed from the LED curing array.
- Make rear cover for the Raspberry Pi
- Cable management :)


<p align="center" width="100%">
    <img width="50%" src="https://github.com/aprzy15/OpenMSLA/assets/14866378/d4702288-e40c-4909-994c-6f0e7948dac5">
</p>


<p align="center" width="100%">
    <img width="50%" src="https://github.com/aprzy15/OpenMSLA/assets/14866378/c772844f-ed9f-4d75-82bb-d293b66ab6fb">
</p>
