import random
import sqlite3

XP_TABLE = {1: 500, 2: 1000, 3: 1500, 4: 2000, 5: 2500, 6: 3000, 7: 3500, 8: 4000, 9: 4500, 10: 5000, 11: 5500,
            12: 6000, 13: 6500, 14: 7000, 15: 7500, 16: 8000, 17: 8500, 18: 9000, 19: 9500, 20: 10000, 21: 10000,
            22: 10000, 23: 10000, 24: 10000, 25: 10000, 26: 10000, 27: 10000, 28: 10000, 29: 10000, 30: 10000,
            31: 10000, 32: 10000, 33: 10000, 34: 10000, 35: 10000, 36: 10000, 37: 10000, 38: 10000, 39: 10000,
            40: 10000, 41: 10000, 42: 10000, 43: 10000, 44: 10000, 45: 10000, 46: 10000, 47: 10000, 48: 10000,
            49: 10000}
OBJ = sqlite3.connect("BaseObjects.db")
OBJ_CUR = OBJ.cursor()


class BaseCharacter:
    def __init__(self, characteristics):
        self.id = characteristics["id"]
        self.name = characteristics["name"]
        self.available = characteristics["available"]
        self.character_init(characteristics)

    def character_init(self, characteristics):
        self.strength = characteristics["strength"]
        self.perception = characteristics["perception"]
        self.endurance = characteristics["endurance"]
        self.charisma = characteristics["charisma"]
        self.intelligence = characteristics["intelligence"]
        self.agility = characteristics["agility"]
        self.luck = characteristics["luck"]

        self.lvl = characteristics["lvl"]
        self.xp = characteristics["xp"]

        self.attack_type = characteristics["attack_type"]

        self.spec_attack_modifiers = characteristics["phys_spec_attack_modifier"], characteristics[
            "mag_spec_attack_modifier"]
        self.spec_attack_recovery = characteristics["spec_attack_recovery"]

        self.base_stats = dict()
        self.base_stats["hp"] = 3600
        self.base_stats["phys_atk"] = 100
        self.base_stats["mag_atk"] = 100
        self.base_stats["phys_def"] = 100
        self.base_stats["mag_def"] = 100
        self.base_stats["crit_chance"] = 10
        self.base_stats["crit_modifier"] = 150
        self.base_stats["accuracy"] = 10
        self.base_stats["dodge"] = 10

        self.equip_weapon(characteristics["weapon_id"])
        self.equip_armor(characteristics["armor_id"])
        self.calculate_characteristics()

    def calculate_characteristics(self):  # ?????????????? ???????????????????????????? ???????????????????????? ????????????, special ?? ??????????????????
        self.stats = dict()
        # ???????????????????? ?????????????????? ??????????????????????????
        self.stats["max_hp"] = self.base_stats["hp"] + self.base_stats["hp"] * (self.strength / 20) + self.base_stats[
            "hp"] * (self.endurance / 10)
        self.stats["phys_atk"] = self.base_stats["phys_atk"] + self.base_stats["phys_atk"] * (self.strength / 10) + \
                                 self.base_stats["phys_atk"] * (self.agility / 10)
        self.stats["mag_atk"] = self.base_stats["mag_atk"] + self.base_stats["mag_atk"] * (self.intelligence / 10) + \
                                self.base_stats["mag_atk"] * (self.perception / 10)
        self.stats["phys_def"] = self.base_stats["phys_def"] + self.base_stats["phys_def"] * (self.endurance / 10)
        self.stats["mag_def"] = self.base_stats["mag_def"] + self.base_stats["mag_def"] * (self.intelligence / 10)
        self.stats["crit_chance"] = self.base_stats["crit_chance"] + self.agility * 1.5 + self.luck * 2
        self.stats["crit_modifier"] = self.base_stats["crit_modifier"] + self.agility * 5 + self.luck * 5
        self.stats["accuracy"] = self.base_stats["accuracy"] + self.perception * 2 + self.luck * 2
        self.stats["dodge"] = self.base_stats["dodge"] + self.agility * 2 + self.luck * 2
        # ?????????????????? ?????????? ???? ???????????? ?? ?????????????????? ???????????????? ???? ?????????? ?? ???????????? 
        for stat in self.stats.keys():
            self.stats[stat] *= int(1 + self.lvl / 25)
            if self.armor is not None:
                self.stats[stat] += self.armor.stat_boosts[stat]
            if self.weapon is not None:
                self.stats[stat] += self.weapon.stat_boosts[stat]

    def equip_armor(self, armor_id):
        if armor_id == 0:
            self.armor = None
        else:
            obj = OBJ_CUR.execute(f"SELECT * FROM items WHERE id='{armor_id}'").fetchone()
            item_char = ("id", "type", "name", "max_hp", "phys_atk", "mag_atk", "phys_def", "mag_def", "crit_chance",
                         "crit_modifier", "accuracy", "dodge")
            d = dict()
            for j in range(len(item_char)):
                d[item_char[j]] = obj[j]
            self.armor = Armor(d)

        if self.armor is not None:
            self.calculate_characteristics()

    def equip_weapon(self, weapon_id):
        if weapon_id == 0:
            self.weapon = None
        else:
            obj = OBJ_CUR.execute(f"SELECT * FROM items WHERE id='{weapon_id}'").fetchone()
            item_char = ("id", "type", "name", "max_hp", "phys_atk", "mag_atk", "phys_def", "mag_def", "crit_chance",
                         "crit_modifier", "accuracy", "dodge")
            d = dict()
            for j in range(len(item_char)):
                d[item_char[j]] = obj[j]
            self.weapon = Weapon(d)
        # if self.weapon is not None:
        #     self.calculate_characteristics()

    def level_up(self):
        if self.lvl == 50:
            return False
        if self.xp >= XP_TABLE[self.lvl]:
            self.xp -= XP_TABLE[self.lvl]
            self.lvl += 1
            self.calculate_characteristics()
            return True
        return False

    def attack(self, target) -> int:
        types = {"phys": (1, 0),
                 "mag": (0, 1),
                 "hybrid": (0.6, 0.6)
                 }
        phys_damage_modifier, mag_damage_modifier = types[self.attack_type]

        phys_damage = phys_damage_modifier * self.stats["phys_atk"]
        mag_damage = mag_damage_modifier * self.stats["mag_atk"]

        r = random.randint(0, 101)
        if r <= self.stats["crit_chance"]:
            phys_damage *= self.stats["crit_modifier"] / 100
            mag_damage *= self.stats["crit_modifier"] / 100

        phys_damage -= target.stats["phys_def"]
        mag_damage -= target.stats["mag_def"]

        mag_damage = max(0, mag_damage)
        phys_damage = max(0, phys_damage)

        total_damage = int(mag_damage + phys_damage)

        return total_damage

    def specattack(self, target):
        phys_damage_modifier, mag_damage_modifier = self.spec_attack_modifiers

        phys_damage = phys_damage_modifier * self.stats["phys_atk"]
        mag_damage = mag_damage_modifier * self.stats["mag_atk"]

        r = random.randint(0, 100)
        if r <= self.stats["crit_chance"]:
            phys_damage *= self.stats["crit_modifier"] / 100
            mag_damage *= self.stats["crit_modifier"] / 100

        phys_damage -= target.stats["phys_def"]
        mag_damage -= target.stats["mag_def"]

        mag_damage = max(0, mag_damage)
        phys_damage = max(0, phys_damage)

        total_damage = int(mag_damage + phys_damage)

        return total_damage


