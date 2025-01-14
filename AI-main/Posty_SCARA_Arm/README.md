# Posty

Posty is one of my favorite projects. I keep meaning to get back to developing, drawing, and making videos with Posty, but I have been so busy with work over the last year or two that I haven't been able to do much that I intended.

Very simply put, Posty is a 3-axis scara bot. There are 2 axes that move the arms, and one small stepper motor that turns a cam that raises and lowers the pen (held down by gravity). The axes are run by steppers (3x) which are controlled by 3 A4988 modules, which are in turn controlled by an ESP32 running MicroPython.

The ESP32 is connected to the local WiFi network and runs as a server. Any device can connect to the server, open a socket, and start passing single-byte commands to Posty. Each byte has a special coding that tells which motor to move, which direction, and how many steps (up to 15). That's all Posty does. It is really a "dumb" robot in that it doesn't even know where it's arms are. It just assumes that the motors will not slip or skip steps. I plan on adding angle sensors at some point, but for now it has no sensors (it doesn't even have proximity switches).

All the real work is done by my desktop. I have a stack of software that I have written to use Posty. It's all written in Python3.

At the bottom of the stack is the communication software that connects to Posty, keeps the socket open, and send command bytes.

The next layer is the "XYZ" library. This converts any XYZ coordinates input into angles of the arms and steps for the motors. This is the "kinematics" layer. It also has functions that can move between coordinates in a smooth manner (i.e. approximating lines/curves with many alternating steps).

That is the core stack. On top of xyz I have other libraries that do fancier things. For example, one that writes using a custom font, and one that can interpret basic g-code.

The font library currently only has one font. It is a series of arcs and straight lines that can be scaled to any size. I did this because it is fast and efficient, but it certainly isn't fancy. Fancy fonts can be done with g-code.

The g-code library handles basic g-code. In the old days there were many, many g-codes, but nowadays most rendering software converts vector graphics into a series of xyz coordinates and only uses a few g-codes. All the curves are already handled and converted into many line segments (although my software may make them smoother).

The easiest thing to do is use the font I created to write stuff. It's a lot harder to go through the process of getting a good image, converting it to black and white, then lines, then converting it to SVG, converting it to g-gode, and making it print. I've only done it a dozen times or so. There are two longer videos on my channel where I use Posty to do some drawing, and I have made postcards for some of my friends and family. I have been using some online tools for SVG and g-code conversions.

My Posty code is in this private repository. It is complex, and has not been cleaned up like most of the stuff I have in the public repository. It is being used only by me and a friend of mine in Turkey that is also making a scara bot. We have started cleaning it up, but we haven't had time to finish it.

That being said, I don't mind sharing it with select people. Please connect with me in LinkedIn (so that I know with whom I'm sharing) and send me your GitLab ID.

I hope this helps,

Clayton
