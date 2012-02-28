
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

