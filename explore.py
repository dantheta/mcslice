
import sys
import pygame
import simplejson
from pygame.locals import *


def create_color(colorstr):
	r,g,b = colorstr[1:3], colorstr[3:5], colorstr[5:7]
	return pygame.Color(int(r,16), int(g, 16), int(b,16), 255)

def mapxyz(x, y, z):
	v  = y + (z % 16) * 128 + (x % 16) * 128 * 16
	return v

blockdata = simplejson.load(open('blocks.json'))
BLOCKS = dict([ (x['blockId'], (x['name'], create_color(x['color']))) 
	for x in blockdata ])

class Chunk():
	def __init__(self, data):
		self.data = data
		self.layers = {}

		self.draw_layers()

	def draw_layers(self):
		for z in xrange(0,16):
			srf = pygame.Surface((16,128))
			for x in xrange(0,16):
				for y in xrange(0,128):
					v = self.data[ mapxyz( x,y,z) ]
					if v != 0:
						srf.fill( BLOCKS.get(v, [0,0])[1], 	(x, 127 -y, 1, 1 ))
			self.layers[z] = srf

	def get_layer(self, index):
		return self.layers[index]


	def __getitem__(self, index):
		return self.data[index]

class Pos:
	def __init__(self, x = 0, y = 0, z = 0):
		self.x = x
		self.y = y
		self.z = z

		self.dx = 0
		self.dy = 0
		self.dz = 0

	def move(self):
		self.x += self.dx
		self.y += self.dy
		self.z += self.dz

