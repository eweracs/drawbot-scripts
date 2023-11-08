from GlyphsApp import *
import os
from easing_functions import *

current_font = Glyphs.font

width = 1000
height = 1000
handleSize = 8
size = 170
fps = 30
duration = 2

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
    
def drawLayer(master, layer, remove_overlap=True):
    offsetX = (width - layer.width) / 2
    offsetY = abs(master.ascender - master.descender) / 4
    translate(offsetX, offsetY)
    strokeWidth(0.5)
    stroke(0.2, 0.2, 0.2)
    save()
    layer = layer.copyDecomposedLayer()
    if remove_overlap:
        layer.removeOverlap()
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
    frameDuration(1 / fps)
    fill(0, 0, 0)
    rect(0, 0, width, height)

def first_layer_for_each_glyph():
    for glyph in current_font.glyphs:
        if not glyph.export:
            continue
        layer = glyph.layers[1]
        proxy_layer = layer.copyDecomposedLayer()
        proxy_layer.removeOverlap()
        draw()
        drawLayer(layer.master, proxy_layer)
        saveImage("~/Desktop/%s.svg" % glyph.name)
        
def return_layers_for_interpolations(glyph, axis_ranges, steps=100):
    
    interpolated_layers = {glyph.layers[0].master.id: []}
    layer = GSLayer()
    proxy_glyph = glyph.copy()
    proxy_glyph.name = glyph.name + ".proxy"
    current_font.glyphs.append(proxy_glyph)
    proxy_glyph.layers.append(layer)
    layer.attributes["coordinates"] = {}
    for step in range(steps):
        
        axis_locations = [CubicEaseInOut(axis_ranges[index][0], axis_ranges[index][1], steps - 1).ease(step) for index, axis in enumerate(axis_ranges)]
        layer.attributes["coordinates"] = {axis.axisId: axis_locations[index] for index, axis in enumerate(current_font.axes)}
        layer.reinterpolate()
        layer.decomposeComponents()
        layer.removeOverlap()
        interpolated_layers[glyph.layers[0].master.id].append(layer.copy())
    del current_font.glyphs[proxy_glyph.name]
    
    return(interpolated_layers)
        
def animate_through_coordinates():
    interpolated_layers = return_layers_for_interpolations(current_font.glyphs["a"], get_axis_ranges(), duration * fps)

    for master_id in interpolated_layers:
        for layer in interpolated_layers[master_id]:
            draw()
            drawLayer(current_font.fontMasterForId_(master_id), layer)
        
    saveImage("~/Desktop/test.gif")
    
def svg_for_masters(glyph):
    for master in current_font.masters:
        draw()
        drawLayer(master, glyph.layers[master.id])
        saveImage("~/Desktop/%s.svg" % master.name)
        
def get_axis_ranges():
    axis_values = [set(master.axes[index] for master in current_font.masters) for index, axis in enumerate(current_font.axes)]
    axis_ranges = [[min(axis), max(axis)] for axis in axis_values]
    return axis_ranges
    
animate_through_coordinates()