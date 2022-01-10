import thorpy

application = thorpy.Application((1440, 1024), "ThorPy Overview")

Levels = [thorpy.make_button(f"Уровень {i + 1}") for i in range(10)]
for l in Levels:
    l.set_size((350, 120))
LevelBox = thorpy.Box(elements=Levels)
LevelBox.add_lift()
LevelBox.center()
LevelBox.set_size((1000, 1024))


LevelBox.set_title(thorpy.Title("Уровни"))
for i in range(len(Levels)):
    if i % 2 == 0:
        Levels[i].set_topleft((600, -114 + 160 * (i // 2)))
    else:
        Levels[i].set_topleft((1000, -114 + 160 * (i // 2)))
Characters = [thorpy.make_button(f"Персонаж {i + 1}") for i in range(10)]

CharacterBox = thorpy.Box(elements=Characters)
CharacterBox.set_size((440, 1024))

LevelBox.set_topleft((0, 0))
CharacterBox.set_topleft((1000, 0))

background = thorpy.Background(elements=[LevelBox, CharacterBox])
# thorpy.store(background)

menu = thorpy.Menu(background)
menu.play()

application.quit()