class Explorer:
	K_AMT = 16
	SCALE = 2

	def __init__(self, pos):
		pygame.init()
		pygame.display.init()
		pygame.font.init()
		self.surface = pygame.display.set_mode( (1024,600), pygame.DOUBLEBUF|pygame.HWSURFACE)
		self.font = pygame.font.SysFont(pygame.font.get_default_font(), 24)
		self.running = True
		self.point_data = {'x': 0, 'y': 0, 'z': 0, 'name': '' }

		self.chunks = {}
		self.pos = pos
		self.scale = self.SCALE

	def keydown(self, evt):
		#if evt.key == K_DOWN:
		#	self.pos.dz -= self.K_AMT
		#if evt.key == K_UP:
		#	self.pos.dz += self.K_AMT
		#if evt.key == K_LEFT:
		#	self.pos.dx -= self.K_AMT
		#if evt.key == K_RIGHT: 
		#	self.pos.dx += self.K_AMT
		if evt.key == K_EQUALS:
			self.scale += 1
			print "Zoom: ", self.scale
		if evt.key == K_MINUS:
			self.scale -= 1
			print "Zoom: ", self.scale
		if evt.key == K_PAGEDOWN:
			self.pos.z += 10# self.K_AMT
		if evt.key == K_PAGEUP:
			self.pos.z -= 10# self.K_AMT
		if evt.key == K_DOWN:
			self.pos.z += 1# self.K_AMT
		if evt.key == K_UP:
			self.pos.z -= 1# self.K_AMT
		if evt.key == K_LEFT:
			self.pos.x -= 16
		if evt.key == K_RIGHT: 
			self.pos.x += 16
		if evt.key == K_q:
			self.running = False

	def keyup(self, evt):
		#if evt.key == K_DOWN:
		#	self.pos.dz += self.K_AMT
		#if evt.key == K_UP:
		#	self.pos.dz -= self.K_AMT
		#if evt.key == K_LEFT:
		#	self.pos.dx += self.K_AMT
		#if evt.key == K_RIGHT: 
		#	self.pos.dx -= self.K_AMT
		pass

	def mousedown(self, evt):
		mx, my = evt.pos

		x = self.pos.x + ((mx-512)/self.scale)
		y =	(( 300 - my )/ self.scale)+64 
		z = self.pos.z 

		print mx, my

		print x,y,z

		region = self.get_region(x,z)
		chunk = self.get_chunk(x,z)
		self.open_chunk(region, chunk)
		name = BLOCKS.get(self.get_value(region, chunk, x,y,z), ('',0))[0]

		self.point_data = {
			'x': x,
			'y': y,
			'z': z,
			'name': name
		}


		

	def get_region(self, x, z):
		return x/512, z/512

	def get_chunk(self, x, z):
		return ((x/16) % 32) + (((z/16) % 32) * 32)

	def open_chunk(self, region, chunk):
		if not (region[0], region[1], chunk) in self.chunks:
			try:
				print "Opening: ", region, chunk
				fp = open("dump/%d/%d/%04d.chunk"%(region[0], region[1], chunk))
				buf = [ ord(x) for x in fp.read(32768) ]
				newchunk = Chunk(buf)
				self.chunks[ (region[0], region[1], chunk) ] = newchunk
				fp.close()
				return newchunk
			except IOError:
				self.chunks[ (region[0], region[1], chunk) ] = None
				return None
		else:
			return self.chunks[ (region[0], region[1], chunk) ]
				
	
	def get_value(self, region, chunk, x, y, z):
		p =  mapxyz(x,y,z) 
		if self.chunks[(region[0], region[1], chunk)] == None:
			return '\0'
		return self.chunks[ (region[0], region[1], chunk) ][p]


	def clear(self):
		self.surface.fill(0)

	def draw(self):
		def drawtext(txt, ty):
			fsrf = self.font.render(txt, True, pygame.Color('white'))
			self.surface.blit(fsrf, (850,ty))

		# how many chunks fit in the screen

		chunks = (1024 / 16) / self.scale

		#center on chunk at self.pos.x

		for x in xrange(0-chunks/2, chunks/2):
			chunkx = x * 16
			region = self.get_region((self.pos.x + chunkx), self.pos.z)
			chunk = self.get_chunk((self.pos.x + chunkx), self.pos.z)
			chunkobj = self.open_chunk(region, chunk)
			if chunkobj:
				if self.scale == 1:
					layer = chunkobj.get_layer( self.pos.z % 16 )
				else:	
					layer = pygame.transform.scale(chunkobj.get_layer( self.pos.z % 16 ), (16*self.scale, 128*self.scale))
				self.surface.blit(layer, (512 + (chunkx*self.scale) , 300 - ( 64 * self.scale )))

			#for y in xrange(0, 128):
			#	v = self.get_value(region, chunk, self.pos.x + x, y, self.pos.z + ofz)
			#	if v != 0 or y < 64:
			#		self.surface.fill( BLOCKS.get(v, [0,0])[1], 
			#			(512 + (self.scale*x), 300 + (64 * self.scale) -(self.scale*y) + (self.scale*ofz), self.scale, self.scale))

		fsrf = self.font.render("X: %d" %( self.pos.x), True, pygame.Color('white'))
		self.surface.blit(fsrf, (0,0))
		fsrf = self.font.render("Z: %d" %( self.pos.z), True, pygame.Color('white'))
		self.surface.blit(fsrf, (0,40))

		drawtext("X: %d" %( self.point_data['x']), 0)
		drawtext("Y: %d" %( self.point_data['y']), 30)
		drawtext("Z: %d" %( self.point_data['z']), 60)
		drawtext("Name: %s" %( self.point_data['name']), 90)

	def main(self):
		self.draw()
		pygame.display.update()
		pygame.display.flip()
		while self.running:
			self.pos.move()
			evt = pygame.event.wait()
			if evt.type != NOEVENT:
				self.clear()
				if evt.type == KEYDOWN:
					self.keydown(evt)
				elif evt.type == KEYUP:
					self.keyup(evt)
				elif evt.type == MOUSEBUTTONDOWN:
					self.mousedown(evt)
				else:
					continue
				if not self.running:
					break

				self.draw()
				pygame.display.update()
				pygame.display.flip()

print sys.argv
if len(sys.argv) == 3:
	pos = Pos(int(sys.argv[1]),0,int(sys.argv[2]))
else:
	pos = Pos()
explore = Explorer(pos)
explore.main()
