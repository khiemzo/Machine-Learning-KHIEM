import math
from . import math2

class LINEAR:

    # This is a translator which converts XYZ on the cartesian coordinate system
    # to absolute step values. The absolute steps are the number of steps from 
    # the origin to position the device at XYZ (as near as possible).

    # how to:
    # translator = LINEAR()
    # translator.variable = value  # this is NECESSARY for all setup variables
    # (steps),(location) = translator.translate(x,y,z)

    # return:
    # (steps),(location) = translator.translate(x,y,z)
    # (steps) = absolute step values (integers) for motors (1,2,3)
    # (location) = actual (x,y,z) coordinates based on steps (won't be exactly x,y,z)
    # use location data to update coordinates in parent function    

    # --- variables ---

    # motor Steps Per Unit Distance (linear)
    spudx = 1
    spudy = 1
    spudz = 1

    # --- init ---

    # --- translate ---

    def translate(self,X=0,Y=0,Z=0):

        xsteps = int(round(X*self.spudx,0))
        ysteps = int(round(Y*self.spudy,0))
        zsteps = int(round(Y*self.spudz,0))

        xtrue = xsteps/self.spudx
        ytrue = ysteps/self.spudy
        ztrue = zsteps/self.spudz

        return (xsteps,ysteps,zsteps),(xtrue,ytrue,ztrue)

