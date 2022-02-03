import random
import pymorphy2
import thorpy
import Classes
import pygame
import sqlite3
import splitter

MORPH = pymorphy2.MorphAnalyzer()


class Game:
    def __init__(self):
        self.window_size = (1440, 1024)
        self.application = thorpy.Application(self.window_size, "YESSS")
        self.elements = []
        self.save_opened = False
        self.obj = sqlite3.connect(f"BaseObjects.db")
        self.obj_cur = self.obj.cursor()
        self.background = thorpy.Background(elements=self.elements)

        self.params = {'lvl': None, 'chr': None}

        self.start_menu_window()

    def init_window(self):
        self.menu = thorpy.Menu(self.background)
        self.menu.play()


    def clear_window(self):


        self.elements = []
        # self.init_window()

    def close_window(self):
        self.application.quit()

    def start_window(self, reac=[]):
        # print(1)
        self.menu.remove_from_population(self.background)
        self.background = thorpy.Background(elements=self.elements)
        for r in reac:
            self.background.add_reaction(r)
        self.menu.rebuild(self.background)
        self.menu.blit_and_update()
        # self.background.remove_all_elements()
        # self.background.add_elements(self.elements)
        #
        # self.background.unblit_and_reblit()


    def start_menu_window(self):

        def new_game_button_handler():
            self.clear_window()
            self.new_game()
            self.disclaimer_window()

        def load_game_button_handler():
            self.clear_window()
            self.load_save()
            self.disclaimer_window()

        new_game_button = thorpy.make_button("Начать новую игру", func=new_game_button_handler)
        new_game_button.set_size((425, 125))
        new_game_button.set_topleft((507, 260))

        load_game_button = thorpy.make_button("Загрузить игру", func=load_game_button_handler)
        load_game_button.set_size((425, 125))
        load_game_button.set_topleft((507, 559))
        self.clear_window()
        self.elements = [new_game_button, load_game_button]

        self.background.add_elements(self.elements)
        self.init_window()

    def open_save(self):
        save_path = "saves/save.db"
        self.save = sqlite3.connect(save_path)
        self.cur = self.save.cursor()
        self.save_opened = True

    def new_game(self):
        self.open_save()
        self.cur.execute("UPDATE Heroes SET lvl = '1'")
        self.cur.execute("UPDATE Heroes SET xp = '0'")
        self.cur.execute("UPDATE Heroes SET weapon_id = '0'")
        self.cur.execute("UPDATE Heroes SET armor_id = '0'")
        self.cur.execute("UPDATE Heroes SET available = '0'")
        self.cur.execute("UPDATE Heroes SET available = '1' where id = '1'")

        self.cur.execute("UPDATE Levels SET completed = '0'")
        f = open("saves/inventory.txt", "w", encoding="utf-8")
        f.close()
        self.load_save()

    def load_save(self):
        if not self.save_opened:
            self.open_save()
        heroes = self.cur.execute("SELECT * FROM Heroes").fetchall()
        characteristics = (
            "id", "name", "lvl", "xp", "weapon_id", "armor_id", "strength", "perception", "endurance", "charisma",
            "intelligence", "agility", "luck", "attack_type", "phys_spec_attack_modifier", "mag_spec_attack_modifier",
            "spec_attack_recovery", "available")

        self.heroes = dict()
        for hero in heroes:
            d = {}
            for i in range(len(characteristics)):
                d[characteristics[i]] = hero[i]
            self.heroes[hero[0]] = Classes.BaseCharacter(d)

        self.levels = dict()
        for level in self.cur.execute("SELECT * FROM Levels").fetchall():
            self.levels[level[0]] = bool(level[1])

        f = open("saves/inventory.txt", "r", encoding="utf-8")
        ids = [int(i) for i in f.readline().split()]
        f.close()
        inv = [self.obj_cur.execute(f"SELECT * FROM items WHERE id='{el}'").fetchone() for el in ids]
        item_char = (
            "id", "type", "name", "max_hp", "phys_atk", "mag_atk", "phys_def", "mag_def", "crit_chance",
            "crit_modifier",
            "accuracy", "dodge")
        self.inventory = []
        for obj in inv:
            d = dict()
            for j in range(len(item_char)):
                d[item_char[j]] = obj[j]
            self.inventory.append(Classes.Armor(d) if d["type"] == "armor" else Classes.Weapon(d))
        self.selected_heroes = [None, self.heroes[1], None]

    def save_game(self):
        for h in self.heroes.values():
            self.cur.execute(
                f"UPDATE Heroes SET lvl = '{h.lvl}', xp = '{h.xp}', weapon_id = '{h.weapon.id if h.weapon is not None else 0}', armor_id = '{h.armor.id if h.armor is not None else 0}' WHERE id = '{h.id}'")
        for l in self.levels.keys():
            self.cur.execute(f"UPDATE Levels SET completed = {self.levels[l]} WHERE id = {l}")
        self.save.commit()

        f = open("saves/inventory.txt", "w", encoding="utf-8")
        f.write(" ".join([str(el.id) for el in self.inventory]))
        f.close()

    def disclaimer_window(self):
        def press():
            # self.clear_window()
            self.level_selector()

        disclaimer_image_path = "sprites/disclaimers/disclaimer.png"
        disclaimer = thorpy.make_button("", func=press)
        disclaimer.set_size(self.window_size)
        disclaimer.set_topleft((0, 0))
        disclaimer.remove_all_hovered_states()
        disclaimer.set_image(img=pygame.image.load(disclaimer_image_path), state=thorpy.constants.STATE_NORMAL)

        self.elements = [disclaimer]
        self.start_window()

    def character_view(self, id):

        def armor_button_handler(item):
            global ITEM
            ITEM = item
            thorpy.launch_nonblocking_choices(f"Экипировать {item.name}?", [("Да", equip_armor), ("Нет", None)])

        def weapon_button_handler(item):
            global ITEM
            ITEM = item
            thorpy.launch_nonblocking_choices(f"Экипировать {item.name}?", [("Да", equip_weapon), ("Нет", None)])

        def equip_armor():
            armor = hero.armor
            item = ITEM
            index = self.inventory.index(item)
            if armor is not None:
                self.inventory[index] = armor
            else:
                self.inventory.pop(index)
            hero.equip_armor(item.id)

            self.clear_window()
            self.character_view(id)

        def equip_weapon():
            weapon = hero.weapon
            item = ITEM
            index = self.inventory.index(item)
            if weapon is not None:
                self.inventory[index] = weapon
            else:
                self.inventory.pop(index)
            hero.equip_weapon(item.id)

            self.clear_window()
            self.character_view(id)

        def go_back_button_handler():
            self.clear_window()
            self.level_selector()

        hero = self.heroes[id]
        d = {"mag": "Магическая", "phys": "Физическая", "hybrid": "Гибридная"}
        im = thorpy.Image(f"sprites/{id}/char.png")
        im.set_topleft((570, 120))
        im.set_size((300, 600))

        characteristics_font_size = 25

        els_name = [
            thorpy.OneLineText("Уровень"),
            thorpy.OneLineText("Опыт"),
            thorpy.OneLineText("Сила"),
            thorpy.OneLineText("Восприятие"),
            thorpy.OneLineText("Выносливость"),
            thorpy.OneLineText("Харизма"),
            thorpy.OneLineText("Интеллект"),
            thorpy.OneLineText("Ловкость"),
            thorpy.OneLineText("Удача"),

            thorpy.OneLineText("Здоровье"),
            thorpy.OneLineText("Физическая атака"),
            thorpy.OneLineText("Магическая атака"),
            thorpy.OneLineText("Физическая защита"),
            thorpy.OneLineText("Магическая защита"),
            thorpy.OneLineText("Тип атаки"),
            thorpy.OneLineText("Шанс крита"),
            thorpy.OneLineText("Множитель крита"),
            thorpy.OneLineText("Точность"),
            thorpy.OneLineText("Уворот"),
            thorpy.OneLineText("Броня"),
            thorpy.OneLineText("Оружие")
        ]

        for el in els_name:
            el.set_font_size(characteristics_font_size)
        weapon_name = self.obj_cur.execute(f"SELECT name FROM items where id= '{hero.weapon.id}'").fetchone()[
            0] if hero.weapon is not None else "Отсутвует"
        armor_name = self.obj_cur.execute(f"SELECT name FROM items where id= '{hero.armor.id}'").fetchone()[
            0] if hero.armor is not None else "Отсутвует"
        els_value = [
            thorpy.OneLineText(str(hero.lvl)),
            thorpy.OneLineText(str(hero.xp)),
            thorpy.OneLineText(str(hero.strength)),
            thorpy.OneLineText(str(hero.perception)),
            thorpy.OneLineText(str(hero.endurance)),
            thorpy.OneLineText(str(hero.charisma)),
            thorpy.OneLineText(str(hero.intelligence)),
            thorpy.OneLineText(str(hero.agility)),
            thorpy.OneLineText(str(hero.luck)),
            thorpy.OneLineText(str(hero.stats["max_hp"])),
            thorpy.OneLineText(str(hero.stats["phys_atk"])),
            thorpy.OneLineText(str(hero.stats["mag_atk"])),
            thorpy.OneLineText(str(hero.stats["phys_def"])),
            thorpy.OneLineText(str(hero.stats["mag_def"])),
            thorpy.OneLineText(d[hero.attack_type]),
            thorpy.OneLineText(str(hero.stats["crit_chance"]) + "%"),
            thorpy.OneLineText(str(hero.stats["crit_modifier"]) + "%"),
            thorpy.OneLineText(str(hero.stats["accuracy"]) + "%"),
            thorpy.OneLineText(str(hero.stats["dodge"]) + "%"),
            thorpy.OneLineText(armor_name),
            thorpy.OneLineText(weapon_name),
        ]
        for el in els_value:
            el.set_font_size(characteristics_font_size)
        els = els_name + els_value
        char_box = thorpy.Box(els)
        char_box.set_topleft((50, 75))
        char_box.set_size((420, 860))

        char_name_store = thorpy.store(char_box, elements=els_name, align="left", x=60, y=85)
        char_value_store = thorpy.store(char_box, elements=els_value, align="right", x=460, y=85)
        inv_buttons = [
            thorpy.make_button("", func=armor_button_handler if el.type == "armor" else weapon_button_handler,
                               params={"item": el}) for el in self.inventory]
        for i in range(len(inv_buttons)):
            if i % 3 == 0:
                inv_buttons[i].set_topleft((30, 30 + 150 * (i // 3)))
            elif i % 3 == 1:
                inv_buttons[i].set_topleft((160, 30 + 150 * (i // 3)))
            else:
                inv_buttons[i].set_topleft((290, 30 + 150 * (i // 3)))
            inv_buttons[i].set_size((100, 100))
            inv_buttons[i].set_text(self.inventory[i].name)
            inv_buttons[i].set_image(img=pygame.image.load(f"sprites/items/{self.inventory[i].id}/icon.png"))

        inv_title = thorpy.make_text("Инвентарь", font_size=20)

        inventory_box = thorpy.Box(inv_buttons + [inv_title])
        inv_title.set_topleft((165, 15))
        for i in range(len(inv_buttons)):
            if i % 3 == 0:
                inv_buttons[i].set_topleft((30, 50 + 150 * (i // 3)))
            elif i % 3 == 1:
                inv_buttons[i].set_topleft((160, 50 + 150 * (i // 3)))
            else:
                inv_buttons[i].set_topleft((290, 50 + 150 * (i // 3)))
            inv_buttons[i].set_size((100, 100))
            inv_buttons[i].set_text(splitter.splitter(self.inventory[i].name))
            inv_buttons[i].set_image(img=pygame.image.load(f"sprites/items/{self.inventory[i].id}/icon.png"))
        inventory_box.set_topleft((970, 75))
        inventory_box.set_size((420, 860))

        go_back_button = thorpy.make_button("Вернуться назад", func=go_back_button_handler)
        go_back_button.set_topleft((520, 815))
        go_back_button.set_size((400, 120))

        self.elements = [im, char_box, inventory_box, go_back_button]

        self.start_window()

    def character_selector(self, id):
        def char_button_handler(hero):
            global HERO
            HERO = hero
            thorpy.launch_nonblocking_choices(f"На какое место вы хотите поставить персонажа {hero.name.capitalize()}?",
                                              [("Напарник 1", set_partner_1), ("Напарник 2", set_partner_2),
                                               ("Отмена", None)]
                                              )

        def set_partner_1():
            if self.selected_heroes[2] == HERO:
                self.selected_heroes[2] = None
            self.selected_heroes[0] = HERO

            self.clear_window()
            self.character_selector(id)

        def set_partner_2():
            if self.selected_heroes[0] == HERO:
                self.selected_heroes[0] = None
            self.selected_heroes[2] = HERO

            self.clear_window()
            self.character_selector(id)

        def go_back_button_handler():
            self.clear_window()
            self.level_selector()

        def proceed_button_handler():
            self.clear_window()
            self.init_fight(id)

        def reset_button_handler():
            self.selected_heroes[0] = None
            self.selected_heroes[2] = None
            self.clear_window()
            self.character_selector(id)

        char_buttons = [thorpy.make_button(h.name.capitalize(), func=char_button_handler, params={"hero": h}) for h in
                        self.heroes.values()]
        char_box = thorpy.Box(char_buttons)
        for i in range(len(char_buttons)):
            char_buttons[i].set_size((120, 120))
            char_buttons[i].set_image(pygame.image.load(f"sprites/{i + 1}/icon.png"))
            char_buttons[i].set_active(self.heroes[i + 1].available)
        char_buttons[0].set_active(False)
        char_store = thorpy.store(char_box, char_buttons, "h", gap=50)

        char_box.fit_children()
        char_box.set_topleft((0, 492))
        char_box.center(axis=(True, False))
        selected_char = [thorpy.Element() for h in self.selected_heroes]
        for i in range(len(selected_char)):
            selected_char[i].set_topleft((370 + 290 * i, 190))
            selected_char[i].set_size((120, 120))
            if self.selected_heroes[i] is not None:
                selected_char[i].set_image(pygame.image.load(f"sprites/{self.selected_heroes[i].id}/icon.png"))

        reset = thorpy.make_button("Сброс", func=reset_button_handler)
        reset.set_topleft((620, 361))
        reset.set_size((200, 80))

        title = thorpy.make_text(f"Уровень {id}", font_size=40)
        title.set_topleft((0, 50))
        title.center(axis=(True, False))

        go_back_button = thorpy.make_button("Вернуться назад", func=go_back_button_handler)
        go_back_button.set_topleft((270, 800))
        go_back_button.set_size((400, 120))

        proceed_button = thorpy.make_button("Далее", func=proceed_button_handler)
        proceed_button.set_topleft((770, 800))
        proceed_button.set_size((400, 120))

        self.elements = [char_box, title, go_back_button, proceed_button, reset] + selected_char

        self.start_window()

    def level_selector(self):
        def lvl_button_parser(n):
            self.params['lvl'] = n
            self.clear_window()
            self.character_selector(n)

        def chr_button_parser(n):
            self.clear_window()
            self.character_view(n)

        Levels = [thorpy.make_button(f"Уровень {i + 1}", func=lvl_button_parser, params={"n": i + 1}) for i in
                  range(len(self.levels))]
        Levels_Box = thorpy.Box(elements=Levels)
        first_not_completed = False
        for i in range(len(Levels)):
            Levels[i].set_size((350, 120))
            if not self.levels[i + 1] and not first_not_completed:
                Levels[i].set_active(True)
                first_not_completed = True
            else:
                Levels[i].set_active(self.levels[i + 1])

        Levels_Box.set_size((1000, 1024))

        Levels_Title = thorpy.make_text("Уровни", 48)
        Levels_Box.add_element(Levels_Title)
        Levels_Title.set_topleft((410, 61))

        for i in range(len(Levels)):
            if i % 2 == 0:
                Levels[i].set_topleft((100, 160 + 160 * (i // 2)))
            else:
                Levels[i].set_topleft((550, 160 + 160 * (i // 2)))

        Levels_Box.set_topleft((0, 0))

        Characters = [
            thorpy.make_button(self.heroes[i + 1].name.capitalize(), func=chr_button_parser, params={"n": i + 1}) for i
            in
            range(len(self.heroes))]
        save_button = thorpy.make_button("Сохранить игру", func=self.save_game)

        Characters_Box = thorpy.Box(elements=Characters + [save_button])
        for i in range(len(Characters)):
            Characters[i].set_size((120, 120))
            Characters[i].set_image(pygame.image.load(f"sprites/{i + 1}/icon.png"))
            Characters[i].set_active(self.heroes[i + 1].available)

        save_button.set_topleft((100, 800))
        save_button.set_size((240, 120))

        Characters_Box.set_size((440, 1024))

        Characters_Title = thorpy.make_text("Персонажи", 48)
        Characters_Box.add_element(Characters_Title)
        Characters_Title.set_topleft((80, 51))

        for i in range(len(Characters)):
            if i % 2 == 0:
                Characters[i].set_topleft((50, 160 + 160 * (i // 2)))
            else:
                Characters[i].set_topleft((245, 160 + 160 * (i // 2)))

        Characters_Box.set_topleft((1000, 0))

        self.elements = [Characters_Box, Levels_Box]

        self.start_window()

    def init_fight(self, level_id):
        print(1)
        player_team = [Classes.FightMember(char) for char in self.selected_heroes]
        self.leveldb = sqlite3.connect("levels.db")
        lcur = self.leveldb.cursor()
        level = lcur.execute(f"SELECT * FROM levels WHERE id='{level_id}'").fetchone()
        enemy_team = []
        for i in range(1, 6, 2):
            if level[i] != 0:
                enemy = dict()
                param_names = (
                "id", "name", "max_hp", "phys_atk", "mag_atk", "phys_def", "mag_def", "crit_chance", "crit_modifier",
                "accuracy", "dodge", "attack_type", "xp_per_level")
                params = self.obj_cur.execute(f"SELECT * FROM enemies WHERE id = '{level[i]}'").fetchone()
                for j in range(len(param_names)):
                    enemy[param_names[j]] = params[j]
                enemy["lvl"] = level[i + 1]
                enemy_team.append(Classes.FightMember(Classes.BaseEnemy(enemy)))
            else:
                enemy_team.append(Classes.FightMember(None))
        self.fight_screen(player_team, enemy_team, level_id)

    def fight_screen(self, pteam, eteam, level_id):

        def ddl_reaction(event):
            char = event.value
            if any([ch in char for ch in [i.name for i in self.heroes.values()]]):
                global SEL_CHAR
                SEL_CHAR = int(event.value[1]) - 1
                char = pteam[int(event.value[1]) - 1].character
                hero_name.set_text("Имя: " + char.name)
                hero_atk_type.set_text("Тип атаки: " + char.attack_type)
                hero_mag_atk.set_text("Маг атака: " + str(char.stats["mag_atk"]))
                hero_phys_atk.set_text("Физ атака: " + str(char.stats["phys_atk"]))
                hero_hp.set_text("Хп: " + str(char.stats["hp"]) + "/" + str(char.stats["max_hp"]))
                hero_box.fit_children()
                hero_box.center(axis=(True, False))

            else:
                global SEL_ENEMY
                SEL_ENEMY = int(event.value[1]) - 1
                char = eteam[int(event.value[1]) - 1].character
                enemy_name.set_text("Имя: " + char.name)
                enemy_atk_type.set_text("Тип атаки: " + char.attack_type)
                enemy_mag_def.set_text("Маг защита: " + str(char.stats["mag_def"]))
                enemy_phys_def.set_text("Физ защита: " + str(char.stats["phys_def"]))
                enemy_hp.set_text("Хп: " + str(char.stats["hp"]) + "/" + str(char.stats["max_hp"]))
                enemy_box.fit_children()
                enemy_box.center(axis=(True, False))
            self.menu.blit_and_update()

        heroes = []
        if not pteam[0].defeated:
            hero1 = thorpy.Image(
                pygame.transform.scale(pygame.image.load(f"sprites/{pteam[0].character.id}/char.png").convert_alpha(),
                                       (100, 200)))
            heroes.append(hero1)
        if not pteam[1].defeated:
            hero2 = thorpy.Image(
                pygame.transform.scale(pygame.image.load(f"sprites/{pteam[1].character.id}/char.png").convert_alpha(),
                                       (100, 200)))
            heroes.append(hero2)
        if not pteam[2].defeated:
            hero3 = thorpy.Image(
                pygame.transform.scale(pygame.image.load(f"sprites/{pteam[2].character.id}/char.png").convert_alpha(),
                                       (100, 200)))
            heroes.append(hero3)

        enemies = []
        if not eteam[0].defeated:
            e1 = thorpy.Image(pygame.transform.scale(
                pygame.image.load(f"sprites/enemies/{eteam[0].character.id}/char.png").convert_alpha(), (100, 200)))
            enemies.append(e1)
        if not eteam[1].defeated:
            e2 = thorpy.Image(pygame.transform.scale(
                pygame.image.load(f"sprites/enemies/{eteam[1].character.id}/char.png").convert_alpha(), (100, 200)))
            enemies.append(e2)
        if not eteam[2].defeated:
            e3 = thorpy.Image(pygame.transform.scale(
                pygame.image.load(f"sprites/enemies/{eteam[2].character.id}/char.png").convert_alpha(), (100, 200)))
            enemies.append(e3)

        fight_area = thorpy.Box(heroes + enemies)
        fight_area.set_topleft((0, 0))
        fight_area.set_size((1440, 604))
        fight_area.set_image(pygame.image.load("sprites/background1.png"))

        if not pteam[0].defeated:
            hero1.set_size((100, 200))
            hero1.set_topleft((1230, 100))
        if not pteam[1].defeated:
            hero2.set_size((100, 200))
            hero2.set_topleft((1050, 190))
        if not pteam[2].defeated:
            hero3.set_size((100, 200))
            hero3.set_topleft((1270, 350))

        if not eteam[0].defeated:
            e1.set_size((100, 200))
            e1.set_topleft((110, 100))
        if not eteam[1].defeated:
            e2.set_size((100, 200))
            e2.set_topleft((290, 190))
        if not eteam[2].defeated:
            e3.set_size((100, 200))
            e3.set_topleft((70, 350))

        hero_chooser = thorpy.DropDownListLauncher(
            titles=[f"({i + 1})" + pteam[i].character.name for i in range(len(pteam)) if
                    not pteam[i].defeated and not pteam[i].made_move], const_text="Hero:")
        enemy_chooser = thorpy.DropDownListLauncher(
            titles=[f"({i + 1})" + eteam[i].character.name for i in range(len(eteam)) if not eteam[i].defeated],
            const_text="Enemy:")
        hero_name = thorpy.make_text("Имя:")
        hero_hp = thorpy.make_text("Хп:")
        hero_atk_type = thorpy.make_text("Тип атаки:")
        hero_mag_atk = thorpy.make_text("Маг атака:")
        hero_phys_atk = thorpy.make_text("Физ атака:")
        hero_box = thorpy.Box([hero_name, hero_hp, hero_atk_type, hero_phys_atk, hero_mag_atk])

        enemy_name = thorpy.make_text("Имя:")
        enemy_hp = thorpy.make_text("Хп:")
        enemy_atk_type = thorpy.make_text("Тип атаки:")
        enemy_mag_def = thorpy.make_text("Маг защита:")
        enemy_phys_def = thorpy.make_text("Физ защита:")
        enemy_box = thorpy.Box([enemy_name, enemy_hp, enemy_atk_type, enemy_phys_def, enemy_mag_def])

        def atk_button_handler():
            if "SEL_ENEMY" not in globals():
                global SEL_ENEMY
                SEL_ENEMY = None

            if "SEL_CHAR" not in globals():
                global SEL_CHAR
                SEL_CHAR = None

            if SEL_CHAR is not None and SEL_ENEMY is not None:
                command = ("attack", SEL_CHAR, SEL_ENEMY)
                self.execute_fight_command(pteam, eteam, command, level_id)
            else:
                thorpy.launch_nonblocking_choices("Выберете героя и противника", [("ОК", None)])

        def spec_atk_button_handler():
            if "SEL_ENEMY" not in globals():
                global SEL_ENEMY
                SEL_ENEMY = None

            if "SEL_CHAR" not in globals():
                global SEL_CHAR
                SEL_CHAR = None

            if SEL_CHAR is not None and SEL_ENEMY is not None:
                command = ("specattack", SEL_CHAR, SEL_ENEMY)
                if pteam[SEL_CHAR].turns_before_spec_attack > 0:
                    thorpy.launch_nonblocking_choices(
                        f"Перезарядка спецатаки.\n Осталось ходов:{pteam[SEL_CHAR].turns_before_spec_attack}",
                        [("ОК", None)])
                else:
                    self.execute_fight_command(pteam, eteam, command, level_id)
            else:
                thorpy.launch_nonblocking_choices("Выберете героя и противника", [("ОК", None)])

        def wait_button_handler():
            if "SEL_CHAR" not in globals():
                global SEL_CHAR
                SEL_CHAR = None
            if SEL_CHAR is not None:
                command = ("wait", SEL_CHAR)
                self.execute_fight_command(pteam, eteam, command, level_id)
            else:
                thorpy.launch_nonblocking_choices("Выберете героя", [("ОК", None)])

        atk_button = thorpy.make_button("Атаковать", func=atk_button_handler)
        spec_atk_button = thorpy.make_button("Спец атака", func=spec_atk_button_handler)
        wait_button = thorpy.make_button("Ждать", func=wait_button_handler)

        control_box = thorpy.Box(
            [hero_chooser, enemy_chooser, hero_box, enemy_box, atk_button, spec_atk_button, wait_button])
        hero_box.set_topleft((0, 75))
        hero_box.fit_children()
        hero_box.center(axis=(True, False))
        enemy_box.set_topleft((0, 245))
        enemy_box.fit_children()
        enemy_box.center(axis=(True, False))
        hero_chooser.set_topleft((0, 30))
        hero_chooser.center(axis=(True, False))
        enemy_chooser.set_topleft((0, 200))
        enemy_chooser.center(axis=(True, False))

        #
        atk_button.set_topleft((1080, 55))
        spec_atk_button.set_topleft((1080, 175))
        wait_button.set_topleft((1080, 295))
        atk_button.set_size((300, 70))
        spec_atk_button.set_size((300, 70))
        wait_button.set_size((300, 70))

        control_box.set_topleft((0, 604))
        control_box.set_size((1440, 420))

        self.elements = [fight_area, control_box]
        self.start_window(reac=[thorpy.Reaction(thorpy.constants.THORPY_EVENT, reac_func=ddl_reaction,
                                               event_args={"id": thorpy.constants.EVENT_DDL})])

    def execute_fight_command(self, pteam, eteam, command, level_id):
        if command[0] == "attack":
            hero = pteam[command[1]]
            enemy = eteam[command[2]]
            damage = hero.character.attack(enemy.character)
            enemy.character.stats["hp"] -= damage
            if enemy.character.stats["hp"] <= 0:
                enemy.defeated = True
            hero.made_move = True
        elif command[0] == "specattack":
            hero = pteam[command[1]]
            enemy = eteam[command[2]]
            damage = hero.character.specattack(enemy.character)
            enemy.character.stats["hp"] -= damage
            if enemy.character.stats["hp"] <= 0:
                enemy.defeated = True
            hero.made_move = True
            hero.turns_before_spec_attack = hero.character.spec_attack_recovery
        elif command[0] == "wait":
            hero = pteam[command[1]]
            hero.made_move = True
        global SEL_CHAR, SEL_ENEMY
        SEL_CHAR = None
        SEL_ENEMY = None
        if all([e.defeated for e in eteam]):
            self.end_level_screen(pteam,eteam, level_id)
            return 0
        if all([p.made_move for p in pteam]):
            self.enemy_team_move(eteam, pteam, level_id)
            for p in pteam:
                if not p.defeated:
                    p.made_move = False
                    p.turns_before_spec_attack -= 1
        if all([p.defeated for p in pteam]):
            self.defeated_screen()
            return 0

        self.fight_screen(pteam, eteam, level_id)

    def enemy_team_move(self, eteam, pteam, level_id):
        for e in eteam:
            if all([p.defeated for p in pteam]):
                break
            if not e.defeated:
                p = random.choice(pteam)
                while p.defeated:
                    p = random.choice(pteam)
                damage = e.character.attack(p.character)
                p.character.stats["hp"] -= damage
                if p.character.stats["hp"] <= 0:
                    p.defeated = True

    def end_level_screen(self, pteam, eteam, level_id):
        title = thorpy.make_text("Вы победили!", font_size=120)

        xp = 0
        for e in eteam:
            if e.character is not None:
                xp += e.character.xp_per_level * e.character.lvl
        xp = xp * 3 // len(tuple(filter(lambda x: x.character is not None, pteam)))
        texts = []
        for p in pteam:
            if p.character is not None:
                p.character.xp += xp
                l = 0
                while p.character.level_up():
                    l += 1
                texts.append(thorpy.make_text(f"Персонаж {p.character.name.capitalize()} получает {xp} XP!"))
                if l > 0:
                    lvl_word = MORPH.parse("уровень")[0]
                    texts.append(thorpy.make_text(f"Персонаж {p.character.name.capitalize()} Поднимает {l} {lvl_word.make_agree_with_number(l).word}!"))

        lcur = self.leveldb.cursor()
        if not self.levels[level_id]:
            item_id = lcur.execute(f"SELECT firstbonusitem FROM levels WHERE id='{level_id}'").fetchone()[0]
            if item_id != 0:
                print(item_id)
                item_name = self.obj_cur.execute(f"SELECT name FROM items WHERE id='{item_id}'").fetchone()[0]
                print(item_name)
                texts.append(thorpy.make_text(f"Бонус первого прохождения {item_name.capitalize()} добавлен в инвентарь"))
                item_char = (
                    "id", "type", "name", "max_hp", "phys_atk", "mag_atk", "phys_def", "mag_def", "crit_chance",
                    "crit_modifier",
                    "accuracy", "dodge")
                item = self.obj_cur.execute(f"SELECT * FROM items WHERE id='{item_id}'").fetchone()
                d = {}
                for i in range(len(item_char)):
                    d[item_char[i]] = item[i]

                self.inventory.append(Classes.Armor(d) if d["type"] == "armor" else Classes.Weapon(d))

            char_id = lcur.execute(f"SELECT characteropen FROM levels WHERE id='{level_id}'").fetchone()[0]
            if char_id != 0:
                self.heroes[char_id].available = True
                texts.append(thorpy.make_text(f"Вы разблокировали персонажа {self.heroes[char_id].name.capitalize()}"))
        self.levels[level_id] = True


        results_box = thorpy.Box(texts)

        for t in texts:
            t.set_font_size(25)

        store = thorpy.store(results_box, texts, align="left", margin=5)
        results_box.fit_children()
        results_box.center()

        title.set_topleft((0, 100))
        title.center(axis=(True, False))

        return_but = thorpy.make_button("Вернуться в меню", func=self.level_selector)
        return_but.set_size((200, 200))
        return_but.set_topleft((100, 724))

        self.elements = [return_but, results_box, title]


        self.start_window()

    def defeated_screen(self):
        pass


a = Game()
