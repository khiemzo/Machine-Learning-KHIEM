import os,sys,time

import posty_desktop_a4988 as postyapp

#-----------------------------------------
# instantiate posty
#-----------------------------------------

posty = postyapp.POSTY()
posty.hold_do = False

posty.xyz.linear_precision = 0.005


#-----------------------------------------
# index device 
#-----------------------------------------

posty.index()

#-----------------------------------------
# open socket
#-----------------------------------------

##posty.socket.nosend = True

print('OPENING SOCKET',end=' ')
posty.socket.connect()
posty.socket.flush(show=False)

#-----------------------------------------
# set speeds 
#-----------------------------------------

posty.setnormalspeed()

#-----------------------------------------
# flush 
#-----------------------------------------

posty.socket.sendRFD()
posty.socket.flush(show=False)

#-----------------------------------------
# manual index 
#-----------------------------------------

# this cause desktop to reboot
#posty.manual_index(False)

#-----------------------------------------
# turn on 
#-----------------------------------------

posty.on()
posty.emoh()

#-----------------------------------------
# test 
#-----------------------------------------

try:

    # header
    posty.write('hayride',
                x=5.5,y=-2,
                height=3/8,
                maxwidth=4,
                csep=4,lsep=2,
                align='c',valign='b',
                rotate=-90)

    # picture
    posty.up()
    posty.moveto(5.5/2,-2)
    posty.setdrawspeed()
    posty.gcoder.setspeed = False
    posty.gcode(
        'project_kevin/kevin_v1.gcode',
        height=5.3,
        width=0,
        align='c',
        valign='m',
        origin_bottom_left=False,
        use_start_code=True,
        rotate=-90
        )
    posty.setnormalspeed()


##----

##    y = -0.25
##    gap = 0.25+(.25/3)
##    posty.write("posty"   ,1.25,y,height=0.5  ,align='c')
##    y -= gap + 0.5
##    posty.write("the"     ,1.25,y,height=0.25 ,align='c')
##    y -= gap + 0.25
##    posty.write("postcard",0.1 ,y,height=0.375,align='l')
##    y -= gap + 0.375
##    posty.write("writer"  ,1.25,y,height=0.375,align='c')
##
##    posty.up()
##    posty.moveto(4.5,-2)
##
##    posty.gcode(
##        'project_watermark/watermark_index_top_left.gcode',
##        width=0,
##        height=3.75,
##        align='c',
##        valign='m',
##        origin_bottom_left=False,
##        use_start_code=True,
##        rotate=0
##        )


##----

##    posty.moveto(1,-1)
##    posty.sendwait(1)
##
##    posty.testpattern(3,-2,size=3.75,center=True)

##----

##    try:
##        for x in range(10):
##            posty.down()
##            #posty.motor_steps_send(1,1000)
##            posty.sendwait(1)
##            posty.up()
##            #posty.motor_steps_send(1,-1000)
##            posty.sendwait(1)
##    except KeyboardInterrupt:
##        import traeback
##        print(traceback.exe())

##----

#-----------------------------------------
# end test
#-----------------------------------------

except KeyboardInterrupt:
    import traeback
    print(traceback.exe())

#-----------------------------------------
# turn off
#-----------------------------------------

posty.home()
posty.holdsend()
posty.off()

#-----------------------------------------
# opensocket close
#-----------------------------------------

print('CLOSING SOCKET')
posty.socket.sendEOD()
posty.socket.waitEOD(show=True)
posty.socket.disconnect()
print('ALL DONE!')

#-----------------------------------------
# end
#-----------------------------------------

##    posty.moveto(0,0)
##    posty.sendwait(1)
##    
##    posty.moveto(0,-4)
##    posty.sendwait(1)
##    
##    posty.moveto(6,-4)
##    posty.sendwait(1)
##    #print(posty.s1,posty.s2,posty.s3)
##    
##    posty.moveto(6,0)
##    posty.sendwait(1)
##    
##    posty.moveto(0,0)
##    posty.sendwait(1)
    

    #-----------------------------------------
    # test pattern 1
    #-----------------------------------------


    #-----------------------------------------
    # test pattern 2
    #-----------------------------------------