class SCARA:

    # This is a translator which converts XYZ on the cartesian coordinate system
    # to absolute step values. The absolute steps are the number of steps from 
    # the origin to position the device at XYZ (as near as possible).

    # how to:
    # translator = SCARA()
    # translator.variable = value  # this is NECESSARY for all setup variables
    # translator.set_zero_angles() # this is REQUIRED
    # (steps),(location) = translator.translate(x,y,z)

    # return:
    # (steps),(location) = translator.translate(x,y,z)
    # (steps) = absolute step values (integers) for motors (1,2,3)
    # (location) = actual (x,y,z) coordinates based on steps (won't be exactly x,y,z)
    # use location data to update coordinates in parent function    

    # --- variables ---

    # motor Steps Per Unit Distance (linear)
    # only applies to Z
    spudz = 1

    # offset from the CO (cartesian origin) to the AO (arm origin)
    # only applies to X and Y
    co2aox = 1
    co2aoy = 1

    # motor Steps Per Angle Degree
    spad1 = 1
    spad2 = 1

    # Arm LENgth in unit distance
    alen1 = 1
    alen2 = 1

    # imagine your own arm
    right_handed = True
    reaching_up = True
    midpoint_index = None

    # angle round precision
    round_precision = 4

    # tracking of A1 in case of 180 crossover
    lastA1 = 0
    check_crossover_at = 135

    # --- init ---

    def __init__(self):
        pass
        
    def round_to(self,N):
        # local function to allow precision changes on the fly
        return round(N,self.round_precision)

    def set_zero_angles(self):

        # set midpoint index (which midpoint to choose)
        if self.right_handed:
            if self.reaching_up:
                self.midpoint_index = 1
            else:
                self.midpoint_index = 0
        else:
            if self.reaching_up:
                self.midpoint_index = 0
            else:
                self.midpoint_index = 1

        # get zero angles
        # see translate() for explanations
        X = -self.co2aox
        Y = -self.co2aoy
        MX,MY = math2.circle_intersects(0,0,self.alen1,X,Y,self.alen2)[self.midpoint_index]
        A1 = math2.xangle(0,0,MX,MY)
        A2 = math2.xangle(MX,MY,X,Y)
        #print('ANGLES ABSOLUTE:',A1,A2,A1-A2)
        A2 = A1-A2
        if A2 > 180:
            A2 = 180 - A2
        elif A2 < -180:
            A2 = 360 - (180 - A2)
        self.zangle1 = self.round_to(A1)
        self.zangle2 = self.round_to(A2)
        #print('ANGLES ZERO:',A1,A2)
        

    # --- translate ---

    def translate(self,X=0,Y=0,Z=0):
        #print('TRANSLATE:',(round(X,3),round(Y,3)))

        # Z is linear
        zsteps = int(round(Z*self.spudz,0))
        ztrue = zsteps/self.spudz

        # apply offsets
        # this makes X,Y relative to the arm origin
        X -= self.co2aox
        Y -= self.co2aoy

        # distance from arm origin to XY
        H = math.hypot(X,Y)

        # fix reach (can't be more than combined arm lenghts)
        # shorten both axes proportionally until it works
        while H > self.alen1 + self.alen2:
            X *= 0.99
            Y *= 0.99
            H = math.hypot(X,Y)

        # get midpoint
        MX,MY = math2.circle_intersects(0,0,self.alen1,X,Y,self.alen2)[self.midpoint_index]

        # get angles in DEGREES
        # arm1 angle is from arm1 origin pivot relative to positive x axis
        # the max angle for arm1 is +-360 degrees (must handle 180 crossover)
        # arm2 angles are from arm2 origin pivot relative to arm1
        # the max angle for arm2 is +-180 degrees
        A1 = math2.xangle(0,0,MX,MY)
        A2 = math2.xangle(MX,MY,X,Y)
        #print('ANGLES ABSOLUTE:',round(A1,3),round(A2,3))

        # handle A1 180 crossover
        # 360 crossover not allowed
        crossover = False
        if abs(self.lastA1) >= self.check_crossover_at:
            if self.lastA1 > 0 and A1 < 0:
                crossover = True
                A1 = 360 + A1
            elif self.lastA1 < 0 and A1 > 0:
                crossover = True
                A1 = 360 - A1
        self.lastA1 = A1

        # make A2 relative to A1
        A2 = A1-A2
        if A2 > 180:
            A2 = 180 - A2
        elif A2 < -180:
            A2 = 360 - (180 - A2)

        #print('    WORKING ANGLES:',round(A1,3),round(A2,3))

        # change angles to offset from zero angles
        # i.e. where they were at (0,0)
        A1 -= self.zangle1
        A2 -= self.zangle2

        # calculate absolute steps to angles
        # this is adjusted to integer steps
        # probably not the target XY
        arm1steps = int(round(A1*self.spad1,0))
        arm2steps = int(round(A2*self.spad2,0))

        # ---- now work backwards to get true location ----

        # calculate true angles based on steps
        A1 = arm1steps/self.spad1
        A2 = arm2steps/self.spad2

        # add the zangles back
        A1 += self.zangle1
        A2 += self.zangle2      
        
        # make A2 NOT relative to A1
        A2 = (A1 + A2) - 180

        # calculate true XY of arm2 end point
        midx,midy = math2.polar(A1,self.alen1)
        endx,endy = math2.polar(A2,self.alen2)
        endx += midx
        endy += midy

        # remove offsets     
        xtrue = endx + self.co2aox
        ytrue = endy + self.co2aoy

        #print('    ANGLES RETURN:',A1,A2,(round(xtrue,3),round(ytrue,3)))

        # done
        return (arm1steps,arm2steps,zsteps),(xtrue,ytrue,ztrue)

