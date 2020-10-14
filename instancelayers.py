from drawBot import *

# EDIT THESE VALUES #####################

string="a"
fontUwant="Your Variable Font"
textsize=3000

framewidth=1920
frameheight=1920

#########################################

axis1=list(listFontVariations(fontUwant).items())[0][0]
textPosX=framewidth/2
textPosY=frameheight/2-textsize/3+240

layers = len(listNamedInstances(fontUwant))
    
# draw background
newPage(framewidth, frameheight)
cmykFill(.0, .0, 0, 1) 
rect(0, 0, framewidth, frameheight)

# set main text properties
blendMode("overlay")
cmykFill(.0, .25, .07, 0)
font(fontUwant)
fontSize(textsize)

for l in range(layers):
    args1 = {axis1:list(listNamedInstances(fontUwant).items())[l][1][axis1]}
    fontVariations(**args1)
    text(string, (textPosX, textPosY), align="center")
      
saveImage("~/Desktop/" + string + " " + str(layers) + " instances.png")
