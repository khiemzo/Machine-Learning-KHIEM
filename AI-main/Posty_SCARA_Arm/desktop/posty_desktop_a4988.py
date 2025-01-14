#-----------------------------------------
# general imports
#-----------------------------------------

import time

from pynput.keyboard import Key, Listener

from posty_lib import xyz,xyz_writer,xyz_gcoder,stepper,byte_socket

#-----------------------------------------
# define posty class
#-----------------------------------------

class POSTY:

    #-----------------------------------------
    # init DEFAULTS
    #-----------------------------------------

    #-----------------------
    # xyz values
    #-----------------------

    # linear precision for plotting lines/arcs
    linear_precision = 0.005

    # up-down values
    upis   = 15 # absolute Z location for up
    downis =  0 # absolute Z location for down
        
    # drawing area
    paper_origin  = (0, 0)
    paper_end     = (6,-4) # opposite corner

    #-----------------------
    # indexing and homing
    #-----------------------

    # index point location from the paper origin
    index_point = (3/8,1/2,upis)

    # where to start drawing sequence
    start_point = (3/8,-1/4,upis)

    # home to start point sequence
    # if true, from home move x then y
    # else, from home move y they x
    home_x_then_y = True

    #-----------------------
    # xyz writer wrapper
    #-----------------------
    writer_align = 'l'
    writer_valign = 't'

    #-----------------------
    # xyz gcode wrapper
    #-----------------------
    gcoder_align = 'l'
    gcoder_valign = 't'

    #-----------------------
    # scara convertor
    #-----------------------

    # micro step factor
    z_micro_step  = 1/8
    xy_micro_step = 1/8

    # motor Steps Per Unit Distance (linear, Z only)
    scara_spudz = 1/z_micro_step

    # motor Steps Per Angle Degree
    # same for both arms
    steps_per_turn = 400
    motor_gear = 15
    big_gear = 79.4 # big_gear is unknown variable, so adjust it until drawing is square
    spad = (steps_per_turn/360) * (1/xy_micro_step) * (big_gear/motor_gear)
    scara_spad1 = spad 
    scara_spad2 = spad

    # Arm LENgth in unit distance
    scara_alen1 = 4.0
    scara_alen2 = 4.0

    # offset from the CO (cartesian origin) to the AO (arm origin)
    # only applies to X and Y
    scara_co2aox = 3 - 0.025 # compensated from theoretical
    scara_co2aoy = 1.25 

    # imagine your own arm
    scara_right_handed = False
    scara_reaching_up = False

    #-----------------------
    # step convertor
    #-----------------------

    # motor setup
    # {motor:[rotation=+1|-1,minsteps,maxsteps]}
    motors = {1:[1,-15000,15000],
              2:[1,-15000,15000],
              3:[1,  -500,  500]}

    #-----------------------
    # socket
    #-----------------------

    server_ip = '192.168.254.81'
    server_port = 10240

    #-----------------------
    # other variables
    #-----------------------

    # state/position counts
    xc = 0 # xyz values returned
    pc = 0 # position changes (step counts different from previous xyz)
    bc = 0 # bytes sent for position changes
    sc = 0 # steps send for position changes
    bc_show = True
    bc_last = 0
    bc_every = 1000

    # hold states until holdsend()
    hold_do = not True
    hold = []
    hold_11_time = 0
    hold_11_time_renew = 10 # seconds

    # step speed values in steps per second
    # use setmotorstepspeed(motor,speed)

    # motor wait time between steps in us
    # use setmotorwaitus(motor,wait)

    # default (normal) motor waits in us
    motor_xy_wait = 400
    motor_z_wait  = 800

    # ----
    motor_waits_normal  = (motor_xy_wait    ,motor_xy_wait    ,motor_z_wait)
    motor_waits_maximum = (motor_xy_wait*0.7,motor_xy_wait*0.7,motor_z_wait)
    motor_waits_draw    = (motor_xy_wait*3.0,motor_xy_wait*3.0,motor_z_wait)
    motor_waits_write   = (motor_xy_wait*3.0,motor_xy_wait*3.0,motor_z_wait)
    motor_waits_current = motor_waits_normal

    #-----------------------------------------
    # init function
    #-----------------------------------------

    def __init__(self):

        #-----------------------
        # xyz engine
        #-----------------------
        self.xyz = xyz.XYZ()
        self.xyz.linear_precision = self.linear_precision
        X,Y,Z = self.index_point
        self.xyz.maxx = X + 0.01
        self.xyz.minx = X - 0.01
        self.xyz.maxy = Y + 0.01
        self.xyz.miny = Y - 0.01
        self.xyz.maxz = self.upis + 0.01
        self.xyz.minz = self.downis - 0.01

        #-----------------------
        # xyz writer wrapper
        #-----------------------
        self.writer = xyz_writer.XYZWriter(self.xyz)
        self.writer.align = self.writer_align
        self.writer.valign = self.writer_valign
        self.writer.upis = self.upis
        self.writer.downis = self.downis
        self.writer.setwritespeed = self.setwritespeed
        self.writer.setnormalspeed = self.setnormalspeed
        self.writer.send = self.holdsend

        #-----------------------
        # xyz gcode wrapper
        #-----------------------
        self.gcoder = xyz_gcoder.XYZGcoder(self.xyz)
        self.gcoder.upis = self.upis
        self.gcoder.downis = self.downis
        self.gcoder.setdrawspeed = self.setdrawspeed
        self.gcoder.setnormalspeed = self.setnormalspeed
        
        #-----------------------
        # scara translator
        #-----------------------
        self.scara = stepper.SCARA()
        self.scara.spudz = self.scara_spudz
        self.scara.spad1 = self.scara_spad1
        self.scara.spad2 = self.scara_spad2
        self.scara.alen1 = self.scara_alen1
        self.scara.alen2 = self.scara_alen2
        self.scara.co2aox = self.scara_co2aox
        self.scara.co2aoy = self.scara_co2aoy 
        self.scara.right_handed = self.scara_right_handed
        self.scara.reaching_up = self.scara_reaching_up
        self.scara.set_zero_angles()
        self.s1,self.s2,self.s3 = 0,0,0

        #-----------------------
        # socket client
        #-----------------------
        self.socket = byte_socket.Byte_Socket()
        self.socket.server_ip = self.server_ip
        self.socket.server_port = self.server_port
        # create socket function shortcuts
        # only ones likely to be used by parent scripts
        self.connect = self.socket.connect
        self.disconnect = self.socket.disconnect
        self.sendRFD = self.socket.sendRFD
        self.sendEOD = self.socket.sendEOD
        self.waitEOD = self.socket.waitEOD
        self.flush = self.socket.flush

    #-----------------------------------------
    # sugar functions 
    #-----------------------------------------

    def setmaxspeed(self):
        print('SET MAX SPEED:',self.motor_waits_maximum)
        self.motor_waits_current = self.motor_waits_maximum
        self.setmotorwaitsus(self.motor_waits_maximum)
        
    def setnormalspeed(self):
        print('SET NORMAL SPEED:',self.motor_waits_normal)
        self.motor_waits_current = self.motor_waits_normal
        self.setmotorwaitsus(self.motor_waits_normal)

    def setdrawspeed(self):
        print('SET DRAW SPEED:',self.motor_waits_draw)
        self.motor_waits_current = self.motor_waits_draw
        self.setmotorwaitsus(self.motor_waits_draw)

    def setwritespeed(self):
        print('SET WRITE SPEED:',self.motor_waits_write)
        self.motor_waits_current = self.motor_waits_write
        self.setmotorwaitsus(self.motor_waits_write)

    def up(self):
        self.moveto(z=self.upis)
        print('P UP')

    def down(self):
        self.moveto(z=self.downis)
        print('P DOWN')

    def home(self): # move into index position

        # get values
        X,Y,Z = self.index_point
        x,y,z = self.start_point

        # move to emoh location        
        print('HEADING HOME:',(x,y))
        self.up()
        self.moveto(x,y)

        # pen is locked on paper
        # allow travel to Y index (off paper)
        self.xyz.maxy = Y + 0.02

        # move to index
        print('HEADING TO INDEX:',(X,Y))
        if self.home_x_then_y:
            self.moveto(x=X)
            self.moveto(y=Y)
        else:
            self.moveto(y=Y)
            self.moveto(x=X)

    def emoh(self): # move out of index position, emoh::home

        # get values
        X,Y,Z = self.index_point
        x,y,z = self.start_point
        xo,yo = self.paper_origin
        xe,ye = self.paper_end

        # set x min-max
        self.xyz.minx = xo + 0.02
        self.xyz.maxx = xe - 0.02

        # allow Y travel outside paper margin
        self.xyz.maxy = Y  + 0.02

        # set y min (bottom of paper)
        self.xyz.miny = ye + 0.02

        # move out
        print('HEADING OUT:',(x,y))
        self.up()
        if self.home_x_then_y:
            self.moveto(y=y)
            self.moveto(x=x)
        else:
            self.moveto(x=x)
            self.moveto(y=y)

        # reset y max (top of paper)
        self.xyz.maxy = yo - 0.02

        # pen is locked onto paper
        print('LIMITS:',(self.xyz.minx,self.xyz.maxy),(self.xyz.maxx,self.xyz.miny))

    def testpattern(self,x,y,size=1,center=True):

        # radius
        half = size/2

        # start up
        self.up()

        # go to start point
        if center:
            self.moveto(x-half,y+half)
        else:
            self.moveto(x,y)

        # write speed and down
        self.setwritespeed()
        self.down()

        # square        
        self.move(size)
        self.move(y=-size)
        self.move(-size)
        self.move(y=size)

        # make X
        self.move(size,-size)
        self.up()
        self.move(y=size)
        self.down()
        self.move(-size,-size)
        
        # up and move for circle 1
        self.up()
        self.move(y=half)

        # down and circle
        self.down()
        self.arc(r=half,R=-1)

        # up and move for circle 2
        self.up()
        #self.move(half*0.75)
        self.arc(half*0.75)

        # down and circle
        self.down()
        self.arc(r=half*.25,R=-1)

        # up and normal speed
        self.up()
        self.setnormalspeed()

    #-----------------------------------------
    # functions 
    #-----------------------------------------

    def on(self,wait_after=0.25):
        print('TURNING ON')
        self.socket.sendints([14])
        self.sendwait(wait_after)

    def off(self):
        print('TURNING OFF')
        self.socket.sendints([13])

    def index(self):

        print('INDEX:')
        input('Place device at coordinates {} with pen UP.\nThen press ENTER to continue.'.format(self.index_point[:2]))

        # get locations
        index_steps,true_index_point = self.scara.translate(*self.index_point)

        # set xyz location
        self.xyz.setxyz(*true_index_point)

        # set step location
        self.s1,self.s2,self.s3 = index_steps

    def sendwait(self,seconds):
        print('WAIT_S:',seconds)
        return self.socket.sendints([29,self.getwaitus(seconds*1000000)])

    def sendwaitms(self,ms):
        print('WAIT_M:',ma)
        return self.socket.sendints([29,self.getwaitus(ms*1000)])

    def sendwaitus(self,us):
        print('WAIT_U:',us)
        return self.socket.sendints([29,self.getwaitus(us)])

    def getwaitus(self,us):

        # a wait value is a single byte
        # bits 7-3 represent a number 0-63
        # bits 2-0 represent an exponent 0-7
        # the exponent is a 10th power (10**exponent)
        # the number * (10**exponent) == value
        # the max value is 63*(10**7) = 630,000,000
        # this is the microseconds to wait (time.ticks_us)
        # wait values are within 10% of target using this method

        exponent = 0

        while round(us,0) > 63:
             us /= 10
             exponent += 1

        return (int(round(us,0)) << 3) + exponent

    def setmotorstepspeed(self,motor,speed):
        # convert steps/sec to wait time in us
        return self.setmotorwaitus(motor,1000000/speed)

    def setmotorwaitsus(self,waits):
        for x in range(len(waits)):
            self.setmotorwaitus(x+1,waits[x])

    def setmotorwaitus(self,motor,wait):

        payload = [22,motor]+self.socket.int22intlistbe(wait)

        if self.hold_do:
            self.hold += payload
            return True
        else:
            return self.socket.sendints(payload)

    def holdsend(self):
        print('SENDING HOLD:',len(self.hold))
        if self.hold:
            self.socket.sendints(self.hold)
            self.hold = []
        else:
            self.socket.sendints([11]) # keep socket open
        self.hold_11_time = time.time()

    #-----------------------------------------
    # manual movement 
    #-----------------------------------------

    # flags
    manual_ctrl = False
    manual_x = 0.005
    manual_y = 0.005
    manual_z = 0.5

    def manual_index(self,and_off=True):

        # get values
        X,Y,Z = self.index_point

        # expand limits
        self.xyz.maxx = X + 1
        self.xyz.minx = X - 1
        self.xyz.maxy = Y + 1
        self.xyz.miny = Y - 1
        self.xyz.maxz = self.upis + 100
        self.xyz.minz = self.downis - 100

        # movement
        self.manual(and_off)

        # get locations
        index_steps,true_index_point = self.scara.translate(X,Y,Z)

        # set xyz location
        self.xyz.setxyz(*true_index_point)

        # set step location
        self.s1,self.s2,self.s3 = index_steps

        # reset limits
        self.xyz.maxx = X + 0.01
        self.xyz.minx = X - 0.01
        self.xyz.maxy = Y + 0.01
        self.xyz.miny = Y - 0.01
        self.xyz.maxz = self.upis + 0.01
        self.xyz.minz = self.downis - 0.01

        # done
        return self.xyz.current_rounded()     

    def manual(self,and_off=True):

        # must have a connection
        if (not self.socket) or (not self.socket.socket):
            print('SOCKET to POSTY is not open.')
            return

        # turn posty on
        self.on()

        # print instructions
        print('MANUAL INDEX STARTED')
        print('Adjust X: left right keys')
        print('Adjust Y: up down keys')
        print('Adjust Z: ctrl-up ctrl-down')
        print('Press ESC or Q to continue.')

        # define and start listener in blocking mode
        with Listener(on_press=self.manual_on_press,on_release=self.manual_on_release,suppress=True) as listener:
            listener.join()

        # turn posty on
        if and_off:
            self.off()

    # action on press
    def manual_on_press(self,key):

        # stop listener
        if key in (Key.enter,'Q','q'):
            return False

        # ctrl key on
        elif key == Key.ctrl:
            self.manual_ctrl = True

        # adjust
        elif key in (Key.up,Key.down,Key.left,Key.right):

            # Z axis
            if self.manual_ctrl:
                if key in (Key.left,Key.up):
                    self.move(z=self.manual_z)
                else:
                    self.move(z=-self.manual_z)

            # X axis
            elif key == Key.right:
                self.move(x=self.manual_x)
            elif key == Key.left:
                self.move(x=-self.manual_x)

            # Y axis
            elif key == Key.up:
                self.move(y=self.manual_y)
            elif key == Key.down:
                self.move(y=-self.manual_y)

    # action on release
    def manual_on_release(self,key):

        pass

