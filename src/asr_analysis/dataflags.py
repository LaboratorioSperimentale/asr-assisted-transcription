from enum import Flag, auto

class position(Flag):
	tu_start = auto()
	tu_end = auto()
	tu_inner = auto()

class intonation(Flag):
	weakly_ascending = auto()
	descending = auto()
	ascending = auto()

class pace(Flag):
	fast = auto()
	slow = auto()

class volume(Flag):
	high = auto()
	low = auto()