class STATES:

    # This tracks the "location" of motors as steps.
    # The primary functions "step" and "stepto" iterators.
    # They yield the states necessary for the motors to make a
    #     coordinated move to the new location.
    # Each yield is a list with 4 state values per defined motor.
    # The state values are 1 or 0, in the order A,a,B,b

    # ----------------------------------------------

    # all motor states
    # {state_id: (byte_states,(mode1_index),(mode2_index),(mode3_index))}
    # pin state order = (A,a,B,b)
    # ascii_states = ascii text representation MSb-->LSb
    # byte_state = byte with lower nibble == pin state
    # modex_index = (backwards_1_step,forwards_1_step)
    # mode1 = single-coil 4 steps
    # mode2 = double-coil 4 steps
    # mode3 = mixed 8 step (half-stepping)
    motor_states = {
        #0:((1,0,0,0),(6,2),(7,1),(7,1)),
        #1:((1,0,1,0),(0,2),(7,3),(0,2)),
        #2:((0,0,1,0),(0,4),(1,3),(1,3)),
        #3:((0,1,1,0),(2,4),(1,5),(2,4)),
        #4:((0,1,0,0),(2,6),(3,5),(3,5)),
        #5:((0,1,0,1),(4,6),(3,7),(4,6)),
        #6:((0,0,0,1),(4,0),(5,7),(5,7)),
        #7:((1,0,0,1),(6,0),(5,1),(6,0)),
        0:( 8,(6,2),(7,1),(7,1)),
        1:(10,(0,2),(7,3),(0,2)),
        2:( 2,(0,4),(1,3),(1,3)),
        3:( 6,(2,4),(1,5),(2,4)),
        4:( 4,(2,6),(3,5),(3,5)),
        5:( 5,(4,6),(3,7),(4,6)),
        6:( 1,(4,0),(5,7),(5,7)),
        7:( 9,(6,0),(5,1),(6,0)),
        }

    # ----------------------------------------------

    # motor data
    motors = []
    last_states = None
    last_steps = None

    def motor_add(self,mode=1,reverse=False,minsteps=0,maxsteps=0,steps=0,index=0):
        #   0    1       2        3        4     5   
        # [mode,reverse,minsteps,maxsteps,steps,index]
        motor = [max(1,min(3,int(mode))),
                 bool(reverse),
                 int(minsteps),
                 int(maxsteps),
                 int(steps),
                 max(0,min(7,int(index)))
                 ]
        self.motors.append(motor)
        self.states()

    def motors_clear(self):
        self.motors = []
        self.last_states = None

    # set all motor step values to 0
    def motors_zero(self):
        for x in range(len(motors)):
            self.motors[x][4] = 0

    # set motor step values to given values
    def motors_steps(self,*step_values):
        for x in range(len(step_values)):
            self.motors[x][4] = step_values[x]

    # get current steps
    def steps(self):
        self.last_steps = [motor[4] for motor in self.motors]
        return self.last_steps

    # get current states
    def states(self):
        self.last_states = [self.motor_states[motor[5]][0] for motor in self.motors]
        return self.last_states

    # ----------------------------------------------

    def stepto(self,*step_values):

        converted = []
        offset = 0

        for x in step_values:
            converted.append(x-self.motors[offset][4])
            offset += 1

        yield from self.step(*converted)

    def step(self,*step_values):

        step_values = list(step_values)
        motor_count = len(step_values)

        while 1:

            # build states
            states = []
            for x in range(motor_count):

                # get values
                step_value = step_values[x]
                mode,reverse,minsteps,maxsteps,steps,index = self.motors[x]

                # no steps
                if step_value == 0:
                    states.append(self.motor_states[index][0])

                # positive steps
                elif step_value > 0:

                    # already at max, use current state
                    if steps + 1 > maxsteps:
                        states.append(self.motor_states[index][0])

                    # continue
                    else:

                        # get new index
                        if reverse:
                            new_index = self.motor_states[index][mode][0]
                        else:
                            new_index = self.motor_states[index][mode][1]

                        # update
                        self.motors[x][4:] = [steps+1,new_index]
                        step_values[x] -= 1

                        # use new state
                        states.append(self.motor_states[new_index][0])

                # negative steps
                else:

                    # already at min, use current state
                    if steps - 1 < minsteps:
                        states.append(self.motor_states[index][0])

                    # continue
                    else:

                        # get new index
                        if reverse:
                            new_index = self.motor_states[index][mode][1]
                        else:
                            new_index = self.motor_states[index][mode][0]

                        # update
                        self.motors[x][4:] = [steps-1,new_index]
                        step_values[x] += 1

                        # use new state
                        states.append(self.motor_states[new_index][0])

            # done
            if states == self.last_states:
                break

            # update last state, yield state
            else:
                self.last_states = states
                yield states

