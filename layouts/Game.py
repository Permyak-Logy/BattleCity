from engine import Application, Layout
from math import sqrt
from typing import Union, Literal

from widgets import *
from const import *
from extra import *

import pygame
import json


class Game(Layout):
    count_tanks_labels: list
    life_player_1: PDisplayNumber
    life_player_2: PDisplayNumber

    def __init__(self, application: Application, layout_config_filename: str = None):
        super().__init__(application, layout_config_filename=layout_config_filename)
        self.global_data = {}
        self.level_data = {}
        self.level_finished = True

        # Все необходимые группы
        self.all_sprites = pygame.sprite.Group()
        self.collision_moving_group = pygame.sprite.Group()
        self.collision_bullet_group = pygame.sprite.Group()

        self.character_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.headquarters_group = pygame.sprite.Group()

        self.bullet_group = pygame.sprite.Group()

        self.brick_wall_group = pygame.sprite.Group()
        self.concrete_wall_group = pygame.sprite.Group()
        self.bushes_group = pygame.sprite.Group()
        self.water_group = pygame.sprite.Group()
        self.ice_group = pygame.sprite.Group()
        self.unbreakable_wall_group = pygame.sprite.Group()

        self.effects_group = pygame.sprite.Group()
        self.spawn_group = pygame.sprite.Group()
        self.bonuses_group = pygame.sprite.Group()

        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса"""

        img_background_right_label = pygame.Surface(size=(100, HEIGHT_W * 2))
        img_background_right_label.fill(BG_COLOR)

        background_right_label = PLabel(layout=self)
        background_right_label.resize((100, HEIGHT_W * 2))
        background_right_label.set_pos((WIDTH_W - 50, 0))
        background_right_label.set_bg_image(img_background_right_label)
        background_right_label.flip()
        self.add_widget(background_right_label)

        icon_tank = pygame.Surface(size=(1, 1))
        icon_tank.fill((100, 0, 0))
        self.count_tanks_labels = [
            PLabel().set_bg_image(icon_tank).resize(
                (SIZE_SMALL_CELL, SIZE_SMALL_CELL)).set_pos(
                (WIDTH_W - int(SIZE_SMALL_CELL * 3.5) + SIZE_SMALL_CELL * (i % 2),
                 70 + SIZE_SMALL_CELL * (i // 2))).set_font(pygame.font.Font(None, 20)).flip()
            for i in range(20)
        ]
        self.add_widgets(*self.count_tanks_labels)

        self.life_player_1 = PDisplayNumber(self, Animation.cut_sheet(
            load_image("data\\image\\numbers.png"), 5, 2), 3)
        self.life_player_1.set_bg_image(img_background_right_label)
        self.life_player_1.resize(size=(SIZE_SMALL_CELL * 3, SIZE_SMALL_CELL))
        self.life_player_1.set_pos((WIDTH_W - SIZE_SMALL_CELL * 4, 300)).flip()

        self.life_player_2 = PDisplayNumber(self, Animation.cut_sheet(
            load_image("data\\image\\numbers.png"), 5, 2), 3)
        self.life_player_2.set_bg_image(img_background_right_label)
        self.life_player_2.resize(size=(SIZE_SMALL_CELL * 3, SIZE_SMALL_CELL))
        self.life_player_2.set_pos((WIDTH_W - SIZE_SMALL_CELL * 4, 400)).flip()

        self.add_widgets(self.life_player_1, self.life_player_2)

    def render(self, screen: pygame.Surface):
        """Отрисовка всех объектов"""

        if self.image_background:
            screen.blit(self.image_background, (0, 0))  # Накладывет фон

        self.water_group.draw(screen)
        self.ice_group.draw(screen)
        self.spawn_group.draw(screen)
        self.player_group.draw(screen)
        self.enemy_group.draw(screen)
        self.bullet_group.draw(screen)
        self.bushes_group.draw(screen)
        self.headquarters_group.draw(screen)
        self.brick_wall_group.draw(screen)
        self.concrete_wall_group.draw(screen)
        self.bonuses_group.draw(screen)
        self.unbreakable_wall_group.draw(screen)

        self.effects_group.draw(screen)
        self.widget_group.draw(screen)  # Отрисовка анимированных виджетов

    @staticmethod
    def draw_level_number(screen: pygame.Surface, number: int):
        """Отрисовка по середине номера уровня"""

        stage_img = load_image("data\\image\\stage.png", -1)
        numbers_img = Animation.cut_sheet(load_image("data\\image\\numbers.png", -1), columns=5, rows=2)
        surface = pygame.Surface(size=((len(str(number)) + 6) * 8, 8))
        surface.fill(BG_COLOR)
        surface.blit(pygame.transform.scale(stage_img, (8 * 5, 8)), (0, 0))
        for i in range(len(str(number))):
            surface.blit(pygame.transform.scale(numbers_img[int(str(number)[i])], (8, 8)), ((6 + i) * 8, 0))
        surface = pygame.transform.scale(surface, (SIZE_SMALL_CELL * 6 + len(str(number)), SIZE_SMALL_CELL))
        screen.blit(surface,
                    (screen.get_width() // 2 - surface.get_width() // 2,
                     screen.get_height() // 2 - surface.get_height() // 2))

    def init_global_data(self, players_is_2):
        """Инициация глобальных данных"""

        self.global_data["level_index"] = -1

        with open("data\\levels\\data_levels.json", encoding="utf8") as file:
            self.global_data["levels_data"] = json.load(file)["levels"]

        self.global_data["life_player_1"] = 2
        self.global_data["life_player_2"] = 2 if players_is_2 else 0

        self.global_data["player_1_stars"] = 0
        self.global_data["player_2_stars"] = 0

    def init_level_data(self, index: int):
        """Инициация данных о уровне"""

        self.global_data["level_index"] = index
        try:
            self.level_data: dict = self.global_data["levels_data"][index]
        except IndexError:
            # TODO: Экран об окончании прохождения игры сделать
            self.app.stop()
            return

        self.level_data["ready_spawn_enemy"] = 1
        self.level_data["kills"] = {
            0: 0,
            1: 0,
            2: 0,
            3: 0
        }
        self.level_data["type_enemy_tanks"] = {
            0: random.choice([3, 4]),
            1: random.choice([3, 4]),
            2: random.choice([3, 4]),
            3: random.choice([3, 4])
        }
        self.level_data.setdefault('bonuses', 3)
        self.level_data.setdefault('speed_spawn', 0.2)
        self.level_data.setdefault('max_tanks', 10)

    def run_animation_hide_level_map(self):
        """Анимация опускания зановеса"""

        rect: pygame.Rect = self.app.screen.get_rect()
        i = 0
        while i <= 50:
            self.app.clock.tick(60)
            i += 60 / 1000 * 40

            drawings = [
                (0, 0, rect.width, int(rect.height / 100 * i)),
                (0, rect.height - int(rect.height / 100 * i), rect.width, int(rect.height / 100 * i))
            ]
            for pos in drawings:
                pygame.draw.rect(self.app.screen, BG_COLOR, pos)
            pygame.display.flip()

    def run_animation_show_level_map(self):
        """Анимация убирания зановеса"""

        rect: pygame.Rect = self.app.screen.get_rect()
        i = 50
        while i >= 0:
            self.ice_group.update()
            self.water_group.update()
            self.bushes_group.update()
            self.headquarters_group.update()
            self.brick_wall_group.update()
            self.concrete_wall_group.update()
            self.unbreakable_wall_group.update()
            self.app.clock.tick(60)
            i -= 60 / 1000 * 40
            self.app.screen.fill((0, 0, 0))

            self.render(self.app.screen)
            pygame.draw.rect(self.app.screen, BG_COLOR, (0, 0, rect.width, int(rect.height / 100 * i)))
            pygame.draw.rect(self.app.screen, BG_COLOR, (0, rect.height - int(rect.height / 100 * i),
                                                         rect.width, int(rect.height / 100 * i)))
            pygame.display.flip()

        pygame.event.clear()

    def run_animation_lose(self):
        pass

    def run_animation_table_scores(self):
        pass

    def run_animation_game_over(self):
        pass

    def get_player(self, number: Literal[1, 2]):
        """Возвращает игрока с указанным номером"""

        for player in self.player_group.sprites():
            player: Player
            if hasattr(player, 'number') and player.number == number:
                return player

    def get_spawns(self, spawn_class):
        """Возвращает спавн указанного объкта"""

        result = []
        for spawn in self.spawn_group:
            spawn: Spawn
            if spawn.character_class == spawn_class:
                result.append(spawn)
        return result

    @staticmethod
    def load_level(filename: str):
        with open(filename, mode="r") as file:
            data_file = file.readlines()
        data_level = list(map(lambda row: list(row)[:WIDTH_F * 2], data_file[:HEIGHT_F * 2]))
        return data_level

    def next_level(self):
        """Начинает следующий уровень"""

        pygame.mixer.stop()  # Останавливаем музыку

        if self.global_data["level_index"] != -1:
            # Выводим счёт
            self.run_animation_table_scores()

        self.run_animation_hide_level_map()  # Делаем зановес

        # Загружаем уровень
        self.init_level_data(self.global_data["level_index"] + 1)
        self.generate_level(data_level=self.load_level(f"data\\levels\\{self.level_data['filename']}"))

        # Рисуем номер уровня
        self.draw_level_number(self.app.screen, self.global_data["level_index"] + 1)

        # Проигрываем музыку
        pygame.mixer_music.load("data\\music\\MusicStart.mp3")
        pygame.mixer_music.play()

        # Через 2.5 секунды убирем зановес
        self.app.wait(2500)
        self.run_animation_show_level_map()

        # Начинаем игру
        self.level_finished = False

    def generate_level(self, data_level):
        def _can_spawn_player_1(layout: Game) -> bool:
            """Проверка на спавн 1 игрока"""
            return layout.global_data["life_player_1"] > 0 and not bool(layout.get_player(1))

        def _can_spawn_player_2(layout: Game) -> bool:
            """Проверка на спавн 2 игрока"""
            return layout.global_data["life_player_2"] > 0 and not bool(layout.get_player(2))

        def _can_spawn_enemy(layout: Game) -> bool:
            """Проверка на спавн врагов"""
            spawns_active_count = sum(map(lambda s: 1 if s.spawning else 0, layout.get_spawns(Enemy)))
            enemy_count = len(self.enemy_group.sprites())

            flags = (spawns_active_count + enemy_count < layout.level_data['max_tanks'],
                     not random.randint(0, 2),
                     len(layout.level_data["enemies"]) > 0,
                     layout.level_data["ready_spawn_enemy"] >= 1)
            if all(flags):
                layout.level_data["ready_spawn_enemy"] -= 1
            return all(flags)

        self.empty_all_sprites()  # Очищаем все объекты

        # Генерируем непробиваемые стены
        for i in range(-1, WIDTH_F + 1):
            UnbreakableWall(self, (i, -1))
            UnbreakableWall(self, (i, HEIGHT_F))
        for j in range(0, HEIGHT_F + 1):
            UnbreakableWall(self, (-1, j))
            UnbreakableWall(self, (WIDTH_F, j))

        # Генерируем остальное
        for y, row in enumerate(data_level):
            for x, obj_code in enumerate(row):
                if obj_code == '=':
                    ConcreteWall(self, (x / 2, y / 2))
                elif obj_code == '-':
                    BrickWall(self, (x / 2, y / 2))
                elif obj_code == '0':
                    Water(self, (x / 2, y / 2))
                elif obj_code == '#':
                    Bushes(self, (x / 2, y / 2))
                elif obj_code == 'P':
                    spawns_player = self.get_spawns(Player)
                    if len(spawns_player) == 0:
                        Spawn(self, (x / 2, y / 2), Player, _can_spawn_player_1, number=1)
                    elif len(spawns_player) == 1:
                        Spawn(self, (x / 2, y / 2), Player, _can_spawn_player_2, number=2)
                elif obj_code == 'H':
                    Headquarters(self, (x / 2, y / 2))
                elif obj_code == '/':
                    Ice(self, (x / 2, y / 2))
                elif obj_code == 'S':
                    Spawn(self, (x / 2, y / 2), Enemy, _can_spawn_enemy)

        [Bonus(self, (random.randrange(WIDTH_F * 2) / 2, random.randrange(HEIGHT_F * 2) / 2))
         for _ in range(3)]

    def update(self, *args):
        """Обновление каждый tick"""

        if not hasattr(self, "level_data"):
            # Без начатого уровня нет смысла что то проверять
            return

        tick = get_tick(args)

        # Обновляем тайминг спавна врагов
        self.level_data["ready_spawn_enemy"] += self.level_data["speed_spawn"] * tick / 1000
        if self.level_data["ready_spawn_enemy"] > 1:
            self.level_data["ready_spawn_enemy"] = 1

        # Обновляем все объекты
        self.all_sprites.update(tick)
        self.update_right_interface()

        # Проверяем на окончание игры
        if not self.level_finished and (self.check_on_win() or self.check_on_lose()):
            print(self.check_on_win(), self.check_on_lose())
            if self.check_on_lose():
                self.run_animation_game_over()
            self.level_finished = True
            pygame.time.set_timer(EVENT_LEVEL_FINISHED, 5000, True)

    def update_right_interface(self):
        """Обновляет интерфейс справа"""

        icon_ready = pygame.Surface(size=(1, 1))
        icon_ready.fill((0, 255, 0))

        icon_warring = pygame.Surface(size=(1, 1))
        icon_warring.fill(pygame.Color('yellow'))

        icon_death = pygame.Surface(size=(1, 1))
        icon_death.fill((100, 0, 0))

        count_active_spawners = sum(map(lambda s: s.spawning, self.get_spawns(Enemy)))
        for i, widget in enumerate(self.count_tanks_labels):
            if len(self.level_data["enemies"]) - count_active_spawners > i:
                widget.set_bg_image(icon_ready).flip()
            elif len(self.level_data["enemies"]) + len(self.enemy_group.sprites()) > i:
                widget.set_bg_image(icon_warring).flip()
            else:
                widget.set_bg_image(icon_death).flip()

        # Обновляем количество жизней у игрока
        self.life_player_1.set_cur_number(self.global_data['life_player_1']).flip()
        self.life_player_2.set_cur_number(self.global_data['life_player_2']).flip()

    def check_on_win(self) -> bool:
        return len(self.level_data["enemies"]) + sum(map(lambda s: s.spawning, self.get_spawns(Enemy))) == 0

    def check_on_lose(self) -> bool:
        hd = self.headquarters_group.sprites()[0]
        if isinstance(hd, Headquarters) and hd.is_destroy:
            return True
        tanks = len(self.player_group.sprites())
        life = self.global_data['life_player_1'] + self.global_data['life_player_2']
        return not life and not tanks

    def on_open(self, players_is_2=False):
        """Событие вызываемое при открытии этой области"""

        self.init_global_data(players_is_2)
        self.next_level()

    def on_key_press(self, event):
        if self.get_player(1):
            if event.key == pygame.K_w:
                self.get_player(1).set_move(y=-1)
            elif event.key == pygame.K_s:
                self.get_player(1).set_move(y=1)
            elif event.key == pygame.K_a:
                self.get_player(1).set_move(x=-1)
            elif event.key == pygame.K_d:
                self.get_player(1).set_move(x=1)
            elif event.key == pygame.K_SPACE:
                self.get_player(1).attack()

        if self.get_player(2):
            if event.key == pygame.K_UP:
                self.get_player(2).set_move(y=-1)
            elif event.key == pygame.K_DOWN:
                self.get_player(2).set_move(y=1)
            elif event.key == pygame.K_LEFT:
                self.get_player(2).set_move(x=-1)
            elif event.key == pygame.K_RIGHT:
                self.get_player(2).set_move(x=1)
            elif event.key == pygame.K_KP0:
                self.get_player(2).attack()

        if event.key == pygame.K_ESCAPE:
            self.app.stop()

    def on_key_release(self, event):
        if self.get_player(1):
            if event.key == pygame.K_w:
                self.get_player(1).unset_move(y=-1)
            elif event.key == pygame.K_s:
                self.get_player(1).unset_move(y=1)
            elif event.key == pygame.K_a:
                self.get_player(1).unset_move(x=-1)
            elif event.key == pygame.K_d:
                self.get_player(1).unset_move(x=1)

        if self.get_player(2):
            if event.key == pygame.K_UP:
                self.get_player(2).unset_move(y=-1)
            elif event.key == pygame.K_DOWN:
                self.get_player(2).unset_move(y=1)
            elif event.key == pygame.K_LEFT:
                self.get_player(2).unset_move(x=-1)
            elif event.key == pygame.K_RIGHT:
                self.get_player(2).unset_move(x=1)

    def on_other_events(self, event):
        if event.type == EVENT_LEVEL_FINISHED:
            if self.check_on_win():
                self.next_level()
            elif self.check_on_lose():
                self.run_animation_table_scores()
                self.run_animation_lose()
                self.app.stop()

        elif event.type == IMMORTALITY_END_P1:
            player = self.get_player(1)
            if isinstance(player, Player):
                player.set_immortality(False)

        elif event.type == IMMORTALITY_END_P2:
            player = self.get_player(2)
            if isinstance(player, Player):
                player.set_immortality(False)

        elif event.type == FREEZING_END:
            self.level_data["freezing"] = False

    def empty_all_sprites(self):
        """Очищает все спрайты кроме виджетов"""

        self.all_sprites.empty()
        self.all_sprites.copy()
        self.collision_moving_group.empty()
        self.collision_bullet_group.empty()
        self.character_group.empty()
        self.player_group.empty()
        self.enemy_group.empty()
        self.headquarters_group.empty()
        self.bullet_group.empty()
        self.brick_wall_group.empty()
        self.concrete_wall_group.empty()
        self.bushes_group.empty()
        self.water_group.empty()
        self.ice_group.empty()
        self.unbreakable_wall_group.empty()
        self.effects_group.empty()
        self.spawn_group.empty()
        self.bonuses_group.empty()


class Actor(pygame.sprite.Sprite):
    """
    Родительский класс для всех игровых объектов
    """
    hide_default_image = True

    true_x: float
    true_y: float

    cur_animation: str
    cur_animation2 = None
    image: pygame.Surface
    rect: pygame.Rect
    sound_shot = None

    def __init__(self, layout: Game, size=None, pos=(0, 0)):
        super().__init__(layout.all_sprites)
        self.layout = layout
        self.animations = {}
        if not size:
            size = SIZE_LARGE_CELL, SIZE_LARGE_CELL
        # Изображение по умолчанию
        image = pygame.Surface(size=size)
        image.fill(pygame.color.Color('purple'))
        if self.hide_default_image:
            image.set_colorkey(pygame.color.Color('purple'))
        self.rect = image.get_rect()
        self.set_state_image(image)
        self.change_animation("state_0_0_-1")

        self.sight = [0, -1]
        self.is_damaged = False  # Может получать урон?
        self.armor = 0  # Количество поглощаемого урона
        self.max_stars = self.stars = 0  # Звёзды объекта
        self.health = 1

        self.set_pos(pos)

    def __repr__(self):
        return f"{self.__class__.__name__}(x={repr(self.rect.x)} y={repr(self.rect.y)} " \
               f"stars={repr(self.stars)} cur_animation={repr(self.cur_animation)})"

    def init_state_animation(self, sheet: pygame.Surface, columns=1, rows=1, star=0):
        animations = Animation.create_in_all_directions(sheet, columns=columns, rows=rows)
        self.animations[f"state_{star}_0_-1"] = animations[0]
        self.animations[f"state_{star}_-1_0"] = animations[1]
        self.animations[f"state_{star}_0_1"] = animations[2]
        self.animations[f"state_{star}_1_0"] = animations[3]

    def set_image(self, image: pygame.Surface):
        self.image = pygame.transform.scale(image, (self.rect.width, self.rect.height))

    def set_state_image(self, image: pygame.Surface):
        self.set_image(image)
        self.animations["state_0_0_-1"] = Animation(image, 1, 1)

    def set_pos(self, pos: tuple):
        """Устанавливает позиции на сетке карты по большим квадратам"""
        x = pos[0] * SIZE_LARGE_CELL + LEFT
        y = pos[1] * SIZE_LARGE_CELL + TOP
        self.set_coords(x, y)

    def set_coords(self, x: float, y: float):
        """Устанавливает координаты отностительно окна"""

        self.true_x, self.true_y = x, y
        self.rect.x, self.rect.y = int(self.true_x), int(self.true_y)

    def add_coords(self, x: float, y: float):
        self.set_coords(self.true_x + x, self.true_y + y)

    def half_damage(self, damage, passage):
        """Получение урона"""
        if self.sound_shot:
            self.sound_shot.play()

        if not self.is_damaged:
            return
        if passage < self.armor:
            return
        self.health -= damage

    def change_animation(self, key, discharge_old=False):
        if key not in self.animations.keys():
            raise ValueError(f"Анимации {key} у объекта не существует")

        if discharge_old:
            self.animations[self.cur_animation].discharge()

        self.cur_animation = key

    def change_animation2(self, key, discharge_old=False):

        if key not in self.animations.keys() and key is not None:
            raise ValueError(f"Анимации {key} у объекта не существует")

        if discharge_old:
            self.animations[self.cur_animation].discharge()

        self.cur_animation2 = key

    def update(self, *args):
        tick = get_tick(args)
        try:
            self.change_animation(f"state_{self.stars}_{self.sight[0]}_{self.sight[1]}")
        except ValueError:
            try:
                self.change_animation(f"state_0_{self.sight[0]} {self.sight[1]}")
            except ValueError:
                self.change_animation(f"state_0_0_-1")
        self.update_animation(tick)
        if self.is_damaged and self.health <= 0:
            self.kill()

    def update_animation(self, tick):
        anim: Animation = self.animations[self.cur_animation]
        anim.update(tick)
        anim.draw(self)

        anim2 = self.animations.get(self.cur_animation2)
        if anim2:
            anim2.update(tick)
            anim2.draw(self)

    def get_center(self):
        return self.rect.centerx, self.rect.centery

    def get_cell(self):
        coords = self.rect.x, self.rect.y
        return (coords[0] - TOP) / SIZE_LARGE_CELL, \
               (coords[1] - LEFT) / SIZE_LARGE_CELL

    def get_coords(self):
        return self.rect.x, self.rect.y

    def get_distance(self, other, as_cells=True) -> float:
        if as_cells:
            xya, xyb = self.get_cell(), other.get_cell()
        else:
            xya, xyb = self.get_center(), other.get_center()
        return sqrt((xya[0] - xyb[0]) ** 2 + (xya[1] - xyb[1]) ** 2)


class Animation:
    def __init__(self, sheet=pygame.Surface(size=(1, 1)), columns=1, rows=1, transform_data=None):
        self.frames_run = self.cut_sheet(sheet, columns, rows, transform_data)
        self.cur_index = 0.
        self.speed = 1.
        self.speed_m = 5.7
        self.rep = 0
        self.max_rep = -1

        # Тип наложения анимации: "f" заменяет картинку, "b" накладывает поверх
        self.type_drawing = "f"

        # Параметры при типе анимации "b"
        self.pos = (0, 0)  # Отступ на картинке от левого верхнего угла
        self.size = -1  # Размер накладываемого кадра

    def __repr__(self):
        return f"{self.__class__.__name__}(speed={repr(self.speed)} " \
               f"max_rep={repr(self.max_rep)} screens={repr(len(self))})"

    def __len__(self):
        return len(self.frames_run)

    def __add__(self, other):
        pass

    def set_max_rep(self, val):
        self.max_rep = val
        return self

    def set_type(self, val: str):
        if val not in ["b", "f"]:
            raise ValueError(f"Типа анимации {val} не существует")
        self.type_drawing = val
        return self

    def set_size(self, size):
        pass

    def set_pos(self, pos: tuple):
        self.pos = pos

    def discharge(self):
        self.cur_index = 0
        self.rep = 0

    def update(self, *args):
        if self.rep != self.max_rep:
            tick = get_tick(args)
            self.cur_index += (tick / 1000) * self.speed * self.speed_m
            if self.cur_index >= len(self):
                self.cur_index %= len(self)
                self.rep += 1
            if self.rep == self.max_rep:
                self.cur_index = -1

    def set_speed(self, val: float):
        self.speed = val
        return self

    def set_speed_m(self, val: float):
        self.speed_m = val
        return self

    def draw(self, actor: Actor):
        if self.type_drawing == "b":
            if self.size == -1:
                size = actor.rect.size
            else:
                size = self.size
            actor.image.blit(pygame.transform.scale(self.get_screen(), size), self.pos)
        elif self.type_drawing == "f":
            actor.set_image(self.get_screen())

    def get_screen(self):
        return self.frames_run[int(self.cur_index)]

    @staticmethod
    def zip(*animations):
        result = []
        for i in zip(*list(map(lambda x: x.frames_run, animations))):
            result += list(i)
        new_a = Animation()
        new_a.frames_run = result
        return new_a

    @staticmethod
    def cut_sheet(sheet: pygame.Surface, columns: int, rows: int, transform_data=None):
        """Разделение доски анимации и возвращение списка кадров"""

        listen = []
        rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                           sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (rect.w * i, rect.h * j)
                image = sheet.subsurface(
                    pygame.Rect(frame_location, rect.size)
                )
                if transform_data:
                    image = pygame.transform.flip(
                        image, *transform_data.get("flip", (False, False))
                    )
                    image = pygame.transform.rotate(
                        image, transform_data.get("rotate", 0)
                    )
                listen.append(image)

        return listen

    def set_sheet(self, sheet: list):
        self.frames_run = sheet
        self.cur_index = 0

    @staticmethod
    def create_in_all_directions(sheet: pygame.Surface, columns=1, rows=1):
        """Возвращает анимации по направлениям WASD соответственно"""
        return (
            Animation(sheet, columns, rows, {"rotate": 0, "flip": (False, False)}),
            Animation(sheet, columns, rows, {"rotate": 270, "flip": (False, True)}),
            Animation(sheet, columns, rows, {"rotate": 0, "flip": (False, True)}),
            Animation(sheet, columns, rows, {"rotate": 90, "flip": (True, True)})
        )


class Character(Actor):
    """
    Игровые персонажи
    """

    def __init__(self, layout: Game, size=None, pos=(0, 0), stars=0):
        super().__init__(layout, size=size, pos=pos)
        self.add(
            layout.character_group,
            layout.collision_moving_group,
            layout.collision_bullet_group
        )

        self.init_state_animation(self.image, 1, 1, 0)
        self.init_moving_animation(self.image, 1, 1, 0)
        self.animations["immortality"] = Animation(load_image("data\\image\\immortality.png", -1), 2, 1)
        self.animations["immortality"].set_type("b")
        self.animations["immortality"].set_speed(5)

        self.moving = [0, 0]
        self.travel_speed = 1
        self.max_stars = stars

        self.delta_aligh = 0.2
        self.delta_aligh_on_ice = 0.1

        self.max_bullets = 1
        self.bullets_ready = 0
        self.charging_rate = 1.2

        self.sound_attack = pygame.mixer.Sound("data\\music\\Shot.wav")
        self.sound_state = pygame.mixer.Sound("data\\music\\State.wav")
        self.sound_moving = pygame.mixer.Sound("data\\music\\Moving.wav")
        self.sound_half_damage = pygame.mixer.Sound("data\\music\\ShotConcreteWall.wav")
        self.sound_explosion_tank = pygame.mixer.Sound("data\\music\\ExplosionTank.wav")

        self.sound_channel = None

    def init_moving_animation(self, sheet: pygame.Surface, columns=1, rows=1, star=0):
        animations = Animation.create_in_all_directions(sheet, columns, rows)
        self.animations[f"moving_{star}_0_-1"] = animations[0].set_speed(2)
        self.animations[f"moving_{star}_-1_0"] = animations[1].set_speed(2)
        self.animations[f"moving_{star}_0_1"] = animations[2].set_speed(2)
        self.animations[f"moving_{star}_1_0"] = animations[3].set_speed(2)

    def set_null_move(self):
        self.unset_move(self.moving[0], self.moving[1])

    def half_damage(self, damage, passage):
        if not self.is_damaged:
            return
        if passage < self.armor:
            return

        if self.stars >= 3 and self.health >= 2:
            self.down_level()
        else:
            self.health -= 1
        if self.health >= 0 and self.sound_channel is not None:
            self.sound_channel.play(self.sound_half_damage)

    def kill(self):
        if self.sound_channel is not None:
            self.sound_channel.stop()
        self.sound_explosion_tank.play()
        BigBang(self.layout, self.get_center())
        return super().kill()

    def can_attack(self) -> bool:
        if self.stars < 0:
            return False
        if self.bullets_ready < 1:
            return False
        if len(list(filter(lambda x: x.sender == self, self.layout.bullet_group.sprites()))) >= self.max_bullets:
            return False
        return True

    def on_ice(self):
        return pygame.sprite.spritecollideany(self, self.layout.ice_group)

    def align(self):
        nx = (self.rect.x - TOP) // SIZE_SMALL_CELL * SIZE_SMALL_CELL + TOP
        ny = (self.rect.y - LEFT) // SIZE_SMALL_CELL * SIZE_SMALL_CELL + LEFT

        delta = self.delta_aligh if not self.on_ice() else self.delta_aligh_on_ice

        if self.rect.x - nx <= delta * SIZE_SMALL_CELL:
            self.set_coords(nx, self.rect.y)
        elif self.rect.x - nx >= (1 - delta) * SIZE_SMALL_CELL:
            self.set_coords(nx + SIZE_SMALL_CELL, self.rect.y)

        if self.rect.y - ny <= delta * SIZE_SMALL_CELL:
            self.set_coords(self.rect.x, ny)
        elif self.rect.y - ny >= (1 - delta) * SIZE_SMALL_CELL:
            self.set_coords(self.rect.x, ny + SIZE_SMALL_CELL)

    def attack(self):
        """Выстрел"""
        if not self.can_attack():
            return

        damage = 1 if self.stars < 3 else 2
        passage = 0 if self.stars < 3 else 1
        k_speed = 5 if self.stars < 1 else 7

        self.sound_attack.play()

        Bullet(self.layout, sender=self, damage=damage, k_speed=k_speed, passage=passage)
        self.bullets_ready -= 1

    def get_moving(self, tick):  # Перемещение
        m = 1 if not self.on_ice() else random.randint(8, 20) / 10
        return tick / 1000 * SIZE_LARGE_CELL * self.travel_speed * m

    def move_up(self, tick):
        """Движение вверх"""

        self.true_y -= self.get_moving(tick)  # Установка новых истенных координат
        self.rect.y = int(self.true_y)  # Установка новых координат квадрата
        if self not in self.layout.collision_moving_group.sprites():
            return
        # Получения списка стен с которыми персонаж пересёкся
        sprite_list = pygame.sprite.spritecollide(self, self.layout.collision_moving_group, False)
        if self in sprite_list:
            sprite_list.remove(self)
        if sprite_list:
            # Если было пересечение то перемещение песонажа на максимально маленькое растояние
            self.rect.y = self.true_y = sprite_list[0].rect.y + sprite_list[0].rect.size[1]

    def move_down(self, tick):
        """Движение вниз"""

        self.true_y += self.get_moving(tick)  # Установка новых истенных координат
        self.rect.y = int(self.true_y)  # Установка новых координат квадрата
        if self not in self.layout.collision_moving_group.sprites():
            return
        # Получения списка стен с которыми персонаж пересёкся
        sprite_list = pygame.sprite.spritecollide(self, self.layout.collision_moving_group, False)
        if self in sprite_list:
            sprite_list.remove(self)
        if sprite_list:
            # Если было пересечение то перемещение песонажа на максимально маленькое растояние
            self.rect.y = self.true_y = sprite_list[0].rect.y - self.rect.size[1]

    def move_left(self, tick):
        """Движение вправо"""

        self.true_x -= self.get_moving(tick)  # Установка новых истенных координат
        self.rect.x = int(self.true_x)  # Установка новых координат квадрата
        if self not in self.layout.collision_moving_group.sprites():
            return
        # Получения списка стен с которыми персонаж пересёкся
        sprite_list = pygame.sprite.spritecollide(self, self.layout.collision_moving_group, False)
        if self in sprite_list:
            sprite_list.remove(self)
        if sprite_list:
            # Если было пересечение то перемещение песонажа на максимально маленькое растояние
            self.rect.x = self.true_x = sprite_list[0].rect.x + sprite_list[0].rect.size[0]

    def move_right(self, tick):
        """Движение влево"""

        self.true_x += self.get_moving(tick)  # Установка новых истенных координат
        self.rect.x = int(self.true_x)  # Установка новых координат квадрата
        if self not in self.layout.collision_moving_group.sprites():
            return
        # Получения списка стен с которыми персонаж пересёкся
        sprite_list = pygame.sprite.spritecollide(self, self.layout.collision_moving_group, False)
        if self in sprite_list:
            sprite_list.remove(self)
        if sprite_list:
            # Если было пересечение то перемещение песонажа на максимально маленькое растояние
            self.rect.x = self.true_x = sprite_list[0].rect.x - self.rect.size[0]

    def set_move(self, x=0, y=0):
        if not isinstance(x, int):
            raise TypeError(f'x is not "int" (got type "{type(x)}")')
        if not isinstance(y, int):
            raise TypeError(f'y is not "int" (got type "{type(y)}"')

        if not self.moving[0] == self.moving[1] == 0:
            return False

        if x != 0:
            self.moving[0] = x // abs(x)
        elif y != 0:
            self.moving[1] = y // abs(y)
        return True

    def unset_move(self, x=0, y=0):
        if not isinstance(x, int):
            raise TypeError(f'x is not "int" (got type "{type(x)}")')
        if not isinstance(y, int):
            raise TypeError(f'y is not "int" (got type "{type(y)}"')

        if self.moving[0] == self.moving[1] == 0:
            return False

        if self.moving[0] == x != 0:
            self.moving[0] = 0
        elif self.moving[1] == y != 0:
            self.moving[1] = 0
        else:
            return False
        self.align()
        return True

    def up_level(self, value=1):
        if value < 0:
            raise ValueError("not value >= 0")

        if self.stars == self.max_stars:
            return
        if self.stars <= 1 and self.stars + value >= 2:
            self.max_bullets += 2
            self.bullets_ready += 2
        if self.stars <= 2 and self.stars + value >= 3:
            self.health += 1

        self.stars += value
        if self.stars > self.max_stars:
            self.stars = self.max_stars

    def down_level(self, value=1):
        if value < 0:
            raise ValueError("not value >= 0")

        if self.stars >= 2 and self.stars - value <= 1:
            self.max_bullets -= 2
            if self.bullets_ready > 1:
                self.bullets_ready = 1

        if self.stars >= 3 and self.stars - value <= 2:
            self.health -= 1

        self.stars -= value

    def update(self, *args):
        tick = get_tick(args)

        if self.is_damaged and self.health <= 0:
            self.kill()
            return

        if isinstance(self, Enemy) and self.layout.level_data.get("freezing"):
            pass
        elif self.moving[1] == -1:
            self.sight[0], self.sight[1] = 0, -1
            self.move_up(tick)
        elif self.moving[1] == 1:
            self.sight[0], self.sight[1] = 0, 1
            self.move_down(tick)
        elif self.moving[0] == -1:
            self.sight[0], self.sight[1] = -1, 0
            self.move_left(tick)
        elif self.moving[0] == 1:
            self.sight[0], self.sight[1] = 1, 0
            self.move_right(tick)

        if self.moving[0] == self.moving[1] == 0:
            if hasattr(self, 'bonus') and self.bonus:
                self.change_animation(f"state_bonus_{self.sight[0]}_{self.sight[1]}")
            else:
                self.change_animation(f"state_{self.stars}_{self.sight[0]}_{self.sight[1]}")
            if self.sound_channel is not None:
                if self.sound_channel.get_sound() != self.sound_state:
                    self.sound_channel.play(self.sound_state)
        else:
            if hasattr(self, 'bonus') and self.bonus:
                self.change_animation(f"moving_bonus_{self.sight[0]}_{self.sight[1]}")
            else:
                self.change_animation(f"moving_{self.stars}_{self.sight[0]}_{self.sight[1]}")
            if self.sound_channel is not None:
                if self.sound_channel.get_sound() != self.sound_moving:
                    self.sound_channel.play(self.sound_moving)

        self.bullets_ready += self.charging_rate * tick / 1000
        if self.bullets_ready > self.max_bullets:
            self.bullets_ready = self.max_bullets

        self.update_animation(tick)


class Player(Character):
    def __init__(self, layout: Game, pos=(0, 0), number=1):
        super().__init__(layout, pos=pos, stars=3)
        self.add(layout.player_group)
        if NO_COLLISION_FOR_PLAYERS:
            self.remove(layout.collision_moving_group)
        self.number = number

        self.up_level(self.layout.global_data.get(f"player_{number}_stars", 0))
        self.is_damaged = True

        for star in range(0, self.max_stars + 1):
            self.init_state_animation(load_image(f"data\\image\\tank_{number}_state_{star}.png", -1),
                                      star=star)
            self.init_moving_animation(load_image(f"data\\image\\tank_{number}_moving_{star}.png", -1),
                                       star=star, columns=2, rows=1)
        self.travel_speed = 3
        self.charging_rate = 10
        self.up_level(3)

        self.sound_channel = pygame.mixer.Channel(number)
        self.set_immortality(True, delay=5)

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"x={self.rect.x} " \
               f"y={self.rect.y} " \
               f"stars={self.stars} " \
               f"cur_animation={self.cur_animation} " \
               f"number={self.number})"

    def set_immortality(self, toggle: bool, delay=0.0):
        self.is_damaged = not toggle
        if not self.is_damaged:
            self.change_animation2("immortality")
            if self.number == 1:
                pygame.time.set_timer(IMMORTALITY_END_P1, int(delay * 1000), True)
            elif self.number == 2:
                pygame.time.set_timer(IMMORTALITY_END_P2, int(delay * 1000), True)
        else:
            self.change_animation2(None)

    def up_level(self, value=1):
        super().up_level(value)
        self.layout.global_data[f"player_{self.number}_stars"] = self.stars if self.stars >= 0 else 0

    def down_level(self, value=1):
        super().down_level(value)
        self.layout.global_data[f"player_{self.number}_stars"] = self.stars if self.stars >= 0 else 0

    def kill(self):
        self.layout.global_data[f"life_player_{self.number}"] -= 1
        self.layout.global_data[f"player_{self.number}_stars"] = 0
        super().kill()


class Enemy(Character):
    assets = {
        0: {
            "name": 0,
            "stars": 0,
            "images_state": [("data\\image\\tank_4_state_0.png", 1, 1)],
            "images_moving": [("data\\image\\tank_4_moving_0.png", 2, 1)],
            "travel_speed": 1.5,
            "max_bullets": 1
        }, 1: {
            "name": 1,
            "stars": 0,
            "images_state": [("data\\image\\tank_4_state_1.png", 1, 1)],
            "images_moving": [("data\\image\\tank_4_moving_1.png", 2, 1)],
            "travel_speed": 5,
            "max_bullets": 1
        }, 2: {
            "name": 2,
            "stars": 0,
            "images_state": [("data\\image\\tank_4_state_2.png", 1, 1)],
            "images_moving": [("data\\image\\tank_4_moving_2.png", 2, 1)],
            "travel_speed": 2,
            "max_bullets": 3
        }, 3: {
            "name": 3,
            "stars": 3,
            "images_state": [(f"data\\image\\tank_3_state_{star}.png", 1, 1)
                             for star in range(4)],
            "images_moving": [(f"data\\image\\tank_3_moving_{star}.png", 2, 1)
                              for star in range(4)],
            "travel_speed": 1,
            "max_bullets": 1
        }
    }

    def __init__(self, layout: Game, pos=(0, 0)):
        self._debug_info = False
        self.asset = self.assets[layout.level_data["enemies"].pop(
            random.randint(0, len(layout.level_data["enemies"]) - 1))]

        super().__init__(layout, pos=pos, stars=self.asset["stars"])
        self.add(layout.enemy_group)
        self.is_damaged = True
        self.bonus = False
        self.priority_player = [1, 2]
        random.shuffle(self.priority_player)

        self.delta_aligh = 0.1
        self.delta_aligh_on_ice = 0.1
        self.set_asset()

        for star in range(0, self.max_stars + 1):
            filename_image_state, *cut_image_state = self.asset["images_state"][star]
            self.init_state_animation(
                load_image(filename_image_state, -1), star=star,
                columns=cut_image_state[0], rows=cut_image_state[1]
            )

            filename_image_moving, *cut_image_moving = self.asset["images_moving"][star]
            self.init_moving_animation(
                load_image(filename_image_moving, -1), star=star,
                columns=cut_image_moving[0], rows=cut_image_moving[1]
            )

        self.tasks = {}

        self.time_reset_tasks = 10
        self.readiness_reset_tasks = 0
        self.count_fails_auto_create_tasks = 0

        self.skip = False

    def attack(self):
        if not self.can_attack():
            return

        Bullet(self.layout, self, self.asset.get("damage", 1), self.asset.get("k_speed", 5))
        self.bullets_ready -= 1

    def half_damage(self, damage, passage):
        if not self.is_damaged:
            return
        if damage <= self.armor:
            return

        self.down_level()
        if self.health >= 0 and self.sound_channel is not None:
            self.sound_channel.play(self.sound_half_damage)

    def down_level(self, value=1):
        if value < 0:
            raise ValueError("not value >= 0")
        self.stars -= value
        if self.stars < 0:
            self.health -= 1

    def up_level(self, value=1):
        # Следует лишь 1 раз её вызывать
        if value < 0:
            raise ValueError("not value >= 0")
        self.stars += value
        if self.stars > self.max_stars:
            self.stars = self.max_stars

    def set_asset(self):
        self.stars = self.asset["stars"]
        self.travel_speed = self.asset["travel_speed"]

        self.max_bullets = self.asset.get("max_bullets", self.max_bullets)
        self.charging_rate = self.asset.get("charging_rate", self.charging_rate)

    def kill(self):
        self.layout.level_data["kills"][self.asset["name"]] += 1
        Score(self.layout, self.get_center(), score=(self.asset["name"] + 1) * 100)
        return super().kill()

    def update(self, *args):
        super().update(*args)
        if self.layout.level_data.get("freezing"):
            return
        tick = get_tick(args)

        if self.bullets_ready and random.random() <= 0.5 and self.tasks:
            self.attack()

        self.update_tasks(tick)

    def clean_tasks(self, key=lambda t: not t["complete"], clean_null=True):
        deletes = set()
        for k in self.tasks.keys():
            self.tasks[k] = list(filter(key, self.tasks[k]))
            if not self.tasks[k] and clean_null:
                deletes.add(k)
        for k in deletes:
            del self.tasks[k]

    def auto_create_tasks(self):
        if not self.tasks:
            self.create_task_random_moving()

    def update_tasks(self, *args):
        tick = get_tick(args)

        self.auto_create_tasks()

        can_level_cal = self.get_can_level_cal()
        for level, tasks in self.tasks.items():
            for i, task in enumerate(tasks):
                task["context"]["__tick__"] = tick
                task["context"]["__i__"] = i
                if task["is_complete"](task["context"]):
                    print(f"complete task \"{task['name']}\"")
                    task["complete"] = True

                if level != can_level_cal:
                    continue
                if task["complete"]:
                    continue
                if not task["check"](task["context"]):
                    continue
                task["update"](task["context"])
        self.clean_tasks()

    def get_can_level_cal(self) -> int:
        if not self.tasks.keys():
            return -1
        return max(self.tasks.keys(),
                   key=lambda k: (
                       any(map(lambda t: t["check"](t["context"]), self.tasks[k])),
                       k
                   ))

    def get_task(self, name):
        for tasks in self.tasks.values():
            for task in tasks:
                if task["name"] == name:
                    return task

    def pop_task(self, name):
        task_index = None
        for tasks in self.tasks.values():
            for i, task in enumerate(tasks):
                if task["name"] == name:
                    task_index = i
                    break
            if task_index is not None:
                return tasks.pop(task_index)

    def create_task(self, name="", **params):
        context = params.pop("context", {})
        update = params.pop("update", lambda *args, **kwargs: False)
        check = params.pop("check", lambda *args, **kwargs: True)
        is_complete = params.pop("is_complete", lambda *args, **kwargs: False)
        complete = params.pop("complete", False)
        priority_level = params.pop("priority_level", 0)

        context["__obj__"] = self

        if params:
            raise ValueError(f"Кароче лишние параметры указаны... {params}")

        task = {
            "name": name,
            "context": context,
            "update": update,
            "check": check,
            "is_complete": is_complete,
            "priority_level": 0,
            "complete": complete
        }

        if priority_level not in self.tasks.keys():
            self.tasks[priority_level] = []
        self.tasks[priority_level].append(task)

        print(f"create task \"{task['name']}\"")

    def create_task_destroy(self, target: Union[Actor, pygame.sprite.Sprite, None], max_rad_att=REVIEW_RADIUS_ENEMY,
                            priority_level=0):
        if target is None:
            return

        def update(context: dict):
            obj: Enemy = context["__obj__"]
            self.set_null_move()
            target_pos = context["target"].get_center()
            self_pos = obj.get_center()
            if abs(target_pos[0] - self_pos[0]) > abs(target_pos[1] - self_pos[1]):
                obj.sight = [get_m(target_pos[0] - self_pos[0]), 0]
            else:
                obj.sight = [0, get_m(target_pos[1] - self_pos[1])]

        def check(context: dict) -> bool:
            obj: Enemy = context["__obj__"]
            if not context["max_rat_att"] + 1 > obj.get_distance(context["target"]):
                return False

            target_cell = context["target"].get_cell()
            self_cell = obj.get_cell()
            if not (abs(self_cell[0] - target_cell[0]) <= 0.5 or abs(self_cell[1] - target_cell[1]) <= 0.5):
                return False
            return True

        def is_complete(context: dict) -> bool:
            return not context["target"] or not context["target"].alive()

        self.create_task(
            name=f"destroy {target}",
            context={"max_rat_att": max_rad_att, "target": target},
            check=check,
            update=update,
            is_complete=is_complete,
            priority_level=priority_level
        )

    def create_task_random_moving(self, priority_level=0):
        def update(context: dict):
            tick = context['__tick__']
            enemy: Enemy = context['__obj__']
            me_coords = enemy.get_coords()
            if context['old_coords'] != me_coords:
                context['old_coords'] = me_coords
                context['readiness_change_dir'] = 0
            else:
                context['readiness_change_dir'] += (1 / context['max_time_wait']) * (tick / 1000)
                if context['max_time_wait'] <= context['readiness_change_dir'] or random.random() <= 0.01:
                    context['readiness_change_dir'] = 0
                    context['cur_dir'] = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                    context['max_time_wait'] = random.randint(1, 10) / 10
                    enemy.set_null_move()
                    enemy.set_move(*context['cur_dir'])

        self.create_task(
            name=f"random moving",
            context={"target_cell": self.get_cell(), "old_coords": self.get_coords(),
                     "cur_dir": (0, 0), "max_time_wait": 1, "readiness_change_dir": 0},
            update=update,
            priority_level=priority_level
        )


class BrickWall(Actor):
    def __init__(self, layout, pos):
        size = SIZE_SMALL_CELL, SIZE_SMALL_CELL
        super().__init__(layout, pos=pos, size=size)
        self.add(
            layout.brick_wall_group,
            layout.collision_moving_group,
            layout.collision_bullet_group
        )
        self.set_state_image(load_image("data\\image\\brick_wall.png"), )

        self.is_damaged = True
        self.stars = 1
        self.armor = 0

        # self.sound_shot = pygame.mixer.Sound("data\\music\\ShotBrickWall.wav")


class ConcreteWall(Actor):
    def __init__(self, layout, pos):
        size = SIZE_SMALL_CELL, SIZE_SMALL_CELL
        super().__init__(layout, pos=pos, size=size)
        self.add(
            layout.concrete_wall_group,
            layout.collision_moving_group,
            layout.collision_bullet_group
        )
        self.set_state_image(load_image("data\\image\\concrete_wall.png"))

        self.is_damaged = True
        self.stars = 0
        self.armor = 1

        self.sound_shot = pygame.mixer.Sound("data\\music\\ShotConcreteWall.wav")


class BonusConcreteWall(ConcreteWall):
    # TODO: Баг с положением
    def __init__(self, layout, pos):
        super().__init__(layout, pos)
        self.delay = 10
        a = self.animations[self.cur_animation]
        a.set_speed(1)
        a.set_speed_m(1)

    def update(self, *args):
        super().update(*args)
        if self.animations[self.cur_animation].rep >= 20:
            self.kill()


class Bushes(Actor):
    def __init__(self, layout, pos):
        size = SIZE_SMALL_CELL, SIZE_SMALL_CELL
        super().__init__(layout, pos=pos, size=size)
        self.add(layout.bushes_group)
        self.set_state_image(load_image("data\\image\\bushes.png", -1))


class Water(Actor):
    def __init__(self, layout, pos):
        size = SIZE_SMALL_CELL, SIZE_SMALL_CELL
        super().__init__(layout, pos=pos, size=size)
        self.add(layout.water_group, layout.collision_moving_group)
        self.init_state_animation(load_image("data\\image\\water.png"), columns=3, rows=1, star=0)


class Ice(Actor):
    def __init__(self, layout, pos):
        size = SIZE_SMALL_CELL, SIZE_SMALL_CELL
        super().__init__(layout, pos=pos, size=size)
        self.add(layout.ice_group)
        self.init_state_animation(load_image("data\\image\\ice.png"))


class Headquarters(Actor):
    def __init__(self, layout: Game, pos):
        super().__init__(layout, pos=pos)
        self.add(layout.headquarters_group, layout.collision_bullet_group, layout.collision_moving_group)
        self.animations["state_-1_0_-1"] = Animation(load_image("data\\image\\destroyed_headquarters.png", -1))
        self.animations["state_0_0_-1"] = Animation(load_image("data\\image\\headquarters.png", -1))
        self.is_damaged = True
        self.is_destroy = False

    def update(self, *args):
        tick = get_tick(args)
        if self.stars < 0 and self.is_damaged:
            self.is_damaged = False
            self.change_animation(f"state_-1_0_-1")
            BigBang(self.layout, self.get_center())
            # pygame.time.set_timer(EVENT_LEVEL_FINISHED, 5 * 1000)
            self.remove(self.layout.collision_bullet_group)
            self.is_destroy = True

        elif self.is_damaged:
            self.change_animation(f"state_{self.stars}_{self.sight[0]}_{self.sight[1]}")
        self.update_animation(tick)


class UnbreakableWall(Actor):
    def __init__(self, layout: Game, pos):
        super().__init__(layout, pos=pos)
        self.add(layout.unbreakable_wall_group, layout.collision_moving_group, layout.collision_bullet_group)
        image = pygame.Surface(size=(1, 1))
        image.fill(BG_COLOR)
        self.animations["state_0_0_-1"] = Animation(image)


class Bullet(Actor):
    """
    Снаряды выпускаемые персонажами
    """

    directory_configs = 'data\\actors\\bullet'

    def __init__(self, layout: Game, sender: Character, damage: int, k_speed: int, passage: int = 0):
        # Получение конфига генирации. Если generation_key == None то берётся случайный из доступных
        size = int(SIZE_SMALL_CELL * 0.5), int(SIZE_SMALL_CELL * 0.5)
        super().__init__(layout, size=size)
        self.add(layout.bullet_group, layout.collision_bullet_group)
        self.is_damaged = True

        self.init_state_animation(load_image("data\\image\\bullet.png", -1))
        self.change_animation(f"state_{self.stars}_{sender.sight[0]}_{sender.sight[1]}")

        # Перемещаем снаряд в его 0-ое положение
        self.set_coords(
            sender.rect.x + (sender.sight[0] + 1) * (sender.rect.w // 2) - self.rect.w // 2,
            sender.rect.y + (sender.sight[1] + 1) * (sender.rect.h // 2) - self.rect.h // 2
        )

        self.damage = damage  # Урон
        self.sender = sender  # Отправитель
        self.k_speed = k_speed  # Множитель скорости полёта
        self.passage = passage  # Пробитие

        # Направления скоростей снаряда
        self.vx, self.vy = sender.sight.copy()

    def update(self, *args):
        """Обновление"""

        if self.is_damaged and self.stars < 0:
            self.kill()

        tick = get_tick(args)
        self.update_animation(tick)
        self.set_coords(
            self.true_x + (tick / 1000) * SIZE_LARGE_CELL * self.vx * self.k_speed,
            self.true_y + (tick / 1000) * SIZE_LARGE_CELL * self.vy * self.k_speed
        )

        # Получение целей которым можно нанести урон
        actors = pygame.sprite.spritecollide(self, self.layout.collision_bullet_group, False)
        actors.remove(self.sender) if self.sender in actors else None
        actors.remove(self) if self in actors else None

        killed, show_explosion = False, True
        if actors:  # Если попали то наносим им урон
            for sprite in actors:
                sprite: Actor

                if isinstance(self.sender, Player):
                    # Ломаемся обовсё но наносим урон только не своим объектам
                    if not isinstance(sprite, Player) and not (isinstance(sprite, Bullet) and
                                                               isinstance(sprite.sender, Player)):
                        sprite.half_damage(self.damage, self.passage)
                    killed = True
                elif isinstance(self.sender, Enemy):
                    # Пролетаем сквозь всё что не принадлежит группе врагов
                    if not isinstance(sprite, Enemy) and not (isinstance(sprite, Bullet) and
                                                              isinstance(sprite.sender, Enemy)):
                        sprite.half_damage(self.damage, self.passage)
                        killed = True

                if isinstance(sprite, Bullet):
                    sprite.kill(show_explosion=False)
                    show_explosion = False

        if killed or not 0 <= self.rect.centerx <= WIDTH_W or not 0 <= self.rect.centery <= HEIGHT_W:
            self.kill(show_explosion=show_explosion)

    def kill(self, show_explosion=True):
        super().kill()
        if show_explosion:
            ShellExplosion(self.layout, self.get_center())


class Effect(Actor):
    def __init__(self, layout: Game, coords, rep=1, size=None):
        super().__init__(layout, size)
        self.add(layout.effects_group)
        self.set_coords(
            coords[0] - self.rect.w // 2,
            coords[1] - self.rect.h // 2
        )
        self.rep = rep

    def update(self, *args):
        tick = get_tick(args)
        self.update_animation(tick)
        if self.animations[self.cur_animation].rep == self.rep:
            self.kill()


class ShellExplosion(Effect):
    def __init__(self, layout, coords):
        super().__init__(layout, coords, rep=1)
        self.init_state_animation(load_image("data\\image\\shell_explosion.png", -1), 3, 1)
        self.animations[self.cur_animation].set_speed(5)


class BigBang(Effect):
    def __init__(self, layout, coords):
        super().__init__(layout, coords, rep=1, size=(SIZE_LARGE_CELL * 2, SIZE_LARGE_CELL * 2))
        self.init_state_animation(load_image("data\\image\\big_bang.png", -1), 3, 1)
        self.animations[self.cur_animation].set_speed(1.2)

        self.damaged_actors = set()

    def update(self, *args):
        if FRAMES_FROM_EXPLOSIONS:
            for sprite in pygame.sprite.spritecollide(self, self.layout.collision_bullet_group, False):
                sprite: Actor
                if id(sprite) not in self.damaged_actors:
                    self.damaged_actors.add(id(sprite))
                    sprite.half_damage(1, passage=10)
        super().update(*args)


class Score(Effect):
    def __init__(self, layout, coords, score=100):
        super().__init__(layout, coords, rep=5, size=(int(SIZE_SMALL_CELL * 1.4), int(SIZE_SMALL_CELL * 0.7)))

        self.score = score
        self.init_state_animation(
            Animation.cut_sheet(load_image("data\\image\\scores.png", -1), 5, 1)[score // 100 - 1])
        self.animations[self.cur_animation].set_speed(1)
        self.animations[self.cur_animation].set_speed(1)

    def update(self, *args):
        tick = get_tick(args)
        self.add_coords(0, - tick / 1000 * SIZE_SMALL_CELL * 1.5)
        super().update(*args)


class Spawn(Actor):
    def __init__(self, layout: Game, pos, character_class, check_func=None, **kwargs_for_spawn):
        super().__init__(layout, pos=pos)
        self.add(layout.spawn_group)

        image = pygame.Surface(size=(SIZE_LARGE_CELL, SIZE_LARGE_CELL))
        image.fill((0, 0, 0))
        self.set_state_image(image)

        self.animations["spawning"] = Animation(load_image("data/image/spawn.png", -1), 6, 1)
        self.animations["spawning"].set_max_rep(5)
        self.animations["spawning"].set_speed(2.5)

        self.pos_spawn = pos
        self.character_class: Character.__class__ = character_class
        self.spawning = False
        self.check_func = (lambda game_space: True) if not check_func else check_func
        self.kwargs_for_spawn = kwargs_for_spawn

    def update(self, *args):
        tick = get_tick(args)
        self.update_animation(tick)
        if self.spawning:
            if self.animations["spawning"].rep == 3:
                self.change_animation("state_0_0_-1", discharge_old=True)
                self.spawning = False
                self.character_class(self.layout, self.pos_spawn, **self.kwargs_for_spawn)
                self.remove(self.layout.collision_moving_group)
        elif (not pygame.sprite.spritecollideany(self, self.layout.collision_moving_group) and
              self.check_func(self.layout)):
            self.spawning = True
            self.change_animation("spawning")
            self.add(self.layout.collision_moving_group)


class Bonus(Actor):
    def __init__(self, layout: Game, pos, key=None):
        super().__init__(layout, pos=pos)
        self.add(layout.bonuses_group)

        if key is None:
            key = random.randint(0, 6)
        elif not isinstance(key, int):
            raise ValueError("Некорректный ключ")
        elif not 0 <= key <= 6:
            raise ValueError("Некорректный ключ")

        self.key = key
        img = Animation.cut_sheet(load_image("data\\image\\bonuses.png"), 7, 1)[key]
        img.set_colorkey(img.get_at((0, 0)))
        img2 = pygame.Surface(size=(1, 1))
        img2.set_colorkey(img2.get_at((0, 0)))

        self.set_state_image(img)
        a: Animation = self.animations[self.cur_animation]

        a.set_sheet([img, pygame.Surface(size=(1, 1))])
        a.set_speed(2)
        a.set_type('f')
        a.set_speed_m(5)

    def update(self, *args):
        self.update_animation(get_tick(args))
        if self.animations[self.cur_animation].rep == 600:
            self.kill()

        sprites = pygame.sprite.spritecollide(self, self.layout.player_group, False)
        if sprites:
            player = random.choice(sprites)
            if isinstance(player, Player):
                self.activate(player)
                self.kill()

    def activate(self, by: Player):
        Score(self.layout, coords=self.get_center(), score=500)

        if self.key == 0:
            by.set_immortality(True, 10)
        elif self.key == 1:
            self.layout.level_data["freezing"] = True
            pygame.time.set_timer(FREEZING_END, 10000, True)
        elif self.key == 2:
            h = self.layout.headquarters_group.sprites()[0]
            if not isinstance(h, Headquarters):
                return
            x, y = h.get_cell()
            for i in range(4):
                BonusConcreteWall(self.layout, (x + 0.5 * (i - 1), y - 0.5))
                BonusConcreteWall(self.layout, (x + 0.5 * (i - 1), y + 1))
            for i in range(2):
                BonusConcreteWall(self.layout, (x + 1, y + 0.5 * i))
                BonusConcreteWall(self.layout, (x - 0.5, y + 0.5 * i))
        elif self.key == 3:
            by.up_level()
        elif self.key == 4:
            [s.kill() for s in self.layout.enemy_group.sprites()]
        elif self.key == 5:
            self.layout.global_data[f"life_player_{by.number}"] += 1
        elif self.key == 6:
            by.up_level(by.max_stars - by.stars)
