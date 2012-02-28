
import pygame
from pygame.locals import *

from chunk import Chunk


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

		# used for description in top right
		self.point_data = {'x': 0, 'y': 0, 'z': 0, 'name': '' }

		self.chunks = {}
		self.pos = pos
		self.scale = self.SCALE

	def keydown(self, evt):
		"""Keyboard key down event handler"""
		if evt.key == K_EQUALS:
			self.scale += 1
			print "Zoom: ", self.scale
		if evt.key == K_MINUS:
			self.scale -= 1
			print "Zoom: ", self.scale
		if evt.key == K_PAGEDOWN:
			self.pos.z += 10
		if evt.key == K_PAGEUP:
			self.pos.z -= 10
		if evt.key == K_DOWN:
			self.pos.z += 1
		if evt.key == K_UP:
			self.pos.z -= 1
		if evt.key == K_LEFT:
			self.pos.x -= 16
		if evt.key == K_RIGHT: 
			self.pos.x += 16
		if evt.key == K_q:
			self.running = False

	def keyup(self, evt):
		"""Keyboard key release event handler"""
		pass

	def mousedown(self, evt):
		"""Mouse buttonpress event handler"""
		mx, my = evt.pos

		x = self.pos.x + ((mx-512)/self.scale)
		y =	(( 300 - my )/ self.scale)+64 
		z = self.pos.z 

		print mx, my

		print x,y,z

		chunkobj = self.get_chunk(x,z)
		if not chunkobj:
			return
		name = chunkobj.get_name( x,y,z)

		self.point_data = {
			'x': x,
			'y': y,
			'z': z,
			'name': name
		}


	def get_chunk(self, x,z):
		region = x/512, z/512
		chunknum = ((x/16) % 32) + (((z/16) % 32) * 32)
		if not (region, chunknum) in self.chunks:
			try:
				print "Opening: ", region, chunknum
				newchunk = Chunk("dump/%d/%d/%04d.chunk"%(region[0], region[1], chunknum))
				self.chunks[ (region, chunknum) ] = newchunk
				return newchunk
			except IOError:
				print "Not found: ", region, chunknum
				self.chunks[ (region, chunknum) ] = None
				return None
		else:
			return self.chunks[ (region, chunknum) ]
				
	def clear(self):
		"""Clear drawing canvas"""
		self.surface.fill(0)

	def drawtext(self, txt, tx, ty):
		fsrf = self.font.render(txt, True, pygame.Color('white'))
		self.surface.blit(fsrf, (tx ,ty))

	def draw(self):

		# how many chunks fit in the screen

		chunks = (1024 / 16) / self.scale

		#center on chunk at self.pos.x

		#count chunks from left to right
		for x in xrange(0-chunks/2, chunks/2):
			chunkx = x * 16
			chunkobj = self.get_chunk((self.pos.x + chunkx), self.pos.z)
			if chunkobj:
				if self.scale == 1:
					layer = chunkobj.get_layer( self.pos.z % 16 )
				else:	
					layer = pygame.transform.scale(chunkobj.get_layer( self.pos.z % 16 ), (16*self.scale, 128*self.scale))
				self.surface.blit(layer, (512 + (chunkx*self.scale) , 300 - ( 64 * self.scale )))


		self.drawtext("X: %d" %(self.pos.x), 0, 0)
		self.drawtext("Z: %d" %( self.pos.z), 0, 40)

		self.drawtext("X: %d" %( self.point_data['x']), 850, 0)
		self.drawtext("Y: %d" %( self.point_data['y']), 850, 30)
		self.drawtext("Z: %d" %( self.point_data['z']), 850, 60)
		self.drawtext("Name: %s" %( self.point_data['name']), 850, 90)

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

	def shutdown(self):
		pygame.display.quit()

