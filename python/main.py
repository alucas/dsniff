#!/usr/bin/python

import sys
import traceback

from pcolors import printRed, printBlue, printGreen
from buffer import BufferToSmall, Buffer

####################################################
#
#  Exceptions
#
####################################################

class StopException(Exception):
	def __init__(self, value=None):
		self.parameter = value

	def __str__(self):
		return repr(self.parameter)

class UnknowMessage(Exception):
	def __init__(self, value):
		self.parameter = value

	def __str__(self):
		return repr(self.parameter)

class UnknowHouseType(Exception):
	def __init__(self, value):
		self.parameter = value

	def __str__(self):
		return repr(self.parameter)

class UnknowActorType(Exception):
	def __init__(self, value):
		self.parameter = value

	def __str__(self):
		return repr(self.parameter)

class UnknowDipositionType(Exception):
	def __init__(self, value):
		self.parameter = value

	def __str__(self):
		return repr(self.parameter)

class UnknowHumanType(Exception):
	def __init__(self, value):
		self.parameter = value

	def __str__(self):
		return repr(self.parameter)

class UnknowSkillType(Exception):
	def __init__(self, value):
		self.parameter = value

	def __str__(self):
		return repr(self.parameter)

class UnknowTeamMemberType(Exception):
	def __init__(self, value):
		self.parameter = value

	def __str__(self):
		return repr(self.parameter)

####################################################
#
#  Deserialization
#
####################################################

def decode(string):
	b =  Buffer(string)

	while(b._size > b._cursor):
		try:
			deserialize(b)
		except UnknowMessage as exp:
			printRed("Unknow packet type: {}\n".format(exp))
			printRed("info restantes: {}\n".format(b._size - b._cursor))
			break
		except StopException:
			break
		except:
			print "Exception in user code:"
			print '-'*60
			traceback.print_exc(file=sys.stdout)
			print '-'*60
			break

def deserialize(b):
	var1 = b.readUnsignedShort()
	msgId = var1>>2
	sizeLen = var1 & 0x03
	
	msgSize = 0
	if(sizeLen == 0):
		msgSize = 0
	elif(sizeLen == 1):
		msgSize = b.readUnsignedByte()
	elif(sizeLen == 2):
		msgSize = b.readUnsignedShort()
	else:
		printRed("wrong size {}\n".format(sizeLen))
		raise StopException()

	if(msgSize > b.getSize()):
		printRed("message too short\n")
		raise StopException()

	if(msgId == MapComplementaryInformationsDataMessage.getProtocolId()):
		printBlue("[new map]\n")

		infos = MapComplementaryInformationsDataMessage().deserialize(b)
	elif(msgId == BasicNoOperationMessage.getProtocolId()):
		noOM = BasicNoOperationMessage().deserialize(b)
	elif(msgId == BasicLatencyStatsRequestMessage.getProtocolId()):
		noOM = BasicLatencyStatsRequestMessage().deserialize(b)
	else:	
		raise UnknowMessage(msgId)

