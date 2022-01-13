import thorpy
import Classes
import pygame
import sqlite3


class Game:
    def __init__(self):
        self.window_size = (1440, 1024)
        self.application = thorpy.Application(self.window_size, "YESSS")
        self.elements = []
        self.save_opened = False
        self.background = thorpy.Background(elements=self.elements)
        self.menu = thorpy.Menu(self.background)
        self.params = {'lvl': None, 'chr': None}
        self.start_menu_window()

    def init_window(self):
        self.background = thorpy.Background(elements=self.elements)
        self.menu = thorpy.Menu(self.background)

    def clear_window(self):
        self.elements = []
        self.init_window()

    def close_window(self):
        self.application.quit()

    def start_window(self):
        self.menu.play()

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

        self.elements = [new_game_button, load_game_button]
        self.init_window()
        self.start_window()

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
        print(self.heroes)

        self.levels = dict()
        for level in self.cur.execute("SELECT * FROM Levels").fetchall():
            self.levels[level[0]] = bool(level[1])


        print(self.levels)

    def disclaimer_window(self):
        def press():
            self.clear_window()
            self.level_selector()

        disclaimer_image_path = "sprites/disclaimers/disclaimer.png"
        disclaimer = thorpy.make_button("", func=press)
        disclaimer.set_size(self.window_size)
        disclaimer.set_topleft((0, 0))
        disclaimer.remove_all_hovered_states()
        disclaimer.set_image(img=pygame.image.load(disclaimer_image_path), state=thorpy.constants.STATE_NORMAL)

        self.elements = [disclaimer]
        self.init_window()
        self.start_window()

    def character_view(self, id):
        hero = self.heroes[id]
        d = {"mag": "Магическая", "phys": "Физическая", "hybrid":"Гибридная"}
        im = thorpy.Image(f"sprites/{id}/char.png")
        im.set_topleft((570, 120))
        im.set_size((300, 600))
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
            thorpy.OneLineText("Уворот")
        ]

        for el in els_name:
            el.set_font_size(30)
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
            thorpy.OneLineText(str(hero.stats["dodge"]) + "%")
        ]
        for el in els_value:
            el.set_font_size(30)
        els = els_name + els_value
        char_box = thorpy.Box(els)
        char_box.set_topleft((50, 75))
        char_box.set_size((420, 860))

        char_name_store = thorpy.store(char_box, elements=els_name, align="left", x=60, y=85)
        char_value_store = thorpy.store(char_box, elements=els_value, align="right", x=460, y=85)

        self.elements = [im, char_box]
        self.init_window()
        self.start_window()


    def character_selector(self):
        self.start_window()

    def level_selector(self):
        def lvl_button_parser(n):
            self.params['lvl'] = n
            self.clear_window()
            self.character_selector()

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

        Characters = [thorpy.make_button(self.heroes[i + 1].name.capitalize(), func=chr_button_parser, params={"n": i + 1}) for i in
                      range(len(self.heroes))]
        Characters_Box = thorpy.Box(elements=Characters)
        for i in range(len(Characters)):
            Characters[i].set_size((120, 120))
            Characters[i].set_image(pygame.image.load(f"sprites/{i + 1}/icon.png"))
            Characters[i].set_active(self.heroes[i + 1].available)
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
        self.init_window()
        self.start_window()


a = Game()
