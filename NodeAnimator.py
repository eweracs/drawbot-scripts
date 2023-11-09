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

		self.easing_function = "linear"
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

	def select_easing_function(self, easing):
		easing_functions_dict = {
			"linear": LinearInOut,
			"quad_ease_in": QuadEaseIn,
			"quad_ease_out": QuadEaseOut,
			"quad_ease_in_out": QuadEaseInOut,
			"cubic_ease_in": CubicEaseIn,
			"cubic_ease_out": CubicEaseOut,
			"cubic_ease_in_out": CubicEaseInOut,
			"quart_ease_in": QuarticEaseIn,
			"quart_ease_out": QuarticEaseOut,
			"quart_ease_in_out": QuarticEaseInOut,
			"quint_ease_in": QuinticEaseIn,
			"quint_ease_out": QuinticEaseOut,
			"quint_ease_in_out": QuinticEaseInOut,
			"sine_ease_in": SineEaseIn,
			"sine_ease_out": SineEaseOut,
			"sine_ease_in_out": SineEaseInOut,
			"circ_ease_in": CircularEaseIn,
			"circ_ease_out": CircularEaseOut,
			"circ_ease_in_out": CircularEaseInOut,
			"expo_ease_in": ExponentialEaseIn,
			"expo_ease_out": ExponentialEaseOut,
			"expo_ease_in_out": ExponentialEaseInOut,
			"elastic_ease_in": ElasticEaseIn,
			"elastic_ease_out": ElasticEaseOut,
			"elastic_ease_in_out": ElasticEaseInOut,
			"back_ease_in": BackEaseIn,
			"back_ease_out": BackEaseOut,
			"back_ease_in_out": BackEaseInOut,
			"bounce_ease_in": BounceEaseIn,
			"bounce_ease_out": BounceEaseOut,
			"bounce_ease_in_out": BounceEaseInOut,
		}

		# Use get() to provide a default value if the easing is not found
		easing_function = easing_functions_dict.get(easing, LinearInOut)
		return easing_function

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
		offset_y = (self.page_height - (layer.ascender + layer.descender)) / 2
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

	def return_layers_for_interpolations_for_glyph(self, glyph, duration=None):
		interpolated_layers = []

		# Set duration
		if duration is None:
			duration = self.duration

		instance = GSInstance()
		instance.font = self.font

		steps = self.fps * duration

		axis_ranges = self.get_axis_ranges()

		for step in range(steps):
			for index, axis in enumerate(self.font.axes):
				instance.internalAxesValues[axis.axisId] = self.select_easing_function(self.easing_function)(
					axis_ranges[index][0],
					axis_ranges[index][1],
					steps - 1
				).ease(step)
			proxy = instance.interpolatedFontProxy
			glyph = proxy.glyphs[glyph.name]
			proxy_layer = glyph.layers[0].copy()
			proxy_layer.parent = glyph.layers[0].parent
			interpolated_layers.append(proxy_layer)

		return interpolated_layers

	def animate_all_axes_for_glyph(self, glyph, reverse=False):
		layers_for_glyphs = self.return_layers_for_interpolations_for_glyph(glyph)
		if reverse:
			layers_for_glyphs.reverse()
		for layer in layers_for_glyphs:
			self.draw_page()
			self.draw_layer(layer)

	def build_animation(self, steps=None, format="mp4"):
		if steps is None:
			# Example steps. TODO: Make this a dictionary with the step name as key and arguments as values
			steps = [
				"animate_all_axes_for_glyphs",
				"animate_all_axes_for_glyphs_reverse"
			]
		for glyph in self.glyphs:
			newDrawing()
			for step in steps:
				if step == "animate_all_axes_for_glyphs":
					self.animate_all_axes_for_glyph(glyph)
				elif step == "animate_all_axes_for_glyphs_reverse":
					self.animate_all_axes_for_glyph(glyph, reverse=True)
			saveImage("~/Desktop/%s.%s" % (glyph.name, format))


# Example usage
animator = NodeAnimator(["a", "s"])
animator.easing_function = "quad_ease_in_out"
animator.path.fill_colour = (0, 0, 0, 0)
animator.off_node.line_colour = (0.2, 0.2, 0.2)
animator.off_node.colour = (0.2, 0.2, 0.2)
animator.on_node.shape = "rect"
animator.on_node.smooth_shape = "oval"

animator.build_animation()
