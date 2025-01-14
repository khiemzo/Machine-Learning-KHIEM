import math
from . import math2

class XYZ:

    # This class handles movement on the cartesian coordinate system (3D).
    # There are no limits implemented here.

    # All movement functions are iterators and yield points on a path the device should travel.
    # The granularity of the points is determined by self.linear_precision. Smaller is finer.

    # --- variables ---

    linear_precision  = 0.01
    round_precision   = 3

    currentx = 0.0
    currenty = 0.0
    currentz = 0.0

    last_rounded_xyz = (0.0,0.0,0.0)
    last_rounded_limited_xyz = (0.0,0.0,0.0)

    minx,maxx = 0,1
    miny,maxy = 0,1
    minz,maxz = 0,1

    # make this available to supers that use this class
    math2 = math2

    # --- init ---

    def __init__(self):
        pass

    # --- static functions ---

    def zero(self):
        self.currentx = 0.0
        self.currenty = 0.0
        self.currentz = 0.0
        self.last_rounded_xyz = (0.0,0.0,0.0)

    def setxyz(self,x,y,z):
        self.currentx = x
        self.currenty = y
        self.currentz = z
        self.last_rounded_xyz = self.current_rounded()

    def seteach(self,x=None,y=None,z=None):
        if x != None:
            self.currentx = x
        if y != None:
            self.currenty = y
        if z != None:
            self.currentz = z
        self.last_rounded_xyz = self.current_rounded()

    def where(self):
        return self.last_rounded_xyz

    def getxyz(self):
        return self.last_rounded_xyz

    def current_rounded(self):
        return (round(self.currentx,self.round_precision),
                round(self.currenty,self.round_precision),
                round(self.currentz,self.round_precision))

    def current_rounded_limited(self):
        x = max(self.minx,min(self.maxx,self.currentx))
        y = max(self.miny,min(self.maxy,self.currenty))
        z = max(self.minz,min(self.maxz,self.currentz))
        return (round(x,self.round_precision),
                round(y,self.round_precision),
                round(z,self.round_precision))

    def same_rounded(self,n1,n2):
        # local function to allow precision changes on the fly
        return round(n1,self.round_precision) == round(n2,self.round_precision)

    def distance_to(self,x,y,z):
        return math2.distance((self.currentx,self.currenty,self.currentz),(x,y,z))

    # --- movement functions (iterators) ---

    # coordinated linear movement to an absolute point
    def moveto(self,x=None,y=None,z=None):

        #print('MOVETO:',[x,y,z])
        #import time
        #time.sleep(0.1)

        if x == None:
            x = self.currentx
        if y == None:
            y = self.currenty
        if z == None:
            z = self.currentz

        yield from self.move(x-self.currentx,
                             y-self.currenty,
                             z-self.currentz,
                             )

    # coordinated linear movement relative to current location
    def polar(self,degrees,distance,z=0):

        # assuming current location is origin
        # x,y are distances to move from current
        x,y = math2.polar(degrees,distance)

        yield from self.move(x,y,z)

    # coordinated linear movement relative to current location
    # coordinated linear movement BASE function
    def move(self,x=0,y=0,z=0):

        # target end coordinates
        targetx = x + self.currentx
        targety = y + self.currenty
        targetz = z + self.currentz

        # steps required
        changemax = max(abs(x),abs(y),abs(z))
        steps = int(changemax/self.linear_precision) + 1 # +1 for better than linear precision

        if steps: # can't be 0

            # axes changes per step
            changex = x/steps
            changey = y/steps
            changez = z/steps

            for nada in range(steps):
                self.currentx += changex
                self.currenty += changey
                self.currentz += changez

                #current_rounded_xyz = self.current_rounded()
                #if current_rounded_xyz != self.last_rounded_xyz:
                #    self.last_rounded_xyz = current_rounded_xyz
                #    yield current_rounded_xyz

                current_rounded_limited_xyz = self.current_rounded_limited()
                if current_rounded_limited_xyz != self.last_rounded_limited_xyz:
                    self.last_rounded_limited_xyz = current_rounded_limited_xyz
                    yield current_rounded_limited_xyz

            # for security and rounding errors
            self.currentx,self.currenty,self.currentz = targetx,targety,targetz

            #current_rounded_xyz = self.current_rounded()
            #if current_rounded_xyz != self.last_rounded_xyz:
            #    print('SECURITY: xyz.move final call for precision')
            #    self.last_rounded_xyz = current_rounded_xyz
            #    yield current_rounded_xyz

            current_rounded_limited_xyz = self.current_rounded_limited()
            if current_rounded_limited_xyz != self.last_rounded_limited_xyz:
                print('SECURITY: xyz.move final call for precision')
                self.last_rounded_limited_xyz = current_rounded_limited_xyz
                yield current_rounded_limited_xyz

    # 2D arc move with helix for z
    def arcto(self,x=None,y=None,z=None,cx=None,cy=None,r=None,D=None,R=1,T=0):
        'x,y,z,centerx,centery,radius,Degrees,Rotation,Turns'

        if x == None:
            x = self.currentx
        if y == None:
            y = self.currenty
        if z == None:
            z = self.currentz

        if cx == None:
            cx = self.currentx
        if cy == None:
            cy = self.currenty

        yield from self.arc(x-self.currentx,y-self.currenty,z-self.currentz,cx-self.currentx,cy-self.currenty,r,D,R,T)  

    # 2D arc move with helix for z relative to current location
    def arc(self,x=0,y=0,z=0,cx=0,cy=0,r=None,D=None,R=1,T=0):
        'x,y,z,centerx,centery,radius,Degrees,Rotation,Turns'

        # no x and y == full circle + turns
        if (not x) and (not y):

            # work from a center
            if (cx != x) or (cy != y):
                Cx,Cy = cx,cy
                r = math.hypot(cx-x,cy-y)
                if R > 0:
                    R = 1
                else:
                    R = -1

            # work from a radius
            # center is on x axis
            # travel starts in an upward direction
            elif r:
                r = abs(r)
                if R > 0:
                    R = 1
                    Cx,Cy = self.currentx-r,self.currenty
                    A1 = 180
                else:
                    R = -1
                    Cx,Cy = self.currentx+r,self.currenty

            # not enough data
            else:
                raise ValueError('No x, no y, no r, no center.')

            # start angle
            # angle from center to current point relative to x-axis
            # angle range is 180 to -180
            A1 = math2.xangle(Cx,Cy,self.currentx,self.currenty)

            # degrees rotation
            degrees = 360

        # normal, arc + turns
        else:

            # get r if needed
            if not r:
                r = math.hypot(x,y)/2
            else:
                r = abs(r)

            # center options
            center1,center2 = math2.circle_intersects(self.currentx,self.currenty,r,self.currentx+x,self.currenty+y,r)

            # choose center
            # reset R to correct values
            if R > 0:
                R = 1
                Cx,Cy = center1 # counter-clockwise rotation
            else:
                R = -1
                Cx,Cy = center2 # clockwise

            # angle from center to current point relative to x-axis
            # angle range is 180 to -180
            A1 = math2.xangle(Cx,Cy,self.currentx,self.currenty)
            #print('A1:',A1)

            # angle from center to end point relative to x-axis
            # angle range is 180 to -180
            A2 = math2.xangle(Cx,Cy,self.currentx+x,self.currenty+y)
            #print('A2:',A2)

            # degrees from A1 to A2
            # max value is < 360
            degrees = abs(A1-A2)
            #print('degrees_1:',degrees)

            # select correct arc based on start, stop, and rotation
            if R > 0:
                if A1 > A2:
                    degrees = 360-degrees
            else:
                if A1 < A2:
                    degrees = 360-degrees

        # finalize degrees (add full turns)
        degrees = (degrees + int(round(T,0))*360)*R
        #print('R:',R)
        #print('T:',int(T))
        #print('degrees_2:',degrees)
        
        # length of arc
        L = math.pi*r*degrees/180
        #print('L:',L)

        # target end point
        targetx = x + self.currentx
        targety = y + self.currenty
        targetz = z + self.currentz
        #print('target:',(targetx,targety,targetz))
        
        # steps required
        steps = int(abs(L)/self.linear_precision) + 1 # +1 for better than linear precision
        #print('steps:',steps)

        # can't be 0
        if steps:

            # change per step
            changea = degrees/steps # angle
            changez = z/steps # helix

            for nada in range(steps):
                A1 += changea
                self.currentx,self.currenty = math2.polar(A1,r)
                self.currentx += Cx
                self.currenty += Cy
                self.currentz += changez

                #current_rounded_xyz = self.current_rounded()
                #if current_rounded_xyz != self.last_rounded_xyz:
                #    self.last_rounded_xyz = current_rounded_xyz
                #    yield current_rounded_xyz

                current_rounded_limited_xyz = self.current_rounded_limited()
                if current_rounded_limited_xyz != self.last_rounded_limited_xyz:
                    self.last_rounded_limited_xyz = current_rounded_limited_xyz
                    yield current_rounded_limited_xyz

            # for security and rounding errors
            self.currentx,self.currenty,self.currentz = targetx,targety,targetz

            #current_rounded_xyz = self.current_rounded()
            #if current_rounded_xyz != self.last_rounded_xyz:
            #    print('SECURITY: xyz.arc final call for precision')
            #    self.last_rounded_xyz = current_rounded_xyz
            #    yield current_rounded_xyz

            current_rounded_limited_xyz = self.current_rounded_limited()
            if current_rounded_limited_xyz != self.last_rounded_limited_xyz:
                print('SECURITY: xyz.arc final call for precision')
                self.last_rounded_limited_xyz = current_rounded_limited_xyz
                yield current_rounded_limited_xyz
        






        

