import thorpy
import Classes


class Game:
    def __init__(self):
        pass

    def init_window(self):
        application = thorpy.Application((1440, 1024), "YESSS")
        background = thorpy.Background(elements=[])
        menu = thorpy.Menu(background)
        menu.play()

    def clear_window(self):
        pass

    def close_window(self):
        pass

