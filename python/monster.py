# id     int
# nameId int
# gfxId  int
# race   int
# grade  int

# grade             int
# monsterId         int
# level             int
# lifePoints        int
# actionPoints      int
# movementPoints    int
# paDodge           int
# pmDodge           int
# earthResistance   int
# airResistance     int
# fireResistance    int
# waterResistance   int
# neutralResistance int

from buffer import Buffer

class Monster(object):
	def __init__(self):
		self._id = 0
		self._nameId = 0
		self._gfxId = 0
		self.race = 0
		self.grade = 0

class Monsters(object):
	def __init__(self, path):
		self.b = Buffer()

		with open(path, 'r') as f:
			self.b.addInfos(f.read())

		c = self.b.readUTF(3)
		if(cmp(c, "D2O") != 0):
			print("D2O error: {}".format(c))
			raise Exception()

		self._indexes = dict()

		self.b.setCursor(self.b.readUnsignedInt());

		nbValues = self.b.readInt() / 8;
		for i in range(0, nbValues):
			key = self.b.readInt();
			val = self.b.readInt();

			self._indexes[key] = val;

		'''
		int nbClasses = MonsterDecode::_stream->readInt();
		printf("nbclass = %d\n", nbClasses);
		for(int i = 0; i < nbClasses; i++){
			int id = MonsterDecode::_stream->readInt();
			std::string lastName = MonsterDecode::_stream->readUTF();
			std::string firstName = MonsterDecode::_stream->readUTF();
			cout << "(" << id << ") " << firstName << "." << lastName << endl;
			int nbFields = MonsterDecode::_stream->readInt();
			for(int j = 0; j < nbFields; j++){
				std::string fieldName = MonsterDecode::_stream->readUTF();
				int fieldType = MonsterDecode::_stream->readInt();
				cout << "\t" << fieldName << ", type : " << fieldType << endl;

			}
		}

		return 0'''

	def getObj(self, arg1):
		mstr = Monster()

		pos = self._indexes[arg1];

		self.b.setCursor(pos);

		if(self.b.readInt() != 3):
			print("!= 2 ?");
			return None;

		mstr._id = self.b.readInt()
		mstr._nameId = self.b.readInt() # readI18n
		mstr._gfxId = self.b.readInt()
		mstr._race = self.b.readInt()
		mstr._grade = 0 # self.b.readInt()

		return mstr;

	def hasObj(arg1):
		return self._indexes[arg1]
