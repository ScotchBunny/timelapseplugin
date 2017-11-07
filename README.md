How to: https://youtu.be/q9FR-tIVvJI

Disclaimer: Use this script at your own risk. The script is tested on a Wanhao Duplicator I3 V2 using RepRap Gcode flavor. It is highly recommended that you look over sample of Gcode before trying to print. The author takes no responcibility for damaged hardware as a result of using this script.

Put the scrip in the directory {Cura install directory}\plugins\PostProcessingPlugin\scripts

Octoprint captures a frame at the start of the print as well as right after the start Gcode. For the best results you should make sure that the printer is at the same postion at those instances. You can do this by "printing" a short Gcode script. For example, if the printer is at Z height 15 after the start Gcode, and you want the frames to be captured at YX (100,100), "print" this code:

G28 G0 X100 Y100 Z1

Using the GcodeEditor plugin for OctoPrint makes it more convenient to edit without re-uploading.

## Note About AppImages ##

To use this script with an AppImage (e.g. for Linux), you need to extend the existing AppImage. To do so, download and run an appriate AppImage. Then run the following commands:

	mkdir ~/Cura.AppDir
	cp -arv $(mount | grep Cura | cut -f3 -d' ')/{*,.[^.]*} ~/Cura.AppDir
	cd ~/Cura.AppDir/usr/bin/plugins/plugins/PostProcessingPlugin/scripts/
	wget https://raw.githubusercontent.com/ScotchBunny/timelapseplugin/master/MoveToXYForTimelapse.py
	cd ~/Cura.AppDir
	sed -e 's,^MimeType=\(.*\);\?$,MimeType=\1;,gi' -e 's,Icon=cura-icon.png,Icon=cura-icon,gi' -i cura.desktop
	cd ~/

Now you can re-pack the AppImage:

	wget -O appimagetool "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
	chmod +x appimagetool
	./appimagetool ./Cura.AppDir

This will produce a file `Cura-x86_64.AppImage` with the Timelapse Plugin included.
