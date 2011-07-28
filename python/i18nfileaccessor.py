from buffer import Buffer

class I18nFileAccessor(object):
	def __init__(self, path):
		self.b = Buffer()
  
		with open(path, 'r') as f:
			self.b.addInfos(f.read())

		self._indexes = dict()
    
		self.b.setCursor(self.b.readInt())
		nbValues = self.b.readInt() / 8;
		for i in range(0, nbValues):
			key = self.b.readInt()
			val = self.b.readInt()

			self._indexes[key] = val

	def getText(self, arg1):
		pos = self._indexes[arg1]
  
		self.b.setCursor(pos)

		return self.b.readUTF()

	def hasText(self, arg1):
		return self._indexes[arg1]
