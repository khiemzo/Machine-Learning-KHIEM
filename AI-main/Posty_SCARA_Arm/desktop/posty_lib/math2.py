import math

round_to_places = 4

def round_to(N):
    return round(N,round_to_places)

def same(N1,N2):
    return round(N1,round_to_places) == round(N2,round_to_places)

def distance(P1,P2):

    # for 2D use math.hypot

    # 2D or 3D or XD distance between two points

    if len(P1) == 2:
        return math.hypot(P1[0]-P2[0],P1[1]-P2[1])

    return math.sqrt(sum(((x[0]-x[1])**2 for x in zip(P1,P2))))

def xangle(X1,Y1,X2,Y2):

    # 2D angle in DEGREES from positive X axis of origin
    
    return math.degrees(math.atan2(Y2-Y1,X2-X1))

def max180(degrees):

    degrees = degrees%360

    if degrees > 180:
        degrees -= 360

    return degrees

def polar(degrees,distance):

    # 2D (x,y) deviation from origin based on an angle and distance
    # distance must be positive
    # degrees max +-180
    
    distance = abs(distance)
    radians = math.radians(max180(degrees))

    return (math.cos(radians)*distance,math.sin(radians)*distance)

def arclen(degrees,radius):

    return math.pi*radius*degrees/180.0

def circle_intersects(X1,Y1,R1,X2,Y2,R2):

    # 2D intersection points of two circles

    # for circles 1 and 2
    # X,Y = center of circle
    # R   = radius of circle

    # find the two possible intersect points
    # these are the where the two circles intersect

    # first, assume the centers are on the x axis
    # find the x-intercept value X for the line between the intersect points
    # then find the positive intersect point y value Y (and the negative -Y)
    # then rotate points around the origin to correct location

    # set center circle 1 as origin, only work with X,Y of circle 2 shifted 
    X = X2-X1
    Y = Y2-Y1

    # get the angle in radians from the x axis
    A = math.atan2(Y,X)

    # get distance between the two centers
    D = round_to(math.hypot(X,Y))

    # get the maximun allowed distance between centers
    # this would be when the circles touch at only one point
    R = round_to(R1+R2)

    # value errors
    if (not D):
        raise ValueError('Same point error.')
    if D > R:
        #raise ValueError('Non-overlapping circles.')
        print('ERROR: Non-overlapping circles. Off by {}.'.format(D-R))
        while D > R:
            R1 /= 0.9999
            R2 /= 0.9999
            R = R1 + R2

    # -----

    # assume the line between centers lies on the x axis
    # i.e. theoretically rotate the line by -A

    # at max distance
    # single point at r1
    if same(R,D):
        x = R1
        y = 0

    # less than max
    # using the formula for a circle
    # r1**2 =     x**2 + y**2 for circle 1
    # r2**2 = (x-D)**2 + y**2 for circle 2
    # solve the top for y**2, substitute, solve for x
    # X = (D**2 + r1**2 - r2**2)/(2*D)
    # by substituting X into formula for circle 1
    # Y = math.sqrt( r1**2 - X**2 ) 
    else:
        x = (D**2 + R1**2 - R2**2) / (2*D)
        y = math.sqrt(R1**2 - x**2)

    # -----

    # rotate both points into position from x-axis
    x1,y1 = rotate_on_origin(x, y,A,radians=True)
    x2,y2 = rotate_on_origin(x,-y,A,radians=True)

    # shift both points back by X1,Y1
    # and return
    return (x1+X1,y1+Y1),(x2+X1,y2+Y1)

def rotate_on_point(PX,PY,X,Y,angle,R=None,radians=True):
    x = X-PX
    y = Y-PY
    x,y = rotate_on_origin(x,y,angle,R,radians)
    return x+PX,y+PY

def rotate_on_origin(X,Y,angle,R=None,radians=True):

    # 2D rotate point around origin
    # referenced to the positive x axis

    # radius/distance origin to current
    R = math.hypot(X,Y)

    # angle from x axis to origin-to-XY line
    A = math.atan2(Y,X)

    # rotation angle
    if not radians:
        angle = math.radians(angle)

    # new angle
    A2 = A + angle

    # new coordinates
    X = R*math.cos(A2)
    Y = R*math.sin(A2)

    return (X,Y)

# additional formulae not yet incorporated

##    def math_center(p1,p2,radius,rotation=None,falsecenter=None):
##
##        # get center from point1, point2, radius, and (rotation or the falsecenter)
##
##        # reference: http://mathforum.org/library/drmath/view/53027.html
##        # reference: http://rosettacode.org/wiki/Circles_of_given_radius_through_two_points
##
##        # set initial variables
##        (x1,y1),(x2,y2),r = p1,p2,radius
##        dx,dy = x2-x1,y2-y1 # distance and direction between coordinates
##        d1 = math_distance(p1,p2) # distance between points
##
##        # error conditions
##        if p1 == p2:
##            raise ValueError('Cannot determine center from radius and coincident points.')
##        elif r <= 0.0:
##            raise ValueError('The radius must be greater than zero.')
##        elif d1 > 2*r:
##            if math_round(d1) >= math_round(2*r):
##                r = d1/2
##            else:
##                raise ValueError('The radius is less than half the distance between points.')
##
##        # midpoint between points
##        x3,y3 = (x1+x2)/2,(y1+y2)/2
##        if d1 == 2*r:
##            return x3,y3
##
##        # right triangle made from point, midpoint, and center
##        # distance from midpoint to center given radius and point-midpoint
##        d2 = math.sqrt(r**2-(d1/2)**2)
##
##        # scale values for midpoint-center line
##        # based on slope of point-point line (perpendicular to)
##        # scaled to 1 by dividing by point-point distance
##        # they are inverted, so use x for y and y for x
##        sx,sy = dy/d1,dx/d1
##
##        # centers
##        center1 = (x3+d2*sx,y3-d2*sy)
##        center2 = (x3-d2*sx,y3+d2*sy)
##
##        # select using false center
##        if falsecenter:
##            if math_distance(falsecenter,center1) <= math_distance(falsecenter,center2):
##                return center1
##            else:
##                return center2
##
##        # select using rotation
##        if rotation == -1:
##            return center1
##        else:
##            return center2

