
import string
import sys
import zlib
import os

def be32toh(buf):
	# named after the c library function
	"""Convert big-endian 4byte int to a python numeric value."""
	out = (ord(buf[0]) << 24) + (ord(buf[1]) << 16) + \
		(ord(buf[2]) << 8) + ord(buf[3])
	return out

for filename in sys.argv[1:]:

	base = os.path.basename(filename)
	print base
	parts = base.split('.')
	print parts

	outpath = os.path.join( 'dump', parts[1], parts[2])
	print outpath
	try:
		os.makedirs( outpath, 0775)
	except: pass

	fp = open(filename)
	for chunknum in range(0, 1024):
		# seek to chunk header
		fp.seek(chunknum * 4, 0)
		buf = fp.read(4)

		# uninitialized chunks don't have an offset
		if buf == '\0\0\0\0':
			continue

		# 24-bit int bigendian conversion
		loc = (ord(buf[0]) << 16) + (ord(buf[1]) << 8) + ord(buf[2])
		length = ord(buf[3])

		# seek to start of block data
		fp.seek(loc * 4096, 0)
		buf = fp.read(length * 4096)
		# read block length and compression type
		datalen = be32toh(buf[0:4])
		compr = ord(buf[4])

		# decompress data
		data = zlib.decompress(buf[5:datalen+5])[2:]

		# crappy seek to blocks data inside decompressed area
		blockstart = data.find('Blocks') + 10

		# dump uncompressed data to a file
		fpout = open(os.path.join('dump', parts[1], parts[2], "%04d.chunk"%(chunknum)), 'w')
		fpout.write(data[blockstart:blockstart+32768])
		fpout.close()

	fp.close()
