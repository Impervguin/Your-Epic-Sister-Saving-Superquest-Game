import random

XP_TABLE = {1: 500, 2: 1000}  # Таблица требуемоего опыта для перехода новый уровень. заполнить позже


class BaseCharacter:
    def __init__(self, Characteristics):
        self.ID = Characteristics["ID"]
        self.Name = Characteristics["Name"]
        self.Character_init(Characteristics)

    def Character_init(self, characteristics):
        self.Strength = characteristics["Strength"]
        self.Perception = characteristics["Perception"]
        self.Endurance = characteristics["Endurance"]
        self.Charisma = characteristics["Charisma"]
        self.Intelligence = characteristics["Intelligence"]
        self.Agility = characteristics["Agility"]
        self.Luck = characteristics["Luck"]

        self.Level = characteristics["Level"]
        self.XP = characteristics["XP"]
        self.Attack_type = characteristics["Attack_type"]

        self.Base_Stats = dict()
        self.Base_Stats["HP"] = 3600
        self.Base_Stats["PHYS_Atk"] = 100
        self.Base_Stats["MAG_Atk"] = 100
        self.Base_Stats["PHYS_Def"] = 100
        self.Base_Stats["MAG_Def"] = 100
        self.Base_Stats["Crit_Chance"] = 10
        self.Base_Stats["Crit_Modifier"] = 150
        self.Base_Stats["Accuracy"] = 10
        self.Base_Stats["Dodge"] = 10

        self.Equip_armor(None)
        self.Equip_weapon(None)

    def Calculate_characteristics(self):  # считает характеристики относительно уровня, special и предметов
        self.Stats = dict()
        # Вычисление стартовых характеристик
        self.Stats["HP"] = self.Base_Stats["HP"] + self.Base_Stats["HP"] * (self.Strength / 20) + self.Base_Stats[
            "HP"] * (self.Endurance / 10)
        self.Stats["Phys_Atk"] = self.Base_Stats["Phys_Atk"] + self.Base_Stats["Phys_Atk"] * (self.Strength / 10) + \
                                 self.Base_Stats["Phys_Atk"] * (self.Agility / 10)
        self.Stats["Mag_Atk"] = self.Base_Stats["Mag_Atk"] + self.Base_Stats["Mag_Atk"] * (self.Intelligence / 10) + \
                                self.Base_Stats["Mag_Atk"] * (self.Perception / 10)
        self.Stats["Phys_Def"] = self.Base_Stats["Phys_Def"] + self.Base_Stats["Phys_Def"] * (self.Endurance / 10)
        self.Stats["Mag_Def"] = self.Base_Stats["Mag_Def"] + self.Base_Stats["Mag_Def"] * (self.Intelligence / 10)
        self.Stats["Crit_Chance"] = self.Base_Stats["Crit_Chance"] + self.Agility * 1.5 + self.Luck * 2
        self.Stats["Crit_Modifier"] = self.Base_Stats["Crit_Modifier"] + self.Agility * 5 + self.Luck * 5
        self.Stats["Accuracy"] = self.Base_Stats["Accuracy"] + self.Perception * 2 + self.Luck * 2
        self.Stats["Dodge"] = self.Base_Stats["Dodge"] + self.Agility * 2 + self.Luck * 2
        # Подгоняет статы по уровню и добавляет бонусные от брони и оружия 
        for stat in self.Stats.keys():
            self.Stats[stat] *= int(1 + self.Level / 25)
            self.Stats[stat] += self.armor.Stat_Boosts[stat]
            self.Stats[stat] += self.weapon.Stat_Boosts[stat]

    def Equip_armor(self, armor):
        if armor is None:
            armor = Armor()
        self.armor = armor
        self.Calculate_characteristics()

    def Equip_weapon(self, weapon):
        if weapon is None:
            weapon = Weapon()
        self.weapon = weapon
        self.Calculate_characteristics()

    def Level_up(self):
        if self.XP >= XP_TABLE[self.Level]:
            self.XP -= XP_TABLE[self.Level]
            self.Level += 1
            self.Calculate_characteristics()

    def Attack(self, target):
        pass


class EquipItem:
    def __init__(self, Stats):
        self.ID = Stats["ID"]
        self.Name = Stats["Name"]
        self.Stats_init(Stats)

    def Stats_init(self, Stats):
        self.Stat_Boosts = dict()
        for stat in Stats.keys():
            self.Stat_Boosts[stat] = Stats[stat]


class Armor(EquipItem):
    def __init__(self):
        super(Armor, self).__init__()
        self.Item_Class = "Armor"


class Weapon(EquipItem):
    def __init__(self):
        super(Weapon, self).__init__()
        self.Item_Class = "Weapon"
