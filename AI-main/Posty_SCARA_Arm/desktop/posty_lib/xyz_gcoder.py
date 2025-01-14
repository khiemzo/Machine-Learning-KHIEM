
import re

class XYZGcoder:

    def __init__(self,xyz):

        # set coordinates object
        self.xyz = xyz

        # gcode values on a single line
        self.gcomment = re.compile(r'\([^\)]*\)|;.*')
        self.gstart = re.compile('%|\x0B')
        self.gword = re.compile(r'\b([a-z])\s*(-?\s*(?:[0-9]\s*)*[0-9](?:\.\s*(?:[0-9]\s*)*[0-9])?)',flags=re.I)

    # ------------------------------------------
    # Functions
    # ------------------------------------------

    # up-down absolute locations    
    upis = 1
    downis = 1
    setspeed = True

    # up
    def up(self):
        yield from self.xyz.moveto(z=self.upis)
        if self.setspeed:
            self.setnormalspeed()
        print('G UP')

    # down
    def down(self):
        yield from self.xyz.moveto(z=self.downis)
        if self.setspeed:
            self.setdrawspeed()
        print('G DOWN')

    # this must be re-defined by the user
    # called after up()
    def setnormalspeed(self):
        pass

    # this must be re-defined by the user
    # called after down()
    def setdrawspeed(self):
        pass

    # known codes
    gcodes = 'G0 G1 G20 G21 G90 G91 M2  '.split()

    # run a file
    def run_file(self,file,width=None,height=None,align=None,valign=None,origin_bottom_left=True,use_start_code=True,rotate=0):

        # current position
        xroot,yroot,zroot = self.xyz.getxyz()

        # first read
        ended = False
        with open(file) as f:
            linecount = 0
            startcount = 0
            xmin,ymin,zmin = 1000000,1000000,1000000
            xmax,ymax,zmax = 0,0,0
            codes = set()
            for line in f:
                line = line.strip().upper()
                if line:
                    linecount += 1
                    line = self.gcomment.sub(' ',line)
                    if self.gstart.search(line):
                        if startcount:
                            ended = True
                            startcount += 1
                            break
                        else:
                            startcount += 1
                    line = self.gstart.sub(' ',line)
                    for alpha,numeric in self.gword.findall(line):
                        if '.' in numeric:
                            number = float(numeric)
                        else:
                            number = int(numeric)
                        code = f'{alpha}{number}'
                        if alpha == 'X':
                            xmin = min(xmin,number)
                            xmax = max(xmax,number)
                        elif alpha == 'Y':
                            ymin = min(ymin,number)
                            ymax = max(ymax,number)
                        elif alpha == 'Z':
                            zmin = min(zmin,number)
                            zmax = max(zmax,number)
                        elif alpha == 'F':
                            pass
                        elif code == 'M2':
                            ended = True
                            startcount += 1
                            codes.add(code)
                            break
                        elif code in self.gcodes:
                            codes.add(code)
                        else:
                            print('ERROR:',code)
                if ended:
                    break
            f.close()

        # invert y values
        yshift = 0
        if not origin_bottom_left:
            ymax,ymin = ymin*-1,ymax*-1
            yshift = ymax

        # spans (dimensions of drawing)
        xspan = xmax-xmin
        yspan = ymax-ymin
        zspan = zmax-zmin

        # scaling
        xscale = None
        yscale = None
        if width and width > 0:
            xscale = width/xspan
        if height and height > 0:
            yscale = height/yspan
        if not xscale:
            if yscale:
                xscale = yscale
            else:
                xscale = 1
        if not yscale:
            yscale = xscale
        zscale = (xscale+yscale)/2

        # adjust alignment (x axis)
        # 'c' = start point is center of image
        # 'r' = start point is right side of image
        # 'l' = start point is left side of image <-- DEFAULT
        if align == 'c':
            xroot2 = xroot - xscale*(xspan/2)
        elif align == 'r':
            xroot2 = xroot - xscale*xspan
        else:
            xroot2 = xroot

        # adjust vertical alignment (y axis)
        # 'm' = start point is middle of image
        # 't' = start point is top edge of image
        # 'b' = start point is bottom edge of image <-- DEFAULT
        if valign == 'm':
            yroot2 = yroot - yscale*(yspan/2)
        elif valign == 't':
            yroot2 = yroot - yscale*yspan 
        else:
            yroot2 = yroot

        # adjust alignments so that minimum xy values will be at edge
        xroot2 -= xscale*xmin
        yroot2 -= yscale*ymin

##        # show values
##        print()
##        print('LINES: ',linecount)
##        print('START/ENDS:',startcount)
##
##        print()
##        print('X RANGE:',[xmin,xmax,xspan])
##        print('Y RANGE:',[ymin,ymax,yspan],'OBL:',origin_bottom_left)
##        print('Z RANGE:',[zmin,zmax,zspan])
##
##        print()
##        print('X SCALE:',xscale)
##        print('Y SCALE:',zscale)
##        print('Z SCALE:',zscale)
##
##        print()
##        print('X ROOT:',[xroot,xroot2])
##        print('Y ROOT:',[yroot,yroot2])

        # second read
        started = False
        if startcount < 2:
            started = True
        ended = False
        # open file
        with open(file) as f:
            # loop 1
            for line in f:
                line = line.strip().upper()
                if line:
                    if self.gstart.search(line):
                        if started:
                            ended = True
                            break
                        else:
                            started = True
                    if not started:
                        continue
                    line = self.gstart.sub(' ',line)
                    x,y,z = None,None,None
                    # loop 2
                    for alpha,numeric in self.gword.findall(line):
                        if '.' in numeric:
                            number = float(numeric)
                        else:
                            number = int(numeric)
                        code = f'{alpha}{number}'

                        if code == 'M2':
                            ended = True
                            break # loop 2

                        elif alpha == 'F':
                            pass 

                        elif code in self.gcodes:
                            continue

                        elif alpha == 'X':
                            x = number
                        elif alpha == 'Y':
                            y = number + yshift
                        elif alpha == 'Z':
                            z = number

                    # code ended
                    if ended:
                        break # loop 1

                    # any z is an up/down
                    if z != None:
                        if z < 0:
                            yield from self.down()
                        else:
                            yield from self.up()

                    # yield movement
                    elif x != None or y != None:

                        # fill in values
                        if x == None:
                            x = self.xyz.currentx
                        if y == None:
                            y = self.xyz.currenty

                        # scale
                        x = xroot2 + x*xscale
                        y = yroot2 + y*yscale

                        # rotate point around root
                        # do this before sending to xyz
                        # so that it won't be trimmed on the wrong axis 
                        if rotate:
                            x,y = self.xyz.math2.rotate_on_point(xroot,yroot,x,y,rotate,radians=False)

                        # movement
                        yield from self.xyz.moveto(x,y,z=None)

                # code ended
                if ended:
                    break # loop 1

            # close file
            f.close()




