class MapComplementaryInformationsDataMessage(object):
	@staticmethod
	def getProtocolId():
		return 226

	def deserialize(self, b):
		self.subareaId = b.readShort()
		self.mapId = b.readInt()
		self.subareaAlignmentSide = b.readByte()

		# Houses
		self.houses = list()

		nbHouse = b.readUnsignedShort()
		for i in range(0, nbHouse):
			houseType = b.readUnsignedShort()
			house = 0

			if(houseType == HouseInformations.getProtocolId()):
				house = HouseInformations().deserialize(b)
			elif(houseType == HouseInformationsExtended.getProtocolId()):
				house = HouseInformationsExtended().deserialize(b)
			else:
				raise UnknowHouseType(houseType)

			self.houses.append(house)

		# Actors
		self.actors = list()

		nbActor = b.readUnsignedShort()
		for i in range(0, nbActor):
			actorType = b.readUnsignedShort()
			actor = 0

			if(actorType == GameRolePlayCharacterInformations.getProtocolId()):
				actor = GameRolePlayCharacterInformations().deserialize(b)
			elif(actorType == GameRolePlayGroupMonsterInformations.getProtocolId()):
				actor = GameRolePlayGroupMonsterInformations().deserialize(b)
			elif(actorType == GameRolePlayTaxColectorInformations.getProtocolId()):
				actor = GameRolePlayTaxColectorInformations().deserialize(b)
			elif(actorType == GameRolePlayPrismInformations.getProtocolId()):
				actor = GameRolePlayPrismInformations().deserialize(b)
			elif(actorType == GameRolePlayNpcInformations.getProtocolId()):
				actor = GameRolePlayNpcInformations().deserialize(b)
			elif(actorType == GameRolePlayMerchantWithGuildInformations.getProtocolId()):
				actor = GameRolePlayMerchantWithGuildInformations().deserialize(b)
			elif(actorType == GameRolePlayMerchantInformations.getProtocolId()):
				actor = GameRolePlayMerchantInformations().deserialize(b)
			elif(actorType == GameRolePlayMountInformations.getProtocolId()):
				actor = GameRolePlayMountInformations().deserialize(b)
			else:
				raise UnknowActorType(actorType)

			self.actors.append(actor)

		# Interactive elements
		self.interactiveElements = list()

		nbInteractiveElement = b.readUnsignedShort()
		for i in range(0, nbInteractiveElement):
			interactiveElement = InteractiveElement().deserialize(b)
			self.interactiveElements.append(interactiveElement)

		# Stated elements
		self.statedElements = list()

		nbStatedElement = b.readUnsignedShort()
		for i in range(0, nbStatedElement):
			statedElement = StatedElement().deserialize(b)
			self.statedElements.append(statedElement)

		# Map obstacles
		self.mapObstacles = list()

		nbMapObstacle = b.readUnsignedShort()
		for i in range(0, nbMapObstacle):
			mapObstacle = MapObstacle().deserialize(b)
			self.mapObstacles.append(mapObstacle)

		# Fights
		self.fights = list()

		nbFight = b.readUnsignedShort()
		for i in range(0, nbFight):
			fight = FightCommonInformations().deserialize(b)
			self.fights.append(fight)


class HouseInformations(object):
	@staticmethod
	def getProtocolId():
		return 111

	def deserialize(self, b):
		flags = b.readByte()
		self.isOnSale = flags & 0x1
		self.isSaleLocked = flags & 0x2
		self.houseId = b.readInt()

		nbDoor = b.readUnsignedShort()
		self.doorsOnMap = list()
		for i in range(0, nbDoor):
			doorInfo = b.readInt()
			self.doorsOnMap.append(doorInfo)

		self.ownerName = b.readUTF()
		self.modelId = b.readShort()

class HouseInformationsExtended(HouseInformations):
	@staticmethod
	def getProtocolId():
		return 112

	def deserialize(self, b):
		HouseInformations.deserialize(self, b)

		self.guildInfo = GuildInformations().deserialize(b)

class GuildInformations(object):
	@staticmethod
	def getProtocolId():
		return 127

	def deserialize(self, b):
		self.guildId = b.readInt()
		self.guildName = b.readUTF()
		self.guildEmblem = GuildEmblem().deserialize(b)

class GuildEmblem(object):
	@staticmethod
	def getProtocolId():
		return 87

	def deserialize(self, b):
		self.symbolShape = b.readShort()
		self.symbolColor = b.readInt()
		self.backgroundShape = b.readShort()
		self.backgroundColor = b.readInt()

class GameContextActorInformations(object):
	@staticmethod
	def getProtocolId():
		return 150

	def deserialize(self, b):
		self.contextualId = b.readInt()
		self.look = EntityLook().deserialize(b)

		dispositionType = b.readUnsignedShort()
		if(dispositionType == EntityDispositionInformations.getProtocolId()):
			self.disposition = EntityDispositionInformations().deserialize(b)
		else:
			raise UnknowDispositionType(dispositionType)

class GameRolePlayActorInformations(GameContextActorInformations):
	@staticmethod
	def getProtocolId():
		return 141

	def deserialize(self, b):
		GameContextActorInformations.deserialize(self, b)

class GameRolePlayNamedActorInformations(GameRolePlayActorInformations):
	@staticmethod
	def getProtocolId():
		return 154

	def deserialize(self, b):
		GameRolePlayActorInformations.deserialize(self, b)

		self.name = b.readUTF()

class GameRolePlayHumanoidInformations(GameRolePlayNamedActorInformations):
	@staticmethod
	def getProtocolId():
		return 159

	def deserialize(self, b):
		GameRolePlayNamedActorInformations.deserialize(self, b)

		humanType = b.readUnsignedShort()
		if(humanType == HumanInformations.getProtocolId()):
			self.humanoidInfo = HumanInformations().deserialize(b)
		elif(humanType == HumanWithGuildInformations.getProtocolId()):
			self.humanoidInfo = HumanWithGuildInformations().deserialize(b)
		else:
			raise UnknowHumanType(humanType)

