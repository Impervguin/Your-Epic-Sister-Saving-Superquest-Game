import thorpy
import Classes
import pygame

class Game:
    def __init__(self):
        self.window_size = (1440, 1024)
        self.application = thorpy.Application(self.window_size, "YESSS")
        self.elements = []
        self.background = thorpy.Background(elements=self.elements)
        self.menu = thorpy.Menu(self.background)
        self.params = {'lvl':None, 'chr':None}
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
            self.disclaimer_window()
            # self.level_selector()

        def load_game_button_handler():
            self.clear_window()
            pass

        new_game_button = thorpy.make_button("Начать новую игра", func=new_game_button_handler)
        new_game_button.set_size((425, 125))
        new_game_button.set_topleft((507, 260))

        load_game_button = thorpy.make_button("Загрузить игру", func=load_game_button_handler)
        load_game_button.set_size((425, 125))
        load_game_button.set_topleft((507, 559))

        self.elements = [new_game_button, load_game_button]
        self.init_window()
        self.start_window()



    def disclaimer_window(self):
        def press():
            self.clear_window()
            self.level_selector()

        disclaimer_image_path = "disclaimer.png"
        disclaimer = thorpy.make_button("", func=press)
        disclaimer.set_size(self.window_size)
        disclaimer.set_topleft((0, 0))
        disclaimer.remove_all_hovered_states()
        disclaimer.set_image(img=pygame.image.load(disclaimer_image_path), state=thorpy.constants.STATE_NORMAL)



        self.elements = [disclaimer]
        self.init_window()
        self.start_window()


    def character_view(self, id):
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

        Levels = [thorpy.make_button(f"Уровень {i + 1}", func=lvl_button_parser, params={"n":i+1}) for i in range(10)]
        Levels_Box = thorpy.Box(elements=Levels)
        for level in Levels:
            level.set_size((350, 120))
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

        Characters = [thorpy.make_button(f"Персонаж {i + 1}", func=chr_button_parser, params={"n":i+1}) for i in range(4)]
        Characters_Box = thorpy.Box(elements=Characters)
        for character in Characters:
            character.set_size((120, 120))
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
# a.level_selector()