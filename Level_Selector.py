import thorpy

application = thorpy.Application((1440, 1024), "Выбор уровня")

Levels = [thorpy.make_button(f"Уровень {i + 1}", func=thorpy.functions.quit_menu_func) for i in range(10)]
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


Characters = [thorpy.make_button(f"Персонаж {i + 1}") for i in range(4)]
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


background = thorpy.Background(elements=[Levels_Box, Characters_Box])
menu = thorpy.Menu(background)
menu.play()

application.quit()