class GameRolePlayCharacterInformations(GameRolePlayHumanoidInformations):
	@staticmethod
	def getProtocolId():
		return 36

	def deserialize(self, b):
		GameRolePlayHumanoidInformations.deserialize(self, b)

		self.alignmentInfo = ActorAlignmentInformations().deserialize(b)

class EntityLook(object):
	@staticmethod
	def getProtocolId():
		return 55

	def deserialize(self, b):
		self.bonesId = b.readShort()

		self.skins = list()
		nbSkin = b.readUnsignedShort()
		for i in range(0, nbSkin):
			skin = b.readShort()
			self.skins.append(skin)

		self.indexedColors = list()
		nbIndexedColor = b.readUnsignedShort()
		for i in range(0, nbIndexedColor):
			indexedColor = b.readInt()
			self.indexedColors.append(indexedColor)

		self.scales = list()
		nbScale = b.readUnsignedShort()
		for i in range(0, nbScale):
			scale = b.readShort()
			self.scales.append(scale)

		self.subentities = list()
		nbSubenrity = b.readUnsignedShort()
		for i in range(0, nbSubenrity):
			subentity = SubEntity().deserialize(b)
			self.subentities.append(subentity)

class SubEntity(object):
	@staticmethod
	def getProtocolId():
		return 54

	def deserialize(self, b):
		self.bindingPointCategory = b.readByte()
		self.bindingPointIndex = b.readByte()
		self.subentityLook = EntityLook().deserialize(b)

class EntityDispositionInformations(object):
	@staticmethod
	def getProtocolId():
		return 60

	def deserialize(self, b):
		self.cellId = b.readShort()
		self.direction = b.readByte()

class HumanInformations(object):
	@staticmethod
	def getProtocolId():
		return 157

	def deserialize(self, b):
		self.followingCharactersLook = list()
		nbFollowingCharacter = b.readUnsignedShort()
		for i in range(0, nbFollowingCharacter):
			look = EntityLook().deserialize(b)
			self.followingCharactersLook.append(look)

		self.emoteId = b.readByte()
		self.emoteEndTime = b.readUnsignedShort()

		self.restrictions = ActorRestrictionsInformations().deserialize(b)

		self.titleId = b.readShort()
		self.titleParam = b.readUTF()

class HumanWithGuildInformations(HumanInformations):
	@staticmethod
	def getProtocolId():
		return 153

	def deserialize(self, b):
		HumanInformations.deserialize(self, b)
		self.guildInfo = GuildInformations().deserialize(b)

class ActorRestrictionsInformations(object):
	@staticmethod
	def getProtocolId():
		return 204

	def deserialize(self, b):
		byte1 = b.readByte()
		self.cantBeAggressed = (byte1 & 0x01)
		self.cantBeChallenged = (byte1 & 0x02)
		self.cantTrade = (byte1 & 0x04)
		self.cantBeAttackedByMutant = (byte1 & 0x08)
		self.cantRun = (byte1 & 0x10)
		self.forceSlowWalk = (byte1 & 0x20)
		self.cantMinimize = (byte1 & 0x40)
		self.cantMove = (byte1 & 0x80)
		
		byte2 = b.readByte()
		self.cantAggress = (byte2 & 0x01)
		self.cantChallenge = (byte2 & 0x02)
		self.cantExchange = (byte2 & 0x04)
		self.cantAttack = (byte2 & 0x08)
		self.cantChat = (byte2 & 0x10)
		self.cantBeMerchant = (byte2 & 0x20)
		self.cantUseObject = (byte2 & 0x40)
		self.cantUseTaxCollector = (byte2 & 0x80)
		
		byte3 = b.readByte()
		self.cantUseInteractive = (byte3 & 0x01)
		self.cantSpeakToNPC = (byte3 & 0x02)
		self.cantChangeZone = (byte3 & 0x04)
		self.cantAttackMonster = (byte3 & 0x08)
		self.cantWalk8Directions = (byte3 & 0x10)

