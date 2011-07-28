#!/usr/bin/python

import sys
import traceback

from dofussniff.pcolors import printRed, printBlue, printGreen
from dofussniff.buffer import BufferToSmall, Buffer
from dofussniff.monster import Monsters, Monster
from dofussniff.i18nfileaccessor import I18nFileAccessor

####################################################
#
#  Exceptions
#
####################################################

class MessageToShort(Exception):
	def __init__(self, value=None):
		self.parameter = value

	def __str__(self):
		return repr(self.parameter)

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

class UnknowDispositionType(Exception):
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

class UnknowEffectType(Exception):
	def __init__(self, value):
		self.parameter = value

	def __str__(self):
		return repr(self.parameter)

####################################################
#
#  Deserialization
#
####################################################

class DofusSniff(object):
	def __init__(self):
		self.b = Buffer()
		self.monsters = Monsters("/home/heero/src/jeux/dofus/Dofus/share/data/common/Monsters.d2o")
		self.i18n_fr = I18nFileAccessor("/home/heero/src/jeux/dofus/Dofus/share/data/i18n/i18n_fr.d2i")

	def decode(self, string):
		self.b.addInfos(string)

		while(self.b.getSize() > self.b.getCursor()):
			try:
				self.deserialize()
			except MessageToShort:

				# Don't wait too long
				if(self.b.discardReadAndSaveUnread() >= 3):
					self.b.reset()
				break
			except UnknowMessage as exp:
				printRed("Unknow packet type: {}\n".format(exp))
				printRed("info restantes: {}\n".format(
					self.b.getSize() - self.b.getCursor()
				))

				self.b.reset()
				break
			except StopException:

				self.b.reset()
				break
			except:
				print "Exception in user code:"
				print '-'*60
				traceback.print_exc(file=sys.stdout)
				print '-'*60

				self.b.reset()
				break

	def deserialize(self):
		var1 = self.b.readUnsignedShort()
		msgId = var1>>2
		sizeLen = var1 & 0x03
	
		msgSize = 0
		if(sizeLen == 0):
			msgSize = 0
		elif(sizeLen == 1):
			msgSize = self.b.readUnsignedByte()
		elif(sizeLen == 2):
			msgSize = self.b.readUnsignedShort()
		else:
			printRed("wrong size {}\n".format(sizeLen))
			raise StopException()

		if(msgSize > self.b.getSize()):
			#printGreen("size: {}, cursor: {}\n".format(b.getSize(), b.getCursor()))
			if(sizeLen == 1):
				self.b.moveCursor(-3)
			elif(sizeLen == 2):
				self.b.moveCursor(-4)

			#printGreen("size: {}, cursor: {}\n".format(b.getSize(), b.getCursor()))
			printRed("message too short (id: {}) {} > {}\n".format(
				msgId, msgSize, self.b.getSize()
			))
			raise MessageToShort()

		if(msgId == MapComplementaryInformationsDataMessage.getProtocolId()):
			printBlue("[new map]\n")

			self.infos = MapComplementaryInformationsDataMessage()
			self.infos.deserialize(self.b)
		elif(msgId == BasicNoOperationMessage.getProtocolId()):
			self.basicBNOM = BasicNoOperationMessage()
			self.basicBNOM.deserialize(self.b)
		elif(msgId == BasicLatencyStatsRequestMessage.getProtocolId()):
			self.basicLSRM = BasicLatencyStatsRequestMessage()
			self.basicLSRM.deserialize(self.b)
		elif(msgId == NotificationListMessage.getProtocolId()):
			self.notiLM = NotificationListMessage()
			self.notiLM.deserialize(self.b)
		elif(msgId == CharacterSelectedSuccessMessage.getProtocolId()):
			self.characterSSM = CharacterSelectedSuccessMessage()
			self.characterSSM.deserialize(self.b)
		elif(msgId == InventoryContentAndPresetMessage.getProtocolId()):
			self.inventoryCAPM = InventoryContentAndPresetMessage()
			self.inventoryCAPM.deserialize(self.b)

			objs = self.inventoryCAPM.objects
			for obj in objs:
				if(obj.objectGID == 10418):
					for effect in obj.effects:
						monster = self.monsters.getObj(effect.diceConst)
						if(monster._race == 78):
							printBlue("{}\n".format(self.i18n_fr.getText(monster._nameId)))
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
				house = HouseInformations()
			elif(houseType == HouseInformationsExtended.getProtocolId()):
				house = HouseInformationsExtended()
			else:
				raise UnknowHouseType(houseType)

			house.deserialize(b)
			self.houses.append(house)

		# Actors
		self.actors = list()

		nbActor = b.readUnsignedShort()
		for i in range(0, nbActor):
			actorType = b.readUnsignedShort()
			actor = 0

			if(actorType == GameRolePlayCharacterInformations.getProtocolId()):
				actor = GameRolePlayCharacterInformations()
			elif(actorType == GameRolePlayGroupMonsterInformations.getProtocolId()):
				actor = GameRolePlayGroupMonsterInformations()
			elif(actorType == GameRolePlayTaxColectorInformations.getProtocolId()):
				actor = GameRolePlayTaxColectorInformations()
			elif(actorType == GameRolePlayPrismInformations.getProtocolId()):
				actor = GameRolePlayPrismInformations()
			elif(actorType == GameRolePlayNpcInformations.getProtocolId()):
				actor = GameRolePlayNpcInformations()
			elif(actorType == GameRolePlayMerchantWithGuildInformations.getProtocolId()):
				actor = GameRolePlayMerchantWithGuildInformations()
			elif(actorType == GameRolePlayMerchantInformations.getProtocolId()):
				actor = GameRolePlayMerchantInformations()
			elif(actorType == GameRolePlayMountInformations.getProtocolId()):
				actor = GameRolePlayMountInformations()
			else:
				raise UnknowActorType(actorType)

			actor.deserialize(b)
			self.actors.append(actor)

		# Interactive elements
		self.interactiveElements = list()

		nbInteractiveElement = b.readUnsignedShort()
		for i in range(0, nbInteractiveElement):
			interactiveElement = InteractiveElement()
			interactiveElement.deserialize(b)
			self.interactiveElements.append(interactiveElement)

		# Stated elements
		self.statedElements = list()

		nbStatedElement = b.readUnsignedShort()
		for i in range(0, nbStatedElement):
			statedElement = StatedElement()
			statedElement.deserialize(b)
			self.statedElements.append(statedElement)

		# Map obstacles
		self.mapObstacles = list()

		nbMapObstacle = b.readUnsignedShort()
		for i in range(0, nbMapObstacle):
			mapObstacle = MapObstacle()
			mapObstacle.deserialize(b)
			self.mapObstacles.append(mapObstacle)

		# Fights
		self.fights = list()

		nbFight = b.readUnsignedShort()
		for i in range(0, nbFight):
			fight = FightCommonInformations()
			fight.deserialize(b)
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

		self.guildInfo = GuildInformations()
		self.guildInfo.deserialize(b)

