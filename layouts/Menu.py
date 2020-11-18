from engine import Application, Layout


class Menu(Layout):
    def __init__(self, app: Application, layout_config_filename: str = None):
        super().__init__(app, layout_config_filename)
