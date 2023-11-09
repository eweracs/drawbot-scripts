from GlyphsApp import *
import os
from easing_functions import *

current_font = Glyphs.font

width = 1000
height = 1000
handle_size = 8
size = 170
fps = 30
duration = 2


def draw_on_node(node, handle_size):
	if handle_size == 0:
		return
	fill(1, 1, 1)
	if node.type == GSCURVE or node.type == GSLINE:
		if node.smooth:
			oval(node.position.x - (handle_size / 2), node.position.y - (handle_size / 2), handle_size, handle_size)
		else:
			rect(node.position.x - (handle_size / 2), node.position.y - (handle_size / 2), handle_size, handle_size)


def draw_off_node(node, handle_size):
	if handle_size == 0:
		return
	fill(0.2, 0.2, 0.2)
	if node.type != GSCURVE and node.type != GSLINE:
		index = node.parent.indexOfNode_(node)
		prev_node = node.parent.nodes[index - 1]
		next_node = node.parent.nodes[index + 1]
		if prev_node.type == GSOFFCURVE:
			newPath()
			moveTo(node.position)
			lineTo(next_node.position)
			drawPath()
		else:
			newPath()
			moveTo(node.position)
			lineTo(prev_node.position)
			drawPath()
		oval(node.position.x - (handle_size / 2), node.position.y - (handle_size / 2), handle_size, handle_size)


def draw_layer(master, layer, remove_overlap=True):
	offset_x = (width - layer.width) / 2
	offset_y = abs(master.ascender - master.descender) / 4
	translate(offset_x, offset_y)
	strokeWidth(0.5)
	stroke(0.2, 0.2, 0.2)
	save()
	layer = layer.copyDecomposedLayer()
	if remove_overlap:
		layer.removeOverlap()
	for path in layer.paths:
		for node in path.nodes:
			draw_off_node(node, handle_size)
		for node in path.nodes:
			draw_on_node(node, handle_size)
	fill(0, 0, 0, 0)
	stroke(1, 1, 1)
	drawPath(layer.bezierPath)


def draw():
	newPage(width, height)
	frameDuration(1 / fps)
	fill(0, 0, 0)
	rect(0, 0, width, height)


def return_first_layer_for_each_glyph():
	first_layers = []
	for glyph in current_font.glyphs:
		if not glyph.export:
			continue
		layer = glyph.layers[0]
		first_layers.append(layer)


def return_layers_for_interpolations(glyph, axis_ranges, steps=100):
	instance = GSInstance()
	instance.font = current_font

	interpolated_layers = []

	for step in range(steps):
		for index, axis in enumerate(current_font.axes):
			instance.internalAxesValues[axis.axisId] = CubicEaseInOut(
				axis_ranges[index][0],
				axis_ranges[index][1],
			    steps - 1
			    ).ease(step)
		proxy = instance.interpolatedFontProxy
		glyph = proxy.glyphs[glyph.name]
		interpolated_layers.append(glyph.layers[0].copy())

	return interpolated_layers


def return_layers_for_interpolations_intermediates(glyph, axis_ranges, steps=100):
	interpolated_layers = {glyph.layers[0].master.id: []}
	layer = GSLayer()
	proxy_glyph = glyph.copy()
	proxy_glyph.name = glyph.name + ".proxy"
	current_font.glyphs.append(proxy_glyph)
	proxy_glyph.layers.append(layer)
	layer.attributes["coordinates"] = {}
	for step in range(steps):
		axis_locations = [CubicEaseInOut(axis_ranges[index][0], axis_ranges[index][1], steps - 1).ease(step) for
		                  index, axis in enumerate(axis_ranges)]
		layer.attributes["coordinates"] = {axis.axisId: axis_locations[index] for index, axis in
		                                   enumerate(current_font.axes)}
		layer.reinterpolate()
		layer.decomposeComponents()
		layer.removeOverlap()
		interpolated_layers[glyph.layers[0].master.id].append(layer.copy())
	del current_font.glyphs[proxy_glyph.name]

	return (interpolated_layers)


def animate_through_coordinates():
	interpolated_layers = return_layers_for_interpolations(current_font.glyphs["a"], get_axis_ranges(), duration * fps)

	for master_id in interpolated_layers:
		for layer in interpolated_layers[master_id]:
			draw()
			draw_layer(current_font.fontMasterForId_(master_id), layer)

	saveImage("~/Desktop/test.gif")


def svg_for_masters(glyph):
	for master in current_font.masters:
		draw()
		draw_layer(master, glyph.layers[master.id])
		saveImage("~/Desktop/%s.svg" % master.name)


def get_axis_ranges():
	axis_values = [set(master.axes[index] for master in current_font.masters) for index, axis in
	               enumerate(current_font.axes)]
	axis_ranges = [[min(axis), max(axis)] for axis in axis_values]
	return axis_ranges


for layer in return_layers_for_interpolations_intermediates(current_font.glyphs["a"], get_axis_ranges(), duration * fps):
	draw()
	draw_layer(current_font.masters[0], layer)