class GuildInformations(object):
	@staticmethod
	def getProtocolId():
		return 127

	def deserialize(self, b):
		self.guildId = b.readInt()
		self.guildName = b.readUTF()
		self.guildEmblem = GuildEmblem()
		self.guildEmblem.deserialize(b)

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
		self.look = EntityLook()
		self.look.deserialize(b)

		dispositionType = b.readUnsignedShort()
		if(dispositionType == EntityDispositionInformations.getProtocolId()):
			self.disposition = EntityDispositionInformations()
		else:
			raise UnknowDispositionType(dispositionType)

		self.disposition.deserialize(b)

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
			self.humanoidInfo = HumanInformations()
		elif(humanType == HumanWithGuildInformations.getProtocolId()):
			self.humanoidInfo = HumanWithGuildInformations()
		else:
			raise UnknowHumanType(humanType)

		self.humanoidInfo.deserialize(b)

class GameRolePlayCharacterInformations(GameRolePlayHumanoidInformations):
	@staticmethod
	def getProtocolId():
		return 36

	def deserialize(self, b):
		GameRolePlayHumanoidInformations.deserialize(self, b)

		self.alignmentInfo = ActorAlignmentInformations()
		self.alignmentInfo.deserialize(b)

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
			subentity = SubEntity()
			subentity.deserialize(b)
			self.subentities.append(subentity)