##    def math_arcdata(current,target=None,angle=None,center=None,radius=None,rotation=1):
##
##        #print('math_arcdata:',[current,target,angle,center,radius,rotation])
##
##        # this is 2D based on the corresponding (x,y) of the current/target/center points passed in
##        # any necessary conversions must be done prior to arriving here
##        
##        # return = endpoint,center,radius,start_angle,end_angle,rotation_angle,rotation
##        # these are the true values (the ones to be used)
##        # the rotation angle is signed according to rotation
##
##        # a current point (start point) is always required
##
##        # when given, the angle (rotation angle) takes precedence
##        # the angle should be positive (control direction using rotation)
##        # the target point (end point) will be overwritten by a calculated value
##        # the angle option requires a center point be given
##
##        # otherwise, the target point has precedence (will end up there) and must be given
##        # a correct center has precedence over a radius
##        # a radius has precedence over a calculated center
##
##        # fix rotation
##        if type(rotation) == str:
##            rotation = rotation.strip().lower()
##            if rotation.startswith('-') or rotation[:2] in ('cw','cl'):
##                rotation = -1
##            else:
##                rotation = 1
##        elif type(rotation) in (int,float) and rotation < 0:
##            rotation = -1
##        else:
##            rotation = 1
##
##        # rotation angle option
##        if angle != None:
##
##            # not valid conditions
##            if (None in current) or \
##               ((not center) or (None in center)) or \
##               (type(angle) not in (int,float)) or \
##               (math_same(current[0],center[0]) and math_same(current[1],center[1])):
##                print('ARC Error:',[current,target,angle,center,radius,rotation])
##                raise ValueError('Insufficient data to use angle.')
##
##            # center is accepted
##            # set radius
##            radius = math_distance(current,center)
##
##            # set rotation angle
##            rangle = abs(angle)
##            if rangle > 360:
##                rangle = rangle%360
##            rangle *= rotation
##
##            # set start angle
##            sangle = math_xangle(center,current)
##
##            # set end angle
##            if math_same(abs(rangle),360):
##                rangle = 360 * rotation
##                eangle = sangle
##            else:
##                eangle = sangle + rangle # rangle is signed
##                if eangle > 180:
##                    eangle -= 360
##                elif eangle < -180:
##                    eangle += 360
##
##            # set end point
##            xoffset,yoffset = math_polar(eangle,radius) # offset from center
##            endpoint = (center[0]+xoffset,center[1]+yoffset)
##
##            # end of angle option
##
##        # normal option
##        else:
##
##            # not valid
##            if (None in current) or \
##               ((not target) or (None in target)) or \
##               (((not center) or (None in center)) and (not radius)):
##                print('ARC Error:',[current,target,angle,center,radius,rotation])
##                raise ValueError('Insufficient data to determine center.')
##
##            # a center is given
##            if center:
##                r1 = math_distance(current,center)
##                r2 = math_distance(target,center)
##                radius = (r1+r2)/2 # reset radius
##                if not math_same(r1,r2):
##                    center = math_center(current,target,radius,falsecenter=center)
##
##            # a radius is given
##            elif radius:
##                # assume half the distance between points minimum
##                radius = max(abs(radius),math_distance(current,target)/2)
##                center = math_center(current,target,radius,rotation=rotation)
##
##            # this shouldn't happen with above catch 
##            else:
##                print('ARC Error:',[current,target,angle,center,radius,rotation])
##                raise ValueError('Insufficient data to determine center (unknown catch).')
##
##            # set start,end angles
##            sangle = math_xangle(center,current)
##            eangle = math_xangle(center,target)
##
##            # end in same place (full rotation)
##            if math_same(eangle,sangle):
##                eangle = sangle
##                rangle = 360 * rotation
##
##            # partial rotation
##            else:
##                rangle = abs(eangle-sangle)
##                if rotation == 1 and eangle < sangle:
##                    rangle = 360 - rangle
##                elif rotation == -1 and eangle > sangle:
##                    rangle = 360 - rangle
##                rangle *= rotation
##
##            # set end point
##            endpoint = target
##
##            # end of normal option
##
##        #print('math_arcdata:',[endpoint,center,radius,sangle,eangle,rangle,rotation])
##        
##        # done
##        return endpoint,center,radius,sangle,eangle,rangle,rotation

       
