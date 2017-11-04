from ..Script import Script

##  MoveToXYForTimelapse v0.1
##  Moves print head to preset XY coordinate before Z change for Octoprint timelapse.
##  Written by Kasper Hald.
##  Questions and comments: @Scotch_Bunny on Twitter or ScotchBunny on Thingiverse.
##  
##  Disclaimer: Use this script at your own risk.
##  The script is tested on a Wanhao Duplicator I3 V2 using RepRap Gcode flavor.
##  It is highly recommended that you look over sample of Gcode before trying to print.
##  The author takes no responcibility for damaged hardware as a result of using this script.
##  
##  Octoprint captures a frame at the start of the print as well as right after the start Gcode.
##  For the best results you should make sure that the printer is at the same postion at those instances.
##  You can do this by "printing" a short Gcode script. For example, if the printer is at Z height 15
##  after the start Gcode, and you want the frames to be captured at YX (100,100), "print" this code:
##  
##  G28
##  G0 X100 Y100 Z1
##
##  Using the GcodeEditor plugin for OctoPrint makes it more convenient to edit without re-uploading. 

class MoveToXYForTimelapse(Script):
    def getSettingDataString(self):
        return """{
            "name": "Move To XY For Timelapse",
            "key": "MoveToXYForTimelapse",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "Frame_X":
                {
                    "label": "X coordinate",
                    "description": "X coordinate for timelapse frames.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0
                },
                "Frame_Y":
                {
                    "label": "Y coordinate",
                    "description": "Y coordinate for timelapse frames.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0
                },
                "travelSpeed":
                {
                    "label": "Travel Speed",
                    "description": "Travel speed on move.",
                    "unit": "mm/s",
                    "type": "float",
                    "default_value": 100
                },
                "framePause":
                {
                    "label": "Pause Before Frame",
                    "description": "Pause duration at frame postion before Z-change to ensure the printer is not shaking.",
                    "unit": "sec",
                    "type": "float",
                    "default_value": 1
                },
                "Retraction":
                {
                    "label": "Retract on move",
                    "description": "Retract filament when moving to frame position.",
                    "type": "bool",
                    "default_value": true
                },
                "RetractionLength":
                {
                    "label": "Retraction length",
                    "description": "Retraction length if retraction is enabled above",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 1
                },
                "RetractionSpeed":
                {
                    "label": "Retraction speed",
                    "description": "Retraction speed if retraction is enabled above",
                    "unit": "mm/s",
                    "type": "float",
                    "default_value": 25
                },
                "ZHopHeight":
                {
                    "label": "Z-Hop height on retraction",
                    "description": "If you use Z-hop on filament retraction, put in the height so it can be ignored. It should be different from your layer height. This should also be set in the Octoprint timelapse settings.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0
                },
                "UseZHop":
                {
                    "label": "Z-Hop on retraction",
                    "description": "Use Z-Hop when moving to frame position if retraction is enabled above.",
                    "type": "bool",
                    "default_value": false
                }
            }
        }"""

    def execute(self, data: list):
        frame_x = self.getSettingValueByKey("Frame_X")
        frame_y = self.getSettingValueByKey("Frame_Y")
        travelSpeed = self.getSettingValueByKey("travelSpeed")*60
        retract = self.getSettingValueByKey("Retraction")
        rLength = self.getSettingValueByKey("RetractionLength")
        rSpeed = self.getSettingValueByKey("RetractionSpeed")*60
        zHopHeight = self.getSettingValueByKey("ZHopHeight")
        zHop = self.getSettingValueByKey("UseZHop")

        pause = self.getSettingValueByKey("framePause")*1000
        if pause == 0:
            pause == 1

        printing = False
        absolutePos = True
        absoluteExtruder = False
        doingRetract = False
        doingZHop = False
        f = travelSpeed
        currentX = 0
        currentY = 0
        currentZ = 0
        currentE = 0

        #Loop through every layer in G-code
        for layer in data:
            lines = layer.split("\n")
            new_gcode = ""
            index = data.index(layer)

            #Loop through every line in layer
            for line in lines:
                
                #Check for position and extrusion modes
                if self.getValue(line, 'G') == 90:
                    absolutePos = True
                elif self.getValue(line, 'G') == 91:
                    absolutePos = False
                elif self.getValue(line, 'M') == 82:
                    absoluteExtruder = True
                elif self.getValue(line, 'M') == 83:
                    absoluteExtruder = False
                #Check if position is set without movement
                elif self.getValue(line, 'G') == 92:
                    if self.getValue(line, 'X') is not None:
                        currentX = self.getValue(line, 'X')
                    if self.getValue(line, 'Y') is not None:
                        currentY = self.getValue(line, 'Y')
                    if self.getValue(line, 'Z') is not None:
                        currentZ = self.getValue(line, 'Z')
                    if self.getValue(line, 'E') is not None:
                        currentE = self.getValue(line, 'E')

                #Check for G-code commmands that change the position
                if self.getValue(line, 'G') == 0 or self.getValue(line, 'G') == 1 or self.getValue(line, 'G') == 28:
                    
                    #Save original line values
                    g = self.getValue(line, 'G')
                    if self.getValue(line, 'X') is not None:
                        x = self.getValue(line, 'X')
                    if self.getValue(line, 'Y') is not None:
                        y = self.getValue(line, 'Y')
                    if self.getValue(line, 'E') is not None:
                        e = self.getValue(line, 'E')
                    if self.getValue(line, 'F') is not None:
                        f = self.getValue(line, 'F')

                    #Check for Z-change
                    if self.getValue(line, 'Z') is not None:

                        z = self.getValue(line, 'Z')
                        zhopForNow = 0
                            
                        #Caluculate Z-change
                        if absolutePos:
                            deltaZ = z - currentZ
                        else:
                            deltaZ = z

                        #Check if Z-change is Z-hop
                        if "%.3f" % deltaZ == "%.3f" % zHopHeight:
                            isZHop = True
                            doingZHop = True
                        elif "%.3f" % deltaZ == "%.3f" % -zHopHeight:
                            isZHop = True
                            doingZHop = False
                        else:
                            isZHop = False
                        
                        #If not Z-hop or homing command replace with new G-code
                        if g != 28 and not isZHop and deltaZ != 0 and printing:

                            new_gcode += ";TYPE:CUSTOM;added code by post processing\n;script: MoveToXYForTimelapse.py\n"

                            #If the printer is in relative position mode, change to absolute position mode
                            if not absolutePos:
                                new_gcode += "G90\n"

                            #If set to retract on move and the printer is not already doing retraction
                            if retract and not doingRetract:
                                #If the extruder is in aboslute position mode, change to relative extruder mode
                                if absoluteExtruder:
                                    new_gcode += "M83\n"
                                new_gcode += "G1 F%f E%f\n" % (rSpeed,-rLength)
                            #If set to Z-hop on move and the printer is not already doing a Z-hop
                            if zHop and not doingZHop:
                                zhopForNow = zHopHeight
                                new_gcode += "G%f F%f Z%f\n" % (g, f, zhopForNow+currentZ)

                            #Travel to frame position
                            new_gcode += "G0 F%f X%f Y%f\n" % (travelSpeed, frame_x, frame_y)

                            #Wait for in case of shaking printer and flush the G-code buffer
                            new_gcode += "G4 P%f\nG4 P1\nG4 P1\nG4 P1\nG4 P1\nG4 P1\nG4 P1\nG4 P1\nG4 P1\nG4 P1\n" % (pause)
                            #Perform Z-change, triggering the Octoprint timelapse
                            new_gcode += "G%f F%f Z%f\n" % (g, f, currentZ+zhopForNow+deltaZ)
                            #Move back to original position
                            new_gcode += "G0 F%f X%f Y%f\n" % (travelSpeed, currentX, currentY)

                            #If set to Z-hop on move and the printer is not already doing a Z-hop
                            if zHop and not doingZHop:
                                new_gcode += "G%f F%f Z%f\n" % (g, f, currentZ+deltaZ)
                            #If set to retract and Z-hop on move and the printer is not already doing a Z-hop
                            if retract and not doingRetract:
                                new_gcode += "G1 F%f E%f\n" % (rSpeed,rLength)
                                #If the extruder is in aboslute position mode, change it back
                                if absoluteExtruder:
                                    new_gcode += "M82\n"
                            
                            #If the printer is in relative position mode, change it back
                            if not absolutePos:
                                new_gcode += "G91\n"

                            #Reset old travel speed and rewrite the rest of the original line
                            new_gcode += "G%f F%f" % (g,f)
                            if self.getValue(line, 'X') is not None:
                                new_gcode += " X%f" % (x)
                            if self.getValue(line, 'Y') is not None:
                                new_gcode += " Y%f" % (y)
                            if self.getValue(line, 'E') is not None:
                                new_gcode += " E%f" % (e)
                            new_gcode += "\n"

                        else:
                            #Write original line
                            new_gcode += line + "\n"
                    else:
                        #Write original line
                        new_gcode += line + "\n"

                    #Save the current positions
                    if absolutePos:
                        if self.getValue(line, 'X') is not None:
                            currentX = x
                        if self.getValue(line, 'Y') is not None:
                            currentY = y
                        if self.getValue(line, 'Z') is not None:
                            currentZ = z
                    else:
                        if self.getValue(line, 'X') is not None:
                            currentX += x
                        if self.getValue(line, 'Y') is not None:
                            currentY += y
                        if self.getValue(line, 'Z') is not None:
                            currentZ += z
                    
                    #Save the current extrusion
                    if self.getValue(line, 'E') is not None:
                        if absoluteExtruder:
                            deltaE = e - currentE
                            currentE = e
                        else:
                            deltaE = e
                            currentE += e

                        #Check if the printer has performed retract
                        if deltaE < 0:
                            doingRetract = True
                        elif deltaE > 0:
                            doingRetract = False

                elif ";LAYER_COUNT:" in line and not printing:
                    #Start on frame position between printer start Gcode and Cura Gcode
                    if not absolutePos:
                        new_gcode += "G90\n"
                    new_gcode += "G0 F%f X%f Y%f\n" % (travelSpeed, frame_x, frame_y)
                    new_gcode += "G4 P%f\nG4 P1\nG4 P1\nG4 P1\nG4 P1\nG4 P1\nG4 P1\nG4 P1\nG4 P1\nG4 P1\n" % (pause)
                    if not absolutePos:
                        new_gcode += "G91\n"
                    new_gcode += line + "\n"
                    printing = True
                elif ";End of Gcode" in line:
                    #End on frame position
                    if not absolutePos:
                        new_gcode += "G90\n"
                    new_gcode += "G0 F%f X%f Y%f\n" % (travelSpeed, frame_x, frame_y)
                    new_gcode += "G4 P%f\nG4 P1\nG4 P1\nG4 P1\nG4 P1\nG4 P1\nG4 P1\nG4 P1\nG4 P1\nG4 P1\n" % (pause)
                    new_gcode += line + "\n"
                else:
                    #Write original line
                    new_gcode += line + "\n"

            #Write new layer data     
            data[index] = new_gcode[:-1] 
        
        

        #Save new data
        return data