class SubEntity(object):
	@staticmethod
	def getProtocolId():
		return 54

	def deserialize(self, b):
		self.bindingPointCategory = b.readByte()
		self.bindingPointIndex = b.readByte()
		self.subentityLook = EntityLook()
		self.subentityLook.deserialize(b)

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
			look = EntityLook()
			look.deserialize(b)
			self.followingCharactersLook.append(look)

		self.emoteId = b.readByte()
		self.emoteEndTime = b.readUnsignedShort()

		self.restrictions = ActorRestrictionsInformations()
		self.restrictions.deserialize(b)

		self.titleId = b.readShort()
		self.titleParam = b.readUTF()

class HumanWithGuildInformations(HumanInformations):
	@staticmethod
	def getProtocolId():
		return 153

	def deserialize(self, b):
		HumanInformations.deserialize(self, b)
		self.guildInfo = GuildInformations()
		self.guildInfo.deserialize(b)

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
			underling = MonsterInGroupInformations()
			underling.deserialize(b)
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

		self.look = EntityLook()
		self.look.deserialize(b)

class GameRolePlayTaxColectorInformations(GameRolePlayActorInformations):
	@staticmethod
	def getProtocolId():
		return 148

	def deserialize(self, b):
		GameRolePlayActorInformations.deserialize(self, b)

		self.firstNameId = b.readShort()
		self.lastNameId = b.readShort()
		self.guildIdentity = GuildInformations()
		self.guildIdentity.deserialize(b)
		self.guildLevel = b.readUnsignedByte()
		self.taxCollectorAttack = b.readInt()

class GameRolePlayPrismInformations(GameRolePlayActorInformations):
	@staticmethod
	def getProtocolId():
		return 161

	def deserialize(self, b):
		GameRolePlayActorInformations.deserialize(self, b)

		self.alignInfos = ActorAlignmentInformations()
		self.alignInfoso.deserialize(b)

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

		self.guildInfos = GuildInformations()
		self.guildInfos.deserialize(b)

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
				enabledSkill = InteractiveElementSkill()
			else:
				raise UnknowSkillType(enabledSkillType)

			enabledSkill.deserialize(b)
			self.enabledSkills.append(enabledSkill)

		self.disabledSkills = list()
		nbDisabledSkill = b.readUnsignedShort()
		for i in range(0, nbDisabledSkill):
			disabledSkillType = b.readUnsignedShort()

			disabledSkill = 0
			if(disabledSkillType == InteractiveElementSkill.getProtocolId()):
				disabledSkill = InteractiveElementSkill()
			else:
				raise UnknowSkillType(disabledSkillType)

			disabledSkill.deserialize(b)
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
				fightTeam = FightTeamInformations()
			else:
				raise UnknowFightTeamType(fightTeamType)

			fightTeam.deserialize(b)
			self.fightTeams.append(fightTeam)

		self.fightTeamPositions = list()
		nbFightTeamPosition = b.readUnsignedShort()
		for i in range(0, nbFightTeamPosition):
			self.fightTeamPositions.append(b.readShort())

		self.fightTeamOptions = list()
		nbFightTeamOption = b.readUnsignedShort()
		for i in range(0, nbFightTeamOption):
			fightTeamOption = FightOptionsInformations()
			fightTeamOption.deserialize(b)
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
				teamMember = FightTeamMemberCharacterInformations()
			elif(teamMemberType == FightTeamMemberMonsterInformations.getProtocolId()):
				teamMember = FightTeamMemberMonsterInformations()
			else:
				raise UnknowTeamMemberType(teamMemberType)

			teamMember.deserialize(b)
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