##        yield from self.arcbase(Cx,Cy,None,x,y,z,rotation)
##        
##    # 2D arc move with helix for z relative to current location
##    # arc movement BASE function
##    def arcbase(self,Cx,Cy,degrees=None,x=None,y=None,z=0,rotation=1):
##
##        # angle from center to current relative to x-axis
##        A1 = math2.xangle(Cx,Cy,self.currentx,self.currenty)
##
##        # angle from center to target end point
##        # offset so that it is measured from x-axis
##        if degrees != None:
##            A2 = math2.max180(degrees)
##        elif (x,y) != (None,None):
##            A2 = math2.max180(math2.xangle(Cx,Cy,self.currentx+x,self.currenty+y)-A1)
##        else:
##            A2 = 0
##
##        # rotation
##        if rotation < 0:
##            A2 *= -1
##
##        # length (radius) from current to center
##        R = math.hypot(Cx-self.currentx,Cy-self.currenty)
##
##        # length of arc
##        L = math.pi*R*degrees/180
##
##        # target end point
##        targetx,targety = math2.polar(A2,R)
##        targetz = z + self.currentz
##        
##        # steps required
##        steps = int(abs(L)/self.linear_precision) + 1 # +1 for better than linear precision
##
##        if steps: # can't be 0
##
##            # change per step
##            changea = degrees/steps # angle
##            changez = z/steps # helix
##
##            for nada in range(steps):
##                A1 += changea
##                self.currentx,self.currenty = math2.polar(A1,R)
##                self.currentx += Cx
##                self.currenty += Cy
##                self.currentz += changez
##                current_rounded_xyz = self.current_rounded()
##                if current_rounded_xyz != self.last_rounded_xyz:
##                    self.last_rounded_xyz = current_rounded_xyz
##                    yield current_rounded_xyz
##
##            # for security and rounding errors
##            self.currentx,self.currenty,self.currentz = targetx,targety,targetz
##            current_rounded_xyz = self.current_rounded()
##            if current_rounded_xyz != self.last_rounded_xyz:
##                print('SECURITy: xyz.arc final call for precision')
##                self.last_rounded_xyz = current_rounded_xyz
##                yield current_rounded_xyz

