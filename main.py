from engine import Application

from layouts.Game import Game
from layouts.Menu import Menu

from const import SIZE_W

app = Application(size=SIZE_W)
app.load_layout('game', Game(app, 'layouts//Game.json'))
app.load_layout('menu', Menu(app, 'layouts//Menu.json'))
app.run()