class BaseEnemy:
    def __init__(self, characteristics):
        self.id = characteristics["id"]
        self.name = characteristics["name"]
        self.character_init(characteristics)

    def character_init(self, characteristics):
        self.lvl = characteristics["lvl"]

        self.attack_type = characteristics["attack_type"]

        self.base_stats = dict()
        self.base_stats["max_hp"] = characteristics["max_hp"]
        self.base_stats["phys_atk"] = characteristics["phys_atk"]
        self.base_stats["mag_atk"] = characteristics["mag_atk"]
        self.base_stats["phys_def"] = characteristics["phys_def"]
        self.base_stats["mag_def"] = characteristics["mag_def"]
        self.base_stats["crit_chance"] = characteristics["crit_chance"]
        self.base_stats["crit_modifier"] = characteristics["crit_modifier"]
        self.base_stats["accuracy"] = characteristics["accuracy"]
        self.base_stats["dodge"] = characteristics["dodge"]

        self.xp_per_level = characteristics["xp_per_level"]

        self.calculate_characteristics()

    def attack(self, target) -> int:
        types = {"phys": (1, 0),
                 "mag": (0, 1),
                 "hybrid": (0.6, 0.6)
                 }
        phys_damage_modifier, mag_damage_modifier = types[self.attack_type]

        phys_damage = phys_damage_modifier * self.stats["phys_atk"]
        mag_damage = mag_damage_modifier * self.stats["mag_atk"]

        r = random.randint(0, 101)
        if r <= self.stats["crit_chance"]:
            phys_damage *= self.stats["crit_modifier"] / 100
            mag_damage *= self.stats["crit_modifier"] / 100

        phys_damage -= target.stats["phys_def"]
        mag_damage -= target.stats["mag_def"]

        mag_damage = max(0, mag_damage)
        phys_damage = max(0, phys_damage)

        total_damage = int(mag_damage + phys_damage)

        return total_damage

    def calculate_characteristics(self):
        self.stats = dict()
        for stat in self.base_stats.keys():
            self.stats[stat] = self.base_stats[stat] * int(1 + self.lvl / 25)


