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

    #-----------------------------------------
    # image 
    #-----------------------------------------

    posty.up()
    posty.moveto(2.75,-0.02)
    posty.gcode(
        'project_watermark/watermark_index_top_left.gcode',
        height=1.75,
        width=0,
        align='c',
        valign='t',
        origin_bottom_left=False,
        use_start_code=True,
        rotate=0
        )
    posty.up()   

    #-----------------------------------------
    # text 
    #-----------------------------------------

    posty.write('ClaytonDarwin',x=0.1,y=-0.1,height=1/2,maxwidth=5.5,csep=1.6,lsep=4,align='c',valign='t',rotate=0)
    posty.write('on YouTube',x=0.1,y=-0.1,height=1/2,maxwidth=5.5,csep=1.6,lsep=4,align='c',valign='t',rotate=0)

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