class NotificationListMessage(object):
	@staticmethod
	def getProtocolId():
		return 6087

	def deserialize(self, b):
		self.flags = list()

		nbFlag = b.readUnsignedShort()
		for i in range(0, nbFlag):
			self.flags.append(b.readInt())

class CharacterSelectedSuccessMessage(object):
	@staticmethod
	def getProtocolId():
		return 153

	def deserialize(self, b):
		self.infos = CharacterBaseInformations()
		self.infos.deserialize(b)

class CharacterMinimalInformations(object):
	@staticmethod
	def getProtocolId():
		return 110

	def deserialize(self, b):
		self.id = b.readInt()
		self.level = b.readUnsignedByte()
		self.name = b.readUTF()

class CharacterMinimalPlusLookInformations(CharacterMinimalInformations):
	@staticmethod
	def getProtocolId():
		return 163

	def deserialize(self, b):
		self.infos = CharacterMinimalInformations.deserialize(self, b)
		self.look = EntityLook()
		self.look.deserialize(b)

class CharacterBaseInformations(CharacterMinimalPlusLookInformations):
	@staticmethod
	def getProtocolId():
		return 45

	def deserialize(self, b):
		CharacterMinimalPlusLookInformations.deserialize(self, b)

		self.breed = b.readByte()
		self.sex = b.readBoolean()

class InventoryContentMessage(object):
	@staticmethod
	def getProtocolId():
		return 3016

	def deserialize(self, b):
		self.objects = list()
		nbObject = b.readUnsignedShort()
		printBlue("nbObject: {}\n".format(nbObject))
		for i in range(0, nbObject):
			objectItem = ObjectItem()
			objectItem.deserialize(b)
			self.objects.append(objectItem)

		self.kamas = b.readInt()
		printGreen("kama: {}\n".format(self.kamas))

class InventoryContentAndPresetMessage(InventoryContentMessage):
	@staticmethod
	def getProtocolId():
		return 6162

	def deserialize(self, b):
		InventoryContentMessage.deserialize(self, b)

		self.presets = list()
		nbPreset = b.readUnsignedShort()
		for i in range(0, nbPreset):
			preset = Preset()
			preset.deserialize(b)
			self.presets.append(preset)

class Preset(object):
	@staticmethod
	def getProtocolId():
		return 355

	def deserialize(self, b):
		self.presetId = b.readByte()
		self.symbolId = b.readByte()
		self.mount = b.readBoolean()

		self.objects = list()
		nbObject = b.readUnsignedShort()
		for i in range(0, nbObject):
			presetItem = PresetItem()
			presetItem.deserialize(b)
			self.objects.append(presetItem)

class PresetItem(object):
	@staticmethod
	def getProtocolId():
		return 354

	def deserialize(self, b):
		self.position = b.readUnsignedByte()
		self.objGid = b.readInt()
		self.objUid = b.readInt()

class Item(object):
	@staticmethod
	def getProtocolId():
		return 7

	def deserialize(self, b):
		pass

