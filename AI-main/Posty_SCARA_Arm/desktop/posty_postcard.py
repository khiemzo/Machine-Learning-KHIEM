import os,sys,time

import posty_desktop_a4988 as postyapp

#-----------------------------------------
# instantiate posty
#-----------------------------------------

posty = postyapp.POSTY()
posty.hold_do = False

posty.paper_origin = (0, 0)
posty.paper_end    = (5.5,-3.5)

#-----------------------------------------
# index device 
#-----------------------------------------

posty.index()

#-----------------------------------------
# open socket
#-----------------------------------------

print('OPENING SOCKET',end=' ')
posty.connect()
posty.flush(show=False)

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

posty.manual_index(False)

#-----------------------------------------
# turn on 
#-----------------------------------------

posty.on()
#posty.off();input('RE-INDEX')
posty.emoh()

#-----------------------------------------
# postcard 
#-----------------------------------------

try:

##    #-----------------------------------------
##    # return address 
##    #-----------------------------------------
##
    return_address = 'Posty Robot\n793 Coile Rd\nComer GA 30629'
    posty.write(return_address,x=0.1,y=-0.1,height=3/16,maxwidth=5.5,csep=1.6,lsep=4,align='l',valign='t',rotate=0)

    #-----------------------------------------
    # address 
    #-----------------------------------------

##    #       | 18 is tne max   |        
##    #line1 = 'The Fish Locker'
##    line1 = 'Lawson Lindsey'
##    line2 = ''
##    line3 = ''
##    line4 = ''
##    line5 = ''
##
##    address = '\n'.join([x.strip() for x in (line1,line2,line3,line4,line5)])# if x.strip()])
##    address = address.strip()
##    posty.write(address,x=2.5,y=-1.6875,height=3/16,maxwidth=5.5,csep=1.6,lsep=4,align='l',valign='t',rotate=0)

    #-----------------------------------------
    # image 
    #-----------------------------------------

##    # picture
##    posty.up()
##    posty.moveto(2.75,-0.02)
##    posty.gcode(
##        #'project_fish_locker/the_fish_locker_3b_thresh_v3.gcode',
##        #'project_lawson/image1c.gcode',
##        'project_fish_locker/the_fish_locker_4.1169.212.020.4.gcode',
##        height=1.75,
##        width=0,
##        align='c',
##        valign='t',
##        origin_bottom_left=False,
##        use_start_code=True,
##        rotate=0
##        )
##    posty.up()

##    # picture
##    posty.up()
##    posty.moveto(2.75,-3.48)
##    posty.gcode(
##        #'project_fish_locker/the_fish_locker_3b_thresh_v3.gcode',
##        #'project_lawson/image1c.gcode',
##        'project_fish_locker/seabass2.528.96.020.7.gcode',
##        height=2.125,
##        width=0,
##        align='c',
##        valign='b',
##        origin_bottom_left=False,
##        use_start_code=True,
##        rotate=0
##        )
##    posty.up()

    #-----------------------------------------
    # text 
    #-----------------------------------------

#-----------------------------------------
# end test
#-----------------------------------------

except KeyboardInterrupt:
    pass  

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
posty.sendEOD()
posty.waitEOD(show=True)
posty.disconnect()
print('ALL DONE!')

#-----------------------------------------
# end
#-----------------------------------------
