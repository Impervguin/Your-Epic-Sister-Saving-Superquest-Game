import random

XP_TABLE = {1: 500, 2: 1000}  # Таблица требуемоего опыта для перехода новый уровень. заполнить позже


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
        if characteristics["weapon_id"] == 0:
            self.equip_weapon(None)
        if characteristics["armor_id"] == 0:
            self.equip_armor(None)
        self.calculate_characteristics()

    def calculate_characteristics(self):  # считает характеристики относительно уровня, special и предметов
        self.stats = dict()
        # Вычисление стартовых характеристик
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
        # Подгоняет статы по уровню и добавляет бонусные от брони и оружия 
        for stat in self.stats.keys():
            self.stats[stat] *= int(1 + self.lvl / 25)
            if self.armor is not None:
                self.stats[stat] += self.armor.Stat_Boosts[stat]
            if self.weapon is not None:
                self.stats[stat] += self.weapon.Stat_Boosts[stat]

    def equip_armor(self, armor):

        self.armor = armor
        if armor is not None:
            self.calculate_characteristics()

    def equip_weapon(self, weapon):
        self.weapon = weapon
        if weapon is not None:
            self.calculate_characteristics()

    def level_up(self):
        if self.xp >= XP_TABLE[self.lvl]:
            self.xp -= XP_TABLE[self.lvl]
            self.lvl += 1
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

        target.stats["hp"] -= total_damage
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

        target.stats["hp"] -= total_damage
        return total_damage


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
        self.item_class = "Armor"


class Weapon(EquipItem):
    def __init__(self, stats):
        super(Weapon, self).__init__(stats)
        self.item_class = "Weapon"


class FightMember:
    def __init__(self, character: BaseCharacter):
        self.character = character
        self.defeated = False
        self.made_move = False
        self.turns_before_spec_attack = 0
        self.character.stats["hp"] = self.character.stats["max_hp"]


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
                damage = actor.character.specattack(object.character)
                actor.turns_before_spec_attack = actor.character.spec_attack_recovery

        elif move_type == "attack":
            damage = actor.character.attack(object.character)
        if object.character.stats["hp"] <= 0:
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