##    posty.moveto(3,-2)
##
##    for x in range(10):
##        posty.down()
##        posty.sendwait(1)
##        posty.up()
##        posty.sendwait(1)
##
##    posty.testpattern(0.5,-0.5,size=0.75,center=True)
##    posty.testpattern(0.5,-3.5,size=0.75,center=True)
##
##    posty.testpattern(5.5,-3.5,size=0.75,center=True)
##    posty.testpattern(5.5,-0.5,size=0.75,center=True)
##
##    posty.testpattern(3,-2,size=3,center=True)
##
##    posty.write('test',x=3,y=-1,height=0.45,maxwidth=6,csep=1.6,lsep=4,align='c',valign='m',rotate=0)
##    posty.write('1234',x=3,y=-1.4,height=0.25,maxwidth=6,csep=1.6,lsep=4,align='c',valign='m',rotate=0)
##
##    posty.write('test',x=3,y=-3,height=0.45,maxwidth=6,csep=1.6,lsep=4,align='c',valign='m',rotate=180)
##    posty.write('1234',x=3,y=-2.6,height=0.25,maxwidth=6,csep=1.6,lsep=4,align='c',valign='m',rotate=180)
##
##    posty.write('test',x=0.5,y=-2,height=0.5,maxwidth=6,csep=1.6,lsep=4,align='c',valign='m',rotate=90)
##    posty.write('1234',x=1.2,y=-2,height=0.25,maxwidth=6,csep=1.6,lsep=4,align='c',valign='m',rotate=90)
##
##    posty.write('test',x=5.5,y=-2,height=0.5,maxwidth=6,csep=1.6,lsep=4,align='c',valign='m',rotate=-90)
##    posty.write('1234',x=4.8,y=-2,height=0.25,maxwidth=6,csep=1.6,lsep=4,align='c',valign='m',rotate=-90)
##
##    posty.moveto(3,-3)
##    posty.moveto(3,-1)

    #-----------------------------------------
    # fish
    #-----------------------------------------

##    # picture
##    posty.up()
##    posty.moveto(3,-2)
##    posty.gcode(
##        'project_jack_crevalle/crevallejack_96_010_10.gcode',
##        height=0,
##        width=5.9,
##        align='c',
##        valign='m',
##        origin_bottom_left=False,
##        use_start_code=True,
##        rotate=0
##        )
##    posty.up()
    
    #-----------------------------------------
    # original posty
    #-----------------------------------------

##    y = -0.25
##    gap = 0.25+(.25/3)
##    posty.write("posty"   ,1.25,y,height=0.5  ,align='c')
##    y -= gap + 0.5
##    posty.write("the"     ,1.25,y,height=0.25 ,align='c')
##    y -= gap + 0.25
##    posty.write("postcard",0.1 ,y,height=0.375,align='l')
##    y -= gap + 0.375
##    posty.write("writer"  ,1.25,y,height=0.375,align='c')
##
##    posty.up()
##    posty.moveto(3.75,-1.5)
##
##    posty.gcode(
##        'watermark_index_top_left.gcode',
##        width=0,
##        height=2.9,
##        align='c',
##        valign='m',
##        origin_bottom_left=False,
##        use_start_code=True,
##        rotate=0
##        )

    #-----------------------------------------
    # hayride 3x5
    #-----------------------------------------

##    # header
##    posty.write('hayride',
##                x=4.75,y=-1.5,
##                height=3/16,
##                maxwidth=3,
##                csep=4,lsep=2,
##                align='c',valign='b',
##                rotate=-90)
##
##    # picture
##    posty.up()
##    posty.moveto((4.75-0.0625)/2,-1.5)
##    posty.gcode(
##        'kevin_v1.gcode',
##        height=0,
##        width=2.9,
##        align='c',
##        valign='m',
##        origin_bottom_left=False,
##        use_start_code=True,
##        rotate=-90
##        )
##    posty.up()

    #-----------------------------------------
    # crafsman 3x5
    #-----------------------------------------

##    # picture
##    posty.up()
##    posty.moveto(5.45,-3.45)
##    posty.gcode(
##        'crafsman35x55_v2_(ready3).gcode',
##        height=3.4,
##        width=0,
##        align='r',
##        valign='b',
##        origin_bottom_left=False,
##        use_start_code=True,
##        rotate=0
##        )
##    posty.up()
