from engine import Application

from const import SIZE_W

if __name__ == "__main__":
    app = Application(size=SIZE_W)

    from data.layouts.Game import Game
    from data.layouts.Menu import Menu

    app.load_layout('game', Game(app, 'data\\layouts\\Game.json'))
    app.load_layout('menu', Menu(app, 'data\\layouts\\Menu.json'))
    app.run()