##        if degrees != None:
##            A2 = math2.max180(A1+degrees)
##        elif (x,y) != (None,None):
##            A2 = math2.xangle(Cx,Cy,self.currentx+x,self.currenty+y)
##        else:
##            A2 = A1

##        # target end point
##        targetx,targety = math2.polar(A2,R)
##        targetx += Cx
##        targety += Cy
##        targetz = z + self.currentz        
##
##        # length of arc
##        L = math.pi*R*degrees/180
##
##        # steps required
##        steps = int(abs(L)/self.linear_precision) + 1 # +1 for better than linear precision
##
##        print('BASE:',A1,A2,degrees,R,steps,rotation)
##
##        if steps: # can't be 0
##
##            # change per step
##            changea = degrees/steps # angle
##            changez = z/steps # helix
##
##            for nada in range(steps):
##                A1 += changea
##                self.currentx,self.currenty = math2.polar(A1,R)
##                self.currentx += Cx
##                self.currenty += Cy
##                self.currentz += changez
##                current_rounded_xyz = self.current_rounded()
##                if current_rounded_xyz != self.last_rounded_xyz:
##                    self.last_rounded_xyz = current_rounded_xyz
##                    yield current_rounded_xyz
##
##            # for security and rounding errors
##            self.currentx,self.currenty,self.currentz = targetx,targety,targetz
##            current_rounded_xyz = self.current_rounded()
##            if current_rounded_xyz != self.last_rounded_xyz:
##                print('SECURITy: xyz.arc final call for precision')
##                self.last_rounded_xyz = current_rounded_xyz
##                yield current_rounded_xyz



    


















































