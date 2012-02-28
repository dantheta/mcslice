
import sys

from MCSlice import Pos,Explorer


if len(sys.argv) == 3:
	pos = Pos(int(sys.argv[1]),0,int(sys.argv[2]))
else:
	pos = Pos()
explore = Explorer(pos)
explore.main()
explore.shutdown()
