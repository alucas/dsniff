import struct

class BufferToSmall(Exception):
	def __init__(self, value):
		self.parameter = value

	def __str__(self):
		return repr(self.parameter)

class Buffer(object):
	def __init__(self, string):
		self._string = string
		self._size = len(string)
		self._cursor = 0

	def getSize(self):
		return self._size

	def readUnsignedByte(self):
		if(self._cursor + 1 <= self._size):
			self._cursor += 1
			return struct.unpack('!B', self._string[self._cursor-1:self._cursor])[0]
		else:
			raise BufferToSmall("query: {}, available: {}".format(1, self._size - self._cursor))

	def readByte(self):
		if(self._cursor + 1 <= self._size):
			self._cursor += 1
			return struct.unpack('!b', self._string[self._cursor-1:self._cursor])[0]
		else:
			raise BufferToSmall("query: {}, available: {}".format(1, self._size - self._cursor))

	def readUnsignedShort(self):
		if(self._cursor + 2 <= self._size):
			self._cursor += 2
			return struct.unpack('!H', self._string[self._cursor-2:self._cursor])[0]
		else:
			raise BufferToSmall("query: {}, available: {}".format(2, self._size - self._cursor))

	def readShort(self):
		if(self._cursor + 2 <= self._size):
			self._cursor += 2
			return struct.unpack('!h', self._string[self._cursor-2:self._cursor])[0]
		else:
			raise BufferToSmall("query: {}, available: {}".format(2, self._size - self._cursor))

	def readInt(self):
		if(self._cursor + 4 <= self._size):
			self._cursor += 4
			return struct.unpack('!i', self._string[self._cursor-4:self._cursor])[0]
		else:
			raise BufferToSmall("query: {}, available: {}".format(4, self._size - self._cursor))

	def readUnsignedInt(self):
		if(self._cursor + 4 <= self._size):
			self._cursor += 4
			return struct.unpack('!I', self._string[self._cursor-4:self._cursor])[0]
		else:
			raise BufferToSmall("query: {}, available: {}".format(4, self._size - self._cursor))

	def readBoolean(self):
		if(self._cursor + 1 <= self._size):
			self._cursor += 1
			return struct.unpack('!?', self._string[self._cursor-1:self._cursor])[0]
		else:
			raise BufferToSmall("query: {}, available: {}".format(1, self._size - self._cursor))

	def readUTF(self):
		size = self.readUnsignedShort()
		if(self._cursor + size <= self._size):
			self._cursor += size

			return self._string[self._cursor-size:self._cursor]
		else:
			raise BufferToSmall("query: {}, available: {}".format(size, self._size - self._cursor))

