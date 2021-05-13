from engine import *
from const import *
from widgets import *
import pygame


class Menu(Layout):
    select_1_player_button: PPushButton
    select_2_player_button: PPushButton
    select_editor_button: PPushButton

    play_1_player_button: PPushButton
    play_2_player_button: PPushButton
    editor_button: PPushButton

    company_1_lbl: PLabel
    company_2_lbl: PLabel

    year_lbl: PLabel
    logo_lbl: PLabel

    bottom_text: PLabel

    selected: int
    count_select: int
    select_image: pygame.Surface

    def __init__(self, app: Application):
        super().__init__(app)
        self.init_ui()

        self.play_1_player_button.connect(self.app.open_layout, 'game', False)
        self.play_2_player_button.connect(self.app.open_layout, 'game', True)

    def render(self, screen: pygame.Surface):
        super(Menu, self).render(screen)
        screen.blit(self.select_image, (SIZE_LARGE_CELL * 4, int(SIZE_LARGE_CELL * (7.5 + self.selected))))

    def init_ui(self):
        font = pygame.font.Font('data\\fonts\\font-7x7.ttf', int(SIZE_SMALL_CELL))

        self.logo_lbl = PLabel()
        self.logo_lbl.resize((SIZE_LARGE_CELL * 19 * 0.6, SIZE_LARGE_CELL * 7 * 0.6))
        self.logo_lbl.set_pos((SIZE_LARGE_CELL * 2, SIZE_LARGE_CELL * 2.5))
        self.logo_lbl.set_bg_image(load_image("data\\image\\logo.png", -1))
        self.add_widget(self.logo_lbl.flip())

        self.play_1_player_button = PPushButton("1 PLAYER  ")
        self.play_1_player_button.resize((SIZE_LARGE_CELL * 5, SIZE_LARGE_CELL))
        self.play_1_player_button.set_pos((SIZE_LARGE_CELL * 5, SIZE_LARGE_CELL * 7.5))
        self.play_1_player_button.set_font(font)
        self.add_widget(self.play_1_player_button.flip())

        self.play_2_player_button = PPushButton("2 PLAYERS")
        self.play_2_player_button.resize((SIZE_LARGE_CELL * 5, SIZE_LARGE_CELL))
        self.play_2_player_button.set_pos((SIZE_LARGE_CELL * 5, SIZE_LARGE_CELL * 8.5))
        self.play_2_player_button.set_font(font)
        self.add_widget(self.play_2_player_button.flip())

        self.editor_button = PPushButton("CONSTRUCTION")
        self.editor_button.resize((SIZE_LARGE_CELL * 7, SIZE_LARGE_CELL))
        self.editor_button.set_pos((SIZE_LARGE_CELL * 5, SIZE_LARGE_CELL * 9.5))
        self.editor_button.set_font(font)
        self.add_widget(self.editor_button.flip())

        self.company_1_lbl = PLabel("NAMCO")
        self.company_1_lbl.resize((SIZE_LARGE_CELL * 4, SIZE_LARGE_CELL))
        self.company_1_lbl.set_pos((SIZE_LARGE_CELL * 8, SIZE_LARGE_CELL * 10.5))
        self.company_1_lbl.set_font(font)
        self.company_1_lbl.set_color_text((255, 0, 0))
        self.add_widget(self.company_1_lbl.flip())

        self.company_2_lbl = PLabel("PYPLY")
        self.company_2_lbl.resize((SIZE_LARGE_CELL * 4, SIZE_LARGE_CELL))
        self.company_2_lbl.set_pos((SIZE_LARGE_CELL * 4, SIZE_LARGE_CELL * 10.5))
        self.company_2_lbl.set_font(font)
        self.company_2_lbl.set_color_text(pygame.Color('purple'))
        self.add_widget(self.company_2_lbl.flip())

        self.bottom_text = PLabel("2020 2021 PYPLY AND NAMCO LTD.")
        self.bottom_text.resize((SIZE_LARGE_CELL * 15, SIZE_LARGE_CELL))
        self.bottom_text.set_pos((SIZE_LARGE_CELL, SIZE_LARGE_CELL * 11.5))
        self.bottom_text.set_font(font)
        self.add_widget(self.bottom_text)

        self.selected = 0
        self.count_select = 3
        self.select_image = pygame.transform.scale(load_image("tanks.png", -1), (SIZE_LARGE_CELL, SIZE_LARGE_CELL))

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
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                    return
                if e.type == pygame.JOYBUTTONDOWN:
                    return

    def on_key_press(self, event):
        if event.type == pygame.KEYDOWN:
            self.play_1_player_button.clicked()

    def on_joy_button_down(self, event):
        if event.button == 4:
            self.app.stop()
        if event.button == 6:
            self.selected = (self.selected + 1) % self.count_select
            print(self.selected)
            # self.select_image.set_pos((SIZE_LARGE_CELL * 4, SIZE_LARGE_CELL * 7.5))\
        elif event.button == 7:
            if self.selected == 0:
                self.play_1_player_button.clicked()
            elif self.selected == 1:
                self.play_2_player_button.clicked()
