import pygame
import simplejson


def create_color(colorstr):
	"""Create pygame Color from hex string"""
	try:
		return pygame.Color(colorstr[:7])
	except TypeError:
		print >>sys.stderr, "Invalid color: ", colorstr[:7]
		return pygame.Color(0,0,0,255)

# load blocks.json
blockdata = simplejson.load(open('blocks.json'))
BLOCKS = dict([ (x['blockId'], (x['name'], create_color(x['color'])))
	for x in blockdata ])

class Chunk():
	def __init__(self, path):
		self.layers = {}
		self.path = path

		fp = open(path)
		self.data = [ord(x) for x in fp.read(32768)]
		fp.close()

		self.draw_layers()

	def draw_layers(self):
		"""Draw layers to offscreen surface after load."""
		for z in xrange(0,16):
			#create surface for this layer
			srf = pygame.Surface((16,128))
			for x in xrange(0,16):
				for y in xrange(0,128):
					v = self.data[ self.xyz_to_offset( x,y,z) ]
					if v != 0:
						srf.fill( BLOCKS.get(v, [0,0])[1], 	(x, 127 -y, 1, 1 ))
			#save layer to dict for this chunk
			self.layers[z] = srf

	def get_layer(self, index):
		return self.layers[index]

	def __getitem__(self, index):
		"""Get value at offset in this chunk's data"""
		return self.data[index]

	def get_value(self, x, y, z):
		"""Get value for xyz in chunk"""
		return self.data[ self.xyz_to_offset(x,y,z) ]

	def get_name(self, x, y, z):
		blockinfo = BLOCKS.get(self.get_value(x,y,z))
		return blockinfo[0] if blockinfo else ''

	@staticmethod
	def xyz_to_offset(x, y, z):
		"""Maps x/y/z co-ordinates to a byte offset in chunk data."""
		v  = y + (z % 16) * 128 + (x % 16) * 128 * 16
		return v
