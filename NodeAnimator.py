from GlyphsApp import *
from easing_functions import *


class NodeAnimator:
	def __init__(self, glyph_names=None):
		self.font = Glyphs.font

		# Defaults
		self.size = 1
		self.fill_colour = (1, 1, 1)
		self.handle_size = 8
		self.shape = "oval"
		self.stroke_width = 0.5

		self.remove_overlap = True

		self.page_width = 1000
		self.page_height = 1000

		self.background_colour = (0, 0, 0)

		self.fps = 30
		self.duration = 2
		# End defaults

		class OnNode:
			def __init__(self, animator):
				self.size = animator.handle_size
				self.shape = animator.shape
				self.colour = animator.fill_colour
				self.stroke_width = animator.stroke_width
				self.line_colour = animator.fill_colour
				self.smooth_shape = animator.shape
				self.smooth_colour = animator.fill_colour

		class OffNode:
			def __init__(self, animator):
				self.size = animator.handle_size
				self.shape = animator.shape
				self.colour = animator.fill_colour
				self.stroke_width = animator.stroke_width
				self.line_colour = animator.fill_colour
				self.line_width = animator.stroke_width
				self.line_colour = animator.fill_colour

		class Path:
			def __init__(self, animator):
				self.fill_colour = animator.fill_colour
				self.stroke_width = animator.stroke_width
				self.stroke_colour = animator.fill_colour

		self.on_node = OnNode(self)
		self.off_node = OffNode(self)
		self.path = Path(self)

		if glyph_names is None:
			glyph_names = ["a"]
		self.glyphs = [self.font.glyphs[glyph_name] for glyph_name in glyph_names]
		if not self.glyphs:
			print("Default glyph \"a\" missing in font. Please specify a glyph.")
			return

		self.size_factor = self.font.upm / self.page_height * self.size

	def get_axis_ranges(self):

		# Returns a list of the axis ranges for the current font, in the same order as the axes. Format:
		# [[min_axis_1, max_axis_1], [min_axis_2, max_axis_2], ...]
		current_font = self.font

		# Collect all axis values
		axis_values = [set(master.axes[index] for master in current_font.masters) for index, axis in
					   enumerate(current_font.axes)]

		# Convert to list with only min and max, sort
		axis_ranges = [[min(axis), max(axis)] for axis in axis_values]

		return axis_ranges

	def draw_on_node(self, node):
		if self.on_node.size == 0:
			return

		# Check if current node is an on-curve node
		if node.type == GSCURVE or node.type == GSLINE:

			# Set stroke properties
			strokeWidth(self.on_node.stroke_width)
			stroke(*self.on_node.line_colour)

			# Calculate node position and size
			measurements = (node.position.x - (self.on_node.size / 2),
							node.position.y - (self.on_node.size / 2),
							self.on_node.size,
							self.on_node.size)

			# Treat smooth nodes
			if node.smooth:
				fill(*self.on_node.smooth_colour)
				if self.on_node.smooth_shape == "oval":
					oval(*measurements)
				elif self.on_node.smooth_shape == "rect":
					rect(*measurements)

			# Treat other nodes
			else:
				fill(*self.on_node.colour)
				if self.on_node.shape == "oval":
					oval(*measurements)
				elif self.on_node.shape == "rect":
					rect(*measurements)

	def draw_off_node(self, node):
		if self.on_node.size == 0:
			return

		# Check if current node is an off-curve node
		if node.type != GSCURVE and node.type != GSLINE:

			# Set fill properties
			fill(*self.off_node.colour)

			# Set stroke properties
			strokeWidth(self.off_node.stroke_width)
			stroke(*self.off_node.line_colour)

			# Calculate node position and size
			measurements = (node.position.x - (self.off_node.size / 2),
							node.position.y - (self.off_node.size / 2),
							self.off_node.size,
							self.off_node.size)

			# If previous node is an off-curve node, draw a line between the two
			if node.prevNode.type == GSOFFCURVE:
				newPath()
				moveTo(node.position)
				lineTo(node.nextNode.position)
				drawPath()

			# Else, draw a line between the current node and the previous node
			else:
				newPath()
				moveTo(node.position)
				lineTo(node.prevNode.position)
				drawPath()
			oval(*measurements)

	def draw_layer(self, layer):

		# Scale document to fit
		scale(self.size_factor, center=(self.page_width / 2, self.page_height / 2))

		# Set position, centred
		offset_x = (self.page_width - layer.bounds.size.width) / 2
		offset_y = (self.page_height - layer.bounds.size.height) / 2
		translate(offset_x, offset_y)
		save()

		# Decompose components
		layer = layer.copyDecomposedLayer()

		# Remove overlap if specified
		if self.remove_overlap:
			layer.removeOverlap()

		# Draw nodes
		for path in layer.paths:
			for node in path.nodes:
				self.draw_off_node(node)
			for node in path.nodes:
				self.draw_on_node(node)

		# Draw path outline
		fill(*self.path.fill_colour)
		stroke(*self.path.stroke_colour)
		drawPath(layer.bezierPath)

	def draw_page(self):
		newPage(self.page_width, self.page_height)
		frameDuration(1 / self.fps)
		fill(*self.background_colour)
		rect(0, 0, self.page_width, self.page_height)

	def return_layers_for_interpolations_for_glyphs(self, duration=None):
		interpolated_layers = {glyph.name: [] for glyph in self.glyphs}

		# Set duration
		if duration is None:
			duration = self.duration

		instance = GSInstance()
		instance.font = self.font

		steps = self.fps * duration

		axis_ranges = self.get_axis_ranges()

		for glyph in self.glyphs:
			for step in range(steps):
				for index, axis in enumerate(self.font.axes):
					instance.internalAxesValues[axis.axisId] = CubicEaseInOut(
						axis_ranges[index][0],
						axis_ranges[index][1],
						steps - 1
					).ease(step)
				proxy = instance.interpolatedFontProxy
				glyph = proxy.glyphs[glyph.name]
				proxy_layer = glyph.layers[0].copy()
				proxy_layer.parent = glyph.layers[0].parent
				interpolated_layers[glyph.name].append(proxy_layer)

		return interpolated_layers

	def animate_all_axes_for_glyphs(self, reverse=False):
		layers_for_glyphs = self.return_layers_for_interpolations_for_glyphs()
		if reverse:
			layers_for_glyphs = {glyph_name: list(reversed(layers_for_glyphs[glyph_name])) for glyph_name in
								 layers_for_glyphs}
		for glyph in self.glyphs:
			for layer in layers_for_glyphs[glyph.name]:
				self.draw_page()
				self.draw_layer(layer)
			saveImage("~/Desktop/%s.gif" % glyph.name)


# Example usage
animator = NodeAnimator(["a"])
animator.path.fill_colour = (0, 0, 0, 0)
animator.off_node.line_colour = (0.2, 0.2, 0.2)
animator.off_node.colour = (0.2, 0.2, 0.2)
animator.on_node.shape = "rect"
animator.on_node.smooth_shape = "oval"

animator.animate_all_axes_for_glyphs()
animator.animate_all_axes_for_glyphs(reverse=True)