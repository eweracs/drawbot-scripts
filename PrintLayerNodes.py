from GlyphsApp import *
import os

current_font = Glyphs.font

width = 1000
height = 1000
handleSize = 5
size = 170

def drawOnNode(node, handleSize):
    if handleSize == 0:
        return 
    pt = node.position
    size = handleSize
    fill(1, 1, 1)
    if node.type == GSCURVE or node.type == GSLINE:
        if node.smooth:
            oval(pt.x - (size / 2), pt.y - (size / 2), size, size)
        else:
            rect(pt.x - (size / 2), pt.y - (size / 2), size, size)

def drawOffNode(node, handleSize):
    if handleSize == 0:
        return 
    pt = node.position
    size = handleSize
    fill(0.2, 0.2, 0.2)
    if node.type != GSCURVE and node.type != GSLINE:
        index = node.parent.indexOfNode_(node)
        prevNode = node.parent.nodes[index - 1]
        nextNode = node.parent.nodes[index + 1]
        if prevNode.type == GSOFFCURVE:
            newPath()
            moveTo(node.position)
            lineTo(nextNode.position)
            drawPath()
        else:
            newPath()
            moveTo(node.position)
            lineTo(prevNode.position)
            drawPath()            
        oval(pt.x - (size / 2), pt.y - (size / 2), size, size)
    
def drawLayer(master, layer):
    offsetX = (width - layer.width) / 2
    offsetY = abs(master.ascender - master.descender) / 4
    translate(offsetX, offsetY)
    strokeWidth(0.5)
    stroke(0.2, 0.2, 0.2)
    save()
    for p in layer.paths:
        for n in p.nodes:
            drawOffNode(n, handleSize)
        for n in p.nodes:
            drawOnNode(n, handleSize)
    fill(0, 0, 0, 0)
    stroke(1, 1, 1)
    drawPath(layer.bezierPath)

def draw():
    newPage(width, height)
    fill(0, 0, 0)
    rect(0, 0, width, height)
    
for glyph in current_font.glyphs:
    if not glyph.export:
        continue
    layer = glyph.layers[0]
    proxy_layer = layer.copyDecomposedLayer()
    proxy_layer.removeOverlap()
    draw()
    drawLayer(layer.master, proxy_layer)
    saveImage("~/Desktop/%s.svg" % glyph.name)
    