class EquipItem:
    def __init__(self, stats):
        self.id = stats["id"]
        self.name = stats["name"]
        self.stats_init(stats)

    def stats_init(self, stats):
        self.stat_boosts = dict()
        for stat in stats.keys():
            self.stat_boosts[stat] = stats[stat]


class Armor(EquipItem):
    def __init__(self, stats):
        super(Armor, self).__init__(stats)
        self.type = "armor"


class Weapon(EquipItem):
    def __init__(self, stats):
        super(Weapon, self).__init__(stats)
        self.type = "weapon"


class FightMember:
    def __init__(self, character):
        self.character = character
        if character is None:
            self.defeated = True
            self.made_move = True
        else:
            self.defeated = False
            self.made_move = False
            self.turns_before_spec_attack = 0
            self.character.stats["hp"] = self.character.stats["max_hp"]

# class Fight:
#     def __init__(self, command1: (list, tuple), command2: (list, tuple)):
#         self.commands = []
#         self.commands.append([FightMember(char) for char in command1])
#         self.commands.append([FightMember(char) for char in command2])
#         self.end = False
#         self.turn = 0
#
#     def make_move(self, n_actor, n_object, move_type):
#         actor, object = None, None
#         for char in self.commands[self.turn]:
#             if char.character.name == n_actor:
#                 actor = char
#                 break
#         for char in self.commands[abs(self.turn - 1)]:
#             if char.character.name == n_object:
#                 object = char
#                 break
#         if actor is None or object is None:
#             return "???????????? ???? ???????????????????????? ????????????????"
#
#         if move_type == "specattack":
#             if not actor.turns_before_spec_attack:
#                 damage = actor.character.specattack(object.character)
#                 actor.turns_before_spec_attack = actor.character.spec_attack_recovery
#
#         elif move_type == "attack":
#             damage = actor.character.attack(object.character)
#         if object.character.stats["hp"] <= 0:
#             object.defeated = True
#         actor.made_move = True
#         if self.check_win():
#             return "?????????? ??????"
#         return self.check_end_turn()
#
#     def check_end_turn(self):
#         if all([char.made_move for char in self.commands[self.turn]]):
#             self.turn = abs(self.turn - 1)
#             for char in self.commands[self.turn]:
#                 char.made_move = False
#                 char.turns_before_spec_attack -= 1
#             return "?????????? ????????"
#         return None
#
#     def check_win(self):
#         self.end = all([char.defeated for char in self.commands[abs(self.turn - 1)]])
