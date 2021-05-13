from engine import Application

from const import SIZE_W

if __name__ == "__main__":
    app = Application(size=SIZE_W)

    from data.layouts.Game import Game
    from data.layouts.Menu import Menu
    from data.layouts.Editor import Editor

    app.load_layout('game', Game(app))
    app.load_layout('menu', Menu(app))
    app.load_layout('editor', Editor(app))
    app.run()
