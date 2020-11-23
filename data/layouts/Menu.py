from engine import *
from const import *
from widgets import *
import pygame


class Menu(Layout):
    play_1_player_button: PPushButton
    play_2_player_button: PPushButton
    editor_button: PPushButton
    company_1_lbl: PLabel
    company_2_lbl: PLabel
    year_lbl: PLabel
    logo_lbl: PLabel

    def __init__(self, app: Application, layout_config_filename: str = None):
        super().__init__(app, layout_config_filename)
        self.init_ui()

        self.play_1_player_button.connect(self.app.open_layout, 'game', False)
        self.play_2_player_button.connect(self.app.open_layout, 'game', True)

    def init_ui(self):
        background = pygame.Surface(size=(1, 1))
        background.fill((100, 100, 100))
        font = pygame.font.SysFont('OCR A Extended', int(SIZE_SMALL_CELL * 1.5))

        self.play_1_player_button = PPushButton("1 Player")
        self.play_1_player_button.resize((SIZE_LARGE_CELL * 4, SIZE_LARGE_CELL))
        self.play_1_player_button.set_pos((SIZE_LARGE_CELL * 6, SIZE_LARGE_CELL * 8))
        self.play_1_player_button.set_font(font)
        self.add_widget(self.play_1_player_button.flip())

        self.play_2_player_button = PPushButton("2 Player")
        self.play_2_player_button.resize((SIZE_LARGE_CELL * 4, SIZE_LARGE_CELL))
        self.play_2_player_button.set_pos((SIZE_LARGE_CELL * 6, SIZE_LARGE_CELL * 9))
        self.play_2_player_button.set_font(font)
        self.add_widget(self.play_2_player_button.flip())

        self.editor_button = PPushButton("Editor")
        self.editor_button.resize((SIZE_LARGE_CELL * 4, SIZE_LARGE_CELL))
        self.editor_button.set_pos((SIZE_LARGE_CELL * 5.5, SIZE_LARGE_CELL * 10))
        self.editor_button.set_font(font)
        self.add_widget(self.editor_button.flip())

        self.company_1_lbl = PLabel("namco")
        self.company_1_lbl.resize((SIZE_LARGE_CELL * 4, SIZE_LARGE_CELL))
        self.company_1_lbl.set_pos((SIZE_LARGE_CELL * 8, SIZE_LARGE_CELL * 11))
        self.company_1_lbl.set_font(font)
        self.company_1_lbl.set_color_text((255, 0, 0))
        self.add_widget(self.company_1_lbl.flip())

        self.company_2_lbl = PLabel("PyPLy")
        self.company_2_lbl.resize((SIZE_LARGE_CELL * 4, SIZE_LARGE_CELL))
        self.company_2_lbl.set_pos((SIZE_LARGE_CELL * 4, SIZE_LARGE_CELL * 11))
        self.company_2_lbl.set_font(font)
        self.company_2_lbl.set_color_text(pygame.Color('purple'))
        self.add_widget(self.company_2_lbl.flip())

        self.logo_lbl = PLabel()
        self.logo_lbl.resize((SIZE_LARGE_CELL * 10, SIZE_LARGE_CELL * 4))
        self.logo_lbl.set_pos((SIZE_LARGE_CELL * 3, SIZE_LARGE_CELL * 2))
        self.logo_lbl.set_bg_image(load_image("data\\image\\logo.png"))
        self.add_widget(self.logo_lbl.flip())

    def on_open(self):
        self.run_show_menu_animation()

    def run_show_menu_animation(self):
        screen = self.app.screen.copy()
        screen.fill((0, 0, 0))
        self.render(screen)

        t = 170
        for i in range(t):
            self.app.screen.fill((0, 0, 0))
            self.app.screen.blit(screen, (0, int(screen.get_height() * ((t - i) / t))))
            self.app.clock.tick(60)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.MOUSEBUTTONDOWN:
                    return

