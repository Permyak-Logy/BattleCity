from engine import Application

from data.layouts.Game import Game
from data.layouts.Menu import Menu

from const import SIZE_W

if __name__ == "__main__":
    app = Application(size=SIZE_W)
    app.load_layout('game', Game(app, 'data//layouts//Game.json'))
    app.load_layout('menu', Menu(app, 'data//layouts//Menu.json'))
    app.run()