class ActorAlignmentInformations(object):
	@staticmethod
	def getProtocolId():
		return 201

	def deserialize(self, b):
		self.alignmentSide = b.readByte()
		self.alignmentValue = b.readByte()
		self.alignmentGrade = b.readByte()
		self.dishonor = b.readUnsignedShort()
		self.characterPower = b.readInt()

class GameRolePlayGroupMonsterInformations(GameRolePlayActorInformations):
	@staticmethod
	def getProtocolId():
		return 160

	def deserialize(self, b):
		GameRolePlayActorInformations.deserialize(self, b)

		self.mainCreatureGenericId = b.readInt()
		self.mainCreatureGrade = b.readByte()

		self.underlings = list()
		nbUnderlings = b.readUnsignedShort()
		for i in range(0, nbUnderlings):
			underling = MonsterInGroupInformations().deserialize(b)
			self.underlings.append(underling)

		self.ageBonus = b.readShort()
		self.alignmentSize = b.readByte()

class MonsterInGroupInformations(object):
	@staticmethod
	def getProtocolId():
		return 144

	def deserialize(self, b):
		self.creatureGenericId = b.readInt()
		self.grade = b.readByte()

		self.look = EntityLook().deserialize(b)

class GameRolePlayTaxColectorInformations(GameRolePlayActorInformations):
	@staticmethod
	def getProtocolId():
		return 148

	def deserialize(self, b):
		GameRolePlayActorInformations.deserialize(self, b)

		self.firstNameId = b.readShort()
		self.lastNameId = b.readShort()
		self.guildIdentity = GuildInformations().deserialize(b)
		self.guildLevel = b.readUnsignedByte()
		self.taxCollectorAttack = b.readInt()

class GameRolePlayPrismInformations(GameRolePlayActorInformations):
	@staticmethod
	def getProtocolId():
		return 161

	def deserialize(self, b):
		GameRolePlayActorInformations.deserialize(self, b)

		self.alignInfos = ActorAlignmentInformations().deserialize(b)

class GameRolePlayNpcInformations(GameRolePlayActorInformations):
	@staticmethod
	def getProtocolId():
		return 156

	def deserialize(self, b):
		GameRolePlayActorInformations.deserialize(self, b)

		self.npcId = b.readShort()
		self.sex = b.readBoolean()
		self.specialArtworkId = b.readShort()
		self.canGiveQuest = b.readBoolean()

class GameRolePlayMerchantInformations(GameRolePlayNamedActorInformations):
	@staticmethod
	def getProtocolId():
		return 129

	def deserialize(self, b):
		GameRolePlayNamedActorInformations.deserialize(self, b)

		self.sellType = b.readInt()

class GameRolePlayMerchantWithGuildInformations(GameRolePlayMerchantInformations):
	@staticmethod
	def getProtocolId():
		return 146

	def deserialize(self, b):
		GameRolePlayMerchantInformations.deserialize(self, b)

		self.guildInfos = GuildInformations().deserialize(b)

class GameRolePlayMountInformations(GameRolePlayNamedActorInformations):
	@staticmethod
	def getProtocolId():
		return 180

	def deserialize(self, b):
		GameRolePlayNamedActorInformations.deserialize(self, b)

		self.ownerName = b.readUTF()
		self.level = b.readUnsignedByte()

class InteractiveElement(object):
	@staticmethod
	def getProtocolId():
		return 80

	def deserialize(self, b):
		self.elementId = b.readInt()
		self.elementTypeId = b.readInt()

		self.enabledSkills = list()
		nbEnabledSkill = b.readUnsignedShort()
		for i in range(0, nbEnabledSkill):
			enabledSkillType = b.readUnsignedShort()

			enabledSkill = 0
			if(enabledSkillType == InteractiveElementSkill.getProtocolId()):
				enabledSkill = InteractiveElementSkill().deserialize(b)
			else:
				raise UnknowSkillType(enabledSkillType)

			self.enabledSkills.append(enabledSkill)

		self.disabledSkills = list()
		nbDisabledSkill = b.readUnsignedShort()
		for i in range(0, nbDisabledSkill):
			disabledSkillType = b.readUnsignedShort()

			disabledSkill = 0
			if(disabledSkillType == InteractiveElementSkill.getProtocolId()):
				disabledSkill = InteractiveElementSkill().deserialize(b)
			else:
				raise UnknowSkillType(disabledSkillType)

			self.disabledSkills.append(disabledSkill)
			

class InteractiveElementSkill(object):
	@staticmethod
	def getProtocolId():
		return 219

	def deserialize(self, b):
		self.skillId = b.readInt()
		self.skillInstanceUid = b.readInt()