##        # ctrl key off
##        if key == Key.ctrl:
##            self.manual_ctrl = False
##
##        # stop listener
##        elif key in (Key.esc,'Q','q'):
##            return False

    #-----------------------------------------
    # base movement 
    #-----------------------------------------

    def moveto(self,x=None,y=None,z=None):

        # current xyz location
        truexyz = self.xyz.getxyz()

        # iterate through track points
        for X,Y,Z in self.xyz.moveto(x,y,z):
            truexyz = self.xyz_steps_send(X,Y,Z)

        # reset xyz to true values
        self.xyz.setxyz(*truexyz)
        
    def move(self,x=0,y=0,z=0):

        # current xyz location
        truexyz = self.xyz.getxyz()

        # iterate through track points
        for X,Y,Z in self.xyz.move(x,y,z):
            truexyz = self.xyz_steps_send(X,Y,Z)

        # reset xyz to true values
        self.xyz.setxyz(*truexyz)
        
    def arcto(self,x=None,y=None,z=None,cx=None,cy=None,r=None,D=None,R=1,T=0):

        # current xyz location
        truexyz = self.xyz.getxyz()

        # iterate through track points
        for X,Y,Z in self.xyz.arcto(x,y,z,cx,cy,r,D,R,T):
            truexyz = self.xyz_steps_send(X,Y,Z)

        # reset xyz to true values
        self.xyz.setxyz(*truexyz)
        
    def arc(self,x=0,y=0,z=0,cx=0,cy=0,r=None,D=None,R=1,T=0):

        # current xyz location
        truexyz = self.xyz.getxyz()

        # iterate through track points
        for X,Y,Z in self.xyz.arc(x,y,z,cx,cy,r,D,R,T):
            truexyz = self.xyz_steps_send(X,Y,Z)

        # reset xyz to true values
        self.xyz.setxyz(*truexyz)
        
    def write(self,text,x=None,y=None,height=None,maxwidth=None,font=None,csep=None,lsep=None,align=None,valign=None,rotate=0):

        # current xyz location
        truexyz = self.xyz.getxyz()

        # iterate through track points
        for X,Y,Z in self.writer.write(text,x,y,height,maxwidth,font,csep,lsep,align,valign,rotate):
            truexyz = self.xyz_steps_send(X,Y,Z)

        # reset xyz to true values
        self.xyz.setxyz(*truexyz)
        
    def gcode(self,file,width=None,height=None,align=None,valign=None,origin_bottom_left=True,use_start_code=True,rotate=0):

        # current xyz location
        truexyz = self.xyz.getxyz()

        # iterate through track points
        for X,Y,Z in self.gcoder.run_file(file,width,height,align,valign,origin_bottom_left,use_start_code,rotate):
            truexyz = self.xyz_steps_send(X,Y,Z)

        # reset xyz to true values
        self.xyz.setxyz(*truexyz)

    def xyz_steps_send(self,x,y,z):

        # count xyz points
        self.xc += 1

        # convert point to motor 1,2,3 step values
        (s1,s2,s3),(x,y,z) = self.scara.translate(x,y,z)
        #print('    STEPS:',[s1,s2,s3])

        # motor step limits 
        s1 = min(self.motors[1][2],max(self.motors[1][1],s1))
        s2 = min(self.motors[2][2],max(self.motors[2][1],s2))
        s3 = min(self.motors[3][2],max(self.motors[3][1],s3))

        # position change
        if (s1,s2,s3) != (self.s1,self.s2,self.s3):

            # count position changes
            self.pc += 1

            # differences
            d1 = s1-self.s1
            d2 = s2-self.s2
            d3 = s3-self.s3
            #print('    DIFF:',[d1,d2,d3])

            # make changes
            if d1:
                self.motor_steps_send(1,d1)
            if d2:
                self.motor_steps_send(2,d2)
            if d3:
                self.motor_steps_send(3,d3)               
            
            # reset step counts
            self.sc += d1 + d2 + d3
            self.s1 = s1
            self.s2 = s2
            self.s3 = s3

        # keep socket open
        if self.hold_do and self.hold_11_time + self.hold_11_time_renew - 0.5 <= time.time():
            self.socket.sendints([11]) # keep socket open
            self.hold_11_time = time.time()

        # notify
        if self.bc_show and self.bc >= self.bc_last + self.bc_every:
            print('COUNTS:',self.xc,self.pc,self.bc,self.sc)
            self.bc_last += self.bc_every

        # return actual location
        #print('    END:',[round(x,3),round(y,3),round(z,3)])
        return x,y,z

    def motor_steps_send(self,motor,steps):

        # limit motors
        motor = max(min(int(motor),3),1)

        # adjust step direction from motor setup
        steps *= self.motors[motor][0]

        # determine rotation
        # 0 = normal|positive|forward
        # 1 = invert|negative|reverse
        rotation = 0
        if steps < 0:
            rotation = 1

        # absolute step integer
        steps = int(abs(steps))

        # send in blocks of max 16
        while steps:
            block = min(16,steps)
            extra = block - 1 
            value = (motor << 5) + (rotation << 4) + extra
            if self.hold_do:
                self.hold += [value]
            else:
                self.socket.sendints([value])
            self.bc += 1
            steps -= block
            #print('        SENT:',[motor,rotation,extra])

#-----------------------------------------
# end
#-----------------------------------------
