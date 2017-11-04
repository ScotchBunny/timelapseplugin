How to: https://youtu.be/q9FR-tIVvJI

Disclaimer: Use this script at your own risk. The script is tested on a Wanhao Duplicator I3 V2 using RepRap Gcode flavor. It is highly recommended that you look over sample of Gcode before trying to print. The author takes no responcibility for damaged hardware as a result of using this script.

Put the scrip in the directory {Cura install directory}\plugins\PostProcessingPlugin\scripts

Octoprint captures a frame at the start of the print as well as right after the start Gcode. For the best results you should make sure that the printer is at the same postion at those instances. You can do this by "printing" a short Gcode script. For example, if the printer is at Z height 15 after the start Gcode, and you want the frames to be captured at YX (100,100), "print" this code:

G28 G0 X100 Y100 Z1

Using the GcodeEditor plugin for OctoPrint makes it more convenient to edit without re-uploading.
