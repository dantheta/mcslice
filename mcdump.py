
import mmap
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

	regionx = int(parts[1])
	regionz = int(parts[2])

	outpath = os.path.join( 'dump', parts[1], parts[2])
	print outpath
	try:
		os.makedirs( outpath, 0775)
	except: pass

	fp = open(filename)

	# create output datafile, and pad to 64MB.
	fpout = open(os.path.join(outpath, 'data.dat'), 'r+')
	for i in range(65536):
		fpout.write('\0' * 1024)
	fpout.flush()

	#mmap output datafile
	mm = mmap.mmap(fpout.fileno(), 65536*1024, prot = mmap.PROT_READ|mmap.PROT_WRITE, flags = mmap.MAP_SHARED)


	for chunknum in range(0, 1024):
		# seek to chunk header
		fp.seek(chunknum * 4, 0)
		buf = fp.read(4)

		# uninitialized chunks don't have an offset
		if buf == '\0\0\0\0':
			continue


		chunkx = (chunknum % 32) * 16
		chunkz = (chunknum / 32) * 16
		print "Chunk: ", chunkx, chunkz

		value = be32toh(buf)
		loc = value >> 8
		length = value % 256

		# seek to start of block data
		fp.seek(loc * 4096, 0)
		buf = fp.read(length * 4096)
		# read block length and compression type
		datalen = be32toh(buf[0:4])
		compr = ord(buf[4])
		assert compr == 2

		# decompress data
		data = zlib.decompress(buf[5:datalen+5])[2:]


		lastfound = data.find('Sections')
		blockstart = None
		while True:
			# search for "Blocks" tags in the chunk
			blockstart = data.find('Blocks', lastfound)
			if blockstart == -1:
				# stop when we don't find any
				break
			# save offset for next search
			lastfound = blockstart+1

			# ensure that the tag before is 'Y' (bit naff)
			assert data[blockstart - 5] == 'Y'
			# get Y height of section
			blocky  = ord(data[blockstart - 4])*16

			# loop over bytes (blocks), transforming and reflecting coords
			for c, d in enumerate(data[blockstart+10:blockstart+4096+10]):
				bx = c % 16
				bz = (c%256) / 16
				by = c / 256

				# reflect about the y axis, so 0 is at the bottom
				offset = ((bz+chunkz) * 131072) + ((255 - by - blocky) * 512) + (bx+chunkx)
				#print "", "C: ", c,  "BY: ", by, "BZ: ", bz, "BX: ", bx, " || " \
				#	"Y: ", by+blocky, "Z: ", bz+chunkz, "X: ", bx + chunkx

				# save to mmap'ed area
				mm[offset] = d

	mm.close()
	fpout.close()

	fp.close()
