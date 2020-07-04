from easing_functions import *
from drawBot import *

# EDIT THESE VALUES #####################

string="string"
fontUwant="Your variable font"
textsize=300

fps=60
speed=60 # speed/fps=duration of one loop in seconds

framewidth=1080
frameheight=1080

layers=5

loops=2

#########################################

axis1=list(listFontVariations(fontUwant).items())[0][0]
axis1min=list(listFontVariations(fontUwant).items())[0][1]["minValue"]
axis1max=list(listFontVariations(fontUwant).items())[0][1]["maxValue"]
axis1range=axis1max-axis1min
textPosX=framewidth/2
textPosY=frameheight/2-textsize/4
    
def draw(loopframe, astart):
    
    # draw background
    newPage(framewidth, frameheight)
    frameDuration(1/fps)
    cmykFill(.01, .02, 0, .95) 
    rect(0, 0, framewidth, frameheight)
    
    # set main text properties
    blendMode("overlay")
    cmykFill(.2, .1, 0, 0)
    font(fontUwant)
    fontSize(textsize)
    
    # for the specified number of layers, calculate the respective values
    for l in range(layers):
        a = QuinticEaseInOut(start=astart, end=axis1max-l*((axis1max-axis1min)/(layers-1)), duration=speed)
        args1 = {axis1 : a.ease(loopframe)}
        fontVariations(**args1)
        text(string, (textPosX, textPosY), align="center")

# create a static repetitition of draw()
def pause(length, currstart):
    for z in range(length):
        draw(a1, currstart)

# for the specified number of loops, cycle through the number of frames defined in speed and insert them into draw()
for k in range(loops):
    
    # second argument defines the start of the loop haöf, I'm sure there's a far more efficient way to write this
    for a1 in range(speed):
        draw(a1, axis1min)
    for a1 in reversed(range(speed)):
        draw(a1, axis1max)
    pause(10, axis1max)
    for a1 in range(speed):
        draw(a1, axis1max)
    for a1 in reversed(range(speed)):
        draw(a1, axis1min)
    pause(10, axis1min)
    
saveImage("~/Desktop/" + string + " " + str(layers) + " layers.mp4")
