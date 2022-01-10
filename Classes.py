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

        self.Attack_type = characteristics["Attack_type"]

        self.Spec_Attack_Modifiers = characteristics["Phys_Spec_Attack_Modifier"], characteristics[
            "Mag_Spec_Attack_Modifier"]
        self.Spec_Attack_Recovery = characteristics["Spec_Attack_Recovery"]

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
        self.Stats["Max_HP"] = self.Base_Stats["HP"] + self.Base_Stats["HP"] * (self.Strength / 20) + self.Base_Stats[
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

    def Attack(self, target) -> int:
        types = {"Phys": (1, 0),
                 "Mag": (0, 1),
                 "Hybrid": (0.6, 0.6)
                 }
        phys_damage_modifier, mag_damage_modifier = types[self.Attack_type]

        phys_damage = phys_damage_modifier * self.Stats["Phys_Atk"]
        mag_damage = mag_damage_modifier * self.Stats["Mag_Atk"]

        r = random.randint(0, 101)
        if r <= self.Stats["Crit_Chance"]:
            phys_damage *= self.Stats["Crit_Modifier"] / 100
            mag_damage *= self.Stats["Crit_Modifier"] / 100

        phys_damage -= target.Stats["Phys_Def"]
        mag_damage -= target.Stats["Mag_Def"]

        mag_damage = max(0, mag_damage)
        phys_damage = max(0, phys_damage)

        total_damage = int(mag_damage + phys_damage)

        target.Stats["HP"] -= total_damage
        return total_damage

    def SpecAttack(self, target):
        phys_damage_modifier, mag_damage_modifier = self.Spec_Attack_Modifiers

        phys_damage = phys_damage_modifier * self.Stats["Phys_Atk"]
        mag_damage = mag_damage_modifier * self.Stats["Mag_Atk"]

        r = random.randint(0, 100)
        if r <= self.Stats["Crit_Chance"]:
            phys_damage *= self.Stats["Crit_Modifier"] / 100
            mag_damage *= self.Stats["Crit_Modifier"] / 100

        phys_damage -= target.Stats["Phys_Def"]
        mag_damage -= target.Stats["Mag_Def"]

        mag_damage = max(0, mag_damage)
        phys_damage = max(0, phys_damage)

        total_damage = int(mag_damage + phys_damage)

        target.Stats["HP"] -= total_damage
        return total_damage


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


class FightMember:
    def __init__(self, character: BaseCharacter):
        self.character = character
        self.defeated = False
        self.made_move = False
        self.turns_before_spec_attack = 0
        self.character.Stats["HP"] = self.character.Stats["Max_HP"]


class Fight:
    def __init__(self, command1: (list, tuple), command2: (list, tuple)):
        self.commands = []
        self.commands.append([FightMember(char) for char in command1])
        self.commands.append([FightMember(char) for char in command2])
        self.end = False
        self.turn = 0

    def make_move(self, n_actor, n_object, move_type):
        actor, object = None, None
        for char in self.commands[self.turn]:
            if char.character.name == n_actor:
                actor = char
                break
        for char in self.commands[abs(self.turn - 1)]:
            if char.character.name == n_object:
                object = char
                break
        if actor is None or object is None:
            return "Выбран не существующий персонаж"

        if move_type == "specattack":
            if not actor.turns_before_spec_attack:
                damage = actor.character.SpecAttack(object.character)
                actor.turns_before_spec_attack = actor.character.Spec_Attack_Recovery

        elif move_type == "attack":
            damage = actor.character.Attack(object.character)
        if object.character.Stats["HP"] <= 0:
            object.defeated = True
        actor.made_move = True
        if self.check_win():
            return "Конец боя"
        return self.check_end_turn()

    def check_end_turn(self):
        if all([char.made_move for char in self.commands[self.turn]]):
            self.turn = abs(self.turn - 1)
            for char in self.commands[self.turn]:
                char.made_move = False
                char.turns_before_spec_attack -= 1
            return "Конец хода"
        return None

    def check_win(self):
        self.end = all([char.defeated for char in self.commands[abs(self.turn - 1)]])