class InteractiveElementNamedSkill(InteractiveElementSkill):
	@staticmethod
	def getProtocolId():
		return 220

	def deserialize(self, b):
		InteractiveElementSkill.deserialize(self, b)

		self.nameId = b.readInt()

class StatedElement(object):
	@staticmethod
	def getProtocolId():
		return 108

	def deserialize(self, b):
		self.elementId = b.readInt()
		self.elementCellId = b.readShort()
		self.elementState = b.readInt()

class MapObstacle(object):
	@staticmethod
	def getProtocolId():
		return 200

	def deserialize(self, b):
		self.obstacleCellId = b.readShort()
		self.state = b.readByte()

class FightCommonInformations(object):
	@staticmethod
	def getProtocolId():
		return 43

	def deserialize(self, b):
		self.fightId = b.readInt()
		self.fightType = b.readByte()

		self.fightTeams = list()
		nbFightTeam = b.readUnsignedShort()
		for i in range(0, nbFightTeam):
			fightTeamType = b.readUnsignedShort()

			fightTeam = 0
			if(fightTeamType == FightTeamInformations.getProtocolId()):
				fightTeam = FightTeamInformations().deserialize(b)
			else:
				raise UnknowFightTeamType(fightTeamType)

			self.fightTeams.append(fightTeam)

		self.fightTeamPositions = list()
		nbFightTeamPosition = b.readUnsignedShort()
		for i in range(0, nbFightTeamPosition):
			self.fightTeamPositions.append(b.readShort())

		self.fightTeamOptions = list()
		nbFightTeamOption = b.readUnsignedShort()
		for i in range(0, nbFightTeamOption):
			fightTeamOption = FightOptionsInformations().deserialize(b)
			self.fightTeamOptions.append(fightTeamOption)

class AbstractFightTeamInformations(object):
	@staticmethod
	def getProtocolId():
		return 116

	def deserialize(self, b):
		self.teamId = b.readByte()
		self.leaderId = b.readInt()
		self.teamSide = b.readByte()
		self.teamTypeId = b.readByte()

class FightTeamInformations(AbstractFightTeamInformations):
	@staticmethod
	def getProtocolId():
		return 33

	def deserialize(self, b):
		AbstractFightTeamInformations.deserialize(self, b)

		self.teamMembers = list()
		nbTeamMember = b.readUnsignedShort()
		for i in range(0, nbTeamMember):
			teamMemberType = b.readUnsignedShort()

			teamMember = 0
			if(teamMemberType == FightTeamMemberCharacterInformations.getProtocolId()):
				teamMember = FightTeamMemberCharacterInformations().deserialize(b)
			elif(teamMemberType == FightTeamMemberMonsterInformations.getProtocolId()):
				teamMember = FightTeamMemberMonsterInformations().deserialize(b)
			else:
				raise UnknowTeamMemberType(teamMemberType)

			self.teamMembers.append(teamMember)
		
class FightTeamMemberInformations(object):
	@staticmethod
	def getProtocolId():
		return 44

	def deserialize(self, b):
		self.id = b.readInt()

class FightTeamMemberCharacterInformations(FightTeamMemberInformations):
	@staticmethod
	def getProtocolId():
		return 13

	def deserialize(self, b):
		FightTeamMemberInformations.deserialize(self, b)

		self.name = b.readUTF()
		self.level = b.readShort()

class FightTeamMemberMonsterInformations(FightTeamMemberInformations):
	@staticmethod
	def getProtocolId():
		return 6

	def deserialize(self, b):
		FightTeamMemberInformations.deserialize(self, b)

		self.monsterId = b.readInt()
		self.grade = b.readByte()

class FightOptionsInformations(object):
	@staticmethod
	def getProtocolId():
		return 20

	def deserialize(self, b):
		byte1 = b.readByte()
		self.isSecret = byte1 & 0x01
		self.isRestrictedToPartyOnly = byte1 & 0x02
		self.isClosed = byte1 & 0x04
		self.isAskingForHelp = byte1 & 0x08

class BasicNoOperationMessage(object):
	@staticmethod
	def getProtocolId():
		return 176

	def deserialize(self, b):
		pass

class BasicLatencyStatsRequestMessage(object):
	@staticmethod
	def getProtocolId():
		return 5816

	def deserialize(self, b):
		pass
