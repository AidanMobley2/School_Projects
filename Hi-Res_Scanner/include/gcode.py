import serial
import time
import math

class CNC:
    def __init__(self, port, width, height):
        self.port = port
        self.width = width
        self.height = height

    # Initializes the CNC machine and serial port so it can properly accept Gcode commands
    def init_cnc(self):
        # How far the gantry should move in both directions to allow some overlap of the images
        self.xstep = 1.5
        self.ystep = 1

        # Setting up and initializing the serial port
        self.ser = serial.Serial(self.port, 115200)
        if self.ser.is_open:
            self.ser.close()
        time.sleep(2)
        self.ser.open()
        time.sleep(2)

        # The commands to start and initialize the CNC controller
        self.init_commands = [      #Put in autohoming if possible
            "%\n",      #% is required to start Gcode program
            "G20\n",    #G20/G21 is in/mm
            "G91\n",    #G90/G91 is absolute/relative mode
            "G17\n"     #G17 is XY plane
        ]
        # Sending the init commands over the serial port
        for i in range(len(self.init_commands)):
            self.ser.write(self.init_commands[i].encode())
            time.sleep(.1)
        
        # Calculating the number of steps the scan will take based on how big the canvas is
        self.numXSteps = math.ceil(self.width/self.xstep)
        self.numYSteps = math.ceil(self.height/self.ystep)

        # Determining the Gcode commands to move the gantry in each required direction
        # Because we are using relative mode, these will be the same no matter where the gantry is
        self.move = "G01 X"+str(self.xstep)+" Y0 F20\n"
        self.nl_1 = "G01 X0 Y-"+str(self.ystep)+" F20\n"
        self.nl_2 = "G01 X-"+str((self.numXSteps-1)*self.xstep)+" Y0 F20\n"

        self.zero_1 = "G01 X-"+str(self.xstep*(self.numXSteps-1))+" Y0 F20\n"
        self.zero_2 = "G01 X0 Y"+str(self.ystep*(self.numYSteps-1))+" F20\n"
    
    # Moves the gantry so the camera is over the next section of painting
    def move_over(self):
        self.ser.write(self.move.encode())
        time.sleep((self.xstep*3)+0.2)

    # Moves the gantry so the camera is on a new line for scanning
    def new_line(self):
        self.ser.write(self.nl_1.encode())
        time.sleep((self.ystep*3)+0.2)
        self.ser.write(self.nl_2.encode())
        time.sleep((self.xstep*self.numXSteps*3)+0.2)

    def movex(self, dist):
        mov = "G01 X"+str(dist)+" Y0 F20\n"
        self.ser.write(mov.encode())
        time.sleep(abs(dist)*3+0.2)

    def movey(self, dist):
        mov = "G01 X0 Y"+str(dist)+" F20\n"
        self.ser.write(mov.encode())
        time.sleep(abs(dist)*3+0.2)
    
    # Hopefully Moves the gantry back to the zero point
    def zero(self):
        self.ser.write(self.zero_1.encode())
        time.sleep((self.xstep*self.numXSteps*3)+0.2)
        self.ser.write(self.zero_2.encode())
        time.sleep((self.ystep*self.numYSteps*3)+0.2)

    # Ends the Gcode program and frees up the serial port
    def close_cnc(self):
        self.ser.write("M30\n".encode())
        time.sleep(0.2)
        self.ser.write("%".encode())
        time.sleep(0.2)
        self.ser.close()