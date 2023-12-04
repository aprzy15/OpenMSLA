
## OpenMSLA File Spec
The MSLA file is a zip folder with the .zip extension renamed to .msla
The MSLA file contains three main things:
- printconfig.ini file
- printplan.gcode file
- Collection of enumerated PNG files

### printconfig.ini
The print config file contains general information for the build: filename, number of layers, layer height, date time, material info, etc.
As of 11/18/2023 only the number of layers variable is actually used by the machine. The rest of the variables are mainly for record keeping purposes.

### printplan.gcode
The gcode file contains all of the commands for producing the build. This gcode is intended to be sent to a control board running Marlin. There are the following customizations to allow for the board to be used for resin printing purposes:
- ```M106 P0 S[0-255]```
	- The ```P0``` fan port is used to controller the solid state relay which controls power to the LED array. A value of 0 closes the relay, 255 opens the relay. Despite being a PWM port, this command can only be used to fully close or fully open the relay. Therefore only values of 0 and 255 should be used.
- ```M118 R1 I1```
		- ```M118``` is a standard Marlin M command that sends a serial message back to the host computer (in this case the Raspberry Pi). In this case the control board sends the command ```R1 I1``` back to the host. ```R``` Designates that this is a host command to be executed on the host computer. ```R1``` is the host command to display an image to the LCD. ```I1``` designates the index of the image to show. In this case the 1st image is displayed.
## OpenMSLA Gcode command architecture
An MSLA printer requires precise timing of image exposure and light exposure to accurately print parts. In the case of this machine, the image exposure is controlled by the host computer and timing of the LED array is controlled by the Gcode controller. This architecture necessitates precise timing between the host computer and Gcode controller.

When the Gcode controller is sent a Gcode command, this command is stored in an internal buffer until it is ready to be executed. When this internal buffer is filled the  controller will cease to accept new commands. This means that while the host computer knows precisely when a command is sent to the control board, it is "blind" as to when the command is actually executed. This introduces complications when trying to precisely time the display of layer to the LCD with the exposure by the LED array.

When Gcode controller is send a Gcode command, the host will wait until either a response is received or the timeout limit is reached. For most standard gcode commands the host waits for the ```ok``` response. For ```M118``` commands the host will wait for the specified serial message to be received, stalling the sending of gcode commands until this response is received.

The solution to this timing issue is to have the control board be the orchestrator during the print to control the timing of the LED array as well as the LCD. Because the LCD is controlled from the host computer this requires that the control board issue a command to the host computer when it wants a specific image to be displayed. Hence the ```M118 R1 I1``` command described above.

Based on these rules the typical layer is organized like the following:
```
G0 Z1 F500
M118 R1 I1
M400
M106 P0 S255
G4 P500
M106 P0 S0
```
- ```G0 Z1 F500``` Moves the Z axis to a specified Z height at a specified feed rate
	- This command is typically a set of multiple Z commands that control the peeling process and setting the next layer position
- ```M118 R1 I1``` This command issues the host command to display an image
- ```M400``` This command waits for all previously issues gcode commands to finish. In the case of long Z moves, this command is necessary to make sure the Z axis is in the correct position prior to turning on the LED array.
- ```M106 P0 S55``` Turns on the LED array
- ```G4 P500``` Is a 500ms dwell time. This dictates the curing time given for the resin
- ```M106 P0 S0``` Turns of the LED array
It is unclear what the actual timing of the LED array compared the designated dwell time. It is assumed that control board executes commands fast enough that the actual time the LED array is on it not significantly different from the commanded dwell time.