class ObjectItem(Item):
	@staticmethod
	def getProtocolId():
		return 37

	def deserialize(self, b):
		Item.deserialize(self, b)

		self.position = b.readUnsignedByte()
		self.objectGID = b.readShort()
		self.powerRate = b.readShort()
		self.overMax = b.readBoolean()

		self.effects = list()
		nbEffect = b.readUnsignedShort()
		printGreen("nbEffect: {}, position: {}, GID: {}, Rate {}, overMax: {}, ".format(nbEffect, self.position, self.objectGID, self.powerRate, self.overMax))
		for i in range(0, nbEffect):
			effectType = b.readUnsignedShort()

			effect = 0
			if(effectType == ObjectEffect.getProtocolId()):
				printRed(", Effect")
				effect = ObjectEffect()
			elif(effectType == ObjectEffectInteger.getProtocolId()):
				printRed(", EffectInt")
				effect = ObjectEffectInteger()
			elif(effectType == ObjectEffectCreature.getProtocolId()):
				printRed(", EffectCrea")
				effect = ObjectEffectCreature()
			elif(effectType == ObjectEffectDate.getProtocolId()):
				printRed(", EffectDate")
				effect = ObjectEffectDate()
			elif(effectType == ObjectEffectDice.getProtocolId()):
				printRed(", EffectDice")
				effect = ObjectEffectDice()
			elif(effectType == ObjectEffectDuration.getProtocolId()):
				printRed(", EffectDuration")
				effect = ObjectEffectDuration()
			elif(effectType == ObjectEffectString.getProtocolId()):
				printRed(", EffectStr")
				effect = ObjectEffectString()
			elif(effectType == ObjectEffectLadder.getProtocolId()):
				printRed(", EffectLadder")
				effect = ObjectEffectLadder()
			elif(effectType == ObjectEffectMinMax.getProtocolId()):
				printRed(", EffectMinMax")
				effect = ObjectEffectMinMax()
			else:
				raise UnknowEffectType(effectType)

			effect.deserialize(b)
			self.effects.append(effect)

		self.objectUID = b.readInt()
		self.quantity = b.readInt()
		printGreen("UID: {}, quantity: {}\n".format(self.objectUID, self.quantity))

class ObjectEffect(object):
	@staticmethod
	def getProtocolId():
		return 76

	def deserialize(self, b):
		self.actionId = b.readShort()

class ObjectEffectInteger(ObjectEffect):
	@staticmethod
	def getProtocolId():
		return 70

	def deserialize(self, b):
		ObjectEffect.deserialize(self, b)

		self.value = b.readShort()

class ObjectEffectCreature(ObjectEffect):
	@staticmethod
	def getProtocolId():
		return 71

	def deserialize(self, b):
		ObjectEffect.deserialize(self, b)

		self.monsterFamilyId = b.readShort()

class ObjectEffectDate(ObjectEffect):
	@staticmethod
	def getProtocolId():
		return 72

	def deserialize(self, b):
		ObjectEffect.deserialize(self, b)

		self.year = b.readShort()
		self.month = b.readShort()
		self.day = b.readShort()
		self.hour = b.readShort()
		self.minute = b.readShort()

class ObjectEffectDice(ObjectEffect):
	@staticmethod
	def getProtocolId():
		return 73

	def deserialize(self, b):
		ObjectEffect.deserialize(self, b)

		self.diceNum = b.readShort()
		self.diceSide = b.readShort()
		self.diceConst = b.readShort()

class ObjectEffectString(ObjectEffect):
	@staticmethod
	def getProtocolId():
		return 74

	def deserialize(self, b):
		ObjectEffect.deserialize(self, b)

		self.value = b.readUTF()
		printBlue(", string: {}".format(self.value))

class ObjectEffectDuration(ObjectEffect):
	@staticmethod
	def getProtocolId():
		return 75

	def deserialize(self, b):
		ObjectEffect.deserialize(self, b)

		self.day = b.readShort()
		self.hour = b.readShort()
		self.minute = b.readShort()

class ObjectEffectLadder(ObjectEffect):
	@staticmethod
	def getProtocolId():
		return 81

	def deserialize(self, b):
		ObjectEffect.deserialize(self, b)

		self.monsterCount = b.readInt()

class ObjectEffectMinMax(ObjectEffect):
	@staticmethod
	def getProtocolId():
		return 82

	def deserialize(self, b):
		ObjectEffect.deserialize(self, b)

		self.min = b.readShort()
		self.max = b.readShort()

class ObjectEffectMount(ObjectEffect):
	@staticmethod
	def getProtocolId():
		return 179

	def deserialize(self, b):
		ObjectEffect.deserialize(self, b)

		self.mountId = b.readInt()
		self.date = b.readDouble()
		self.modelId = b.readShort()
