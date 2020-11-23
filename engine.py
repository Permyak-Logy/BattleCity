import pygame
import os
import sys
import json
from win32api import GetSystemMetrics
from extra import load_image, get_tick
import configparser
from typing import Union, Tuple
from widgets import PPushButton


class Application:
    screen: pygame.Surface
    fps: int
    smooth: bool
    debug: bool
    size_window: Tuple[int, int]

    mode = None
    __image_arrow = None
    __show_arrow = True

    def __init__(self, size: Tuple[int, int]):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(sys.path[0], 'config.ini'))

        pygame.init()
        pygame.mixer.set_num_channels(self.config.getint("engine", "num_channels"))
        self.init_window(size)
        self.__layouts = {}
        self.debug = self.config.getboolean('engine', 'debug')
        self.clock = pygame.time.Clock()

        self.__running = False

    def wait(self, milliseconds):
        val = 0
        while val <= milliseconds:
            val += self.clock.tick()
            pygame.event.clear()
            pygame.display.flip()

    def init_window(self, size: Tuple[int, int]):
        self.size_window = size

        if self.config.getboolean('engine', 'centring_window'):
            self.__center_window()

        self.fps = self.config.getint('engine', 'fps')
        self.smooth = self.config.getboolean('engine', 'smooth')
        self.screen = pygame.display.set_mode(self.get_matrix())

        pygame.display.set_caption(self.config.get('engine', 'title'))
        pygame.display.set_icon(load_image(self.config.get('engine', 'icon')))

    def get_matrix(self) -> tuple:
        return self.size_window

    def load_layout(self, key_mode: str, layout):
        self.__layouts[key_mode] = layout

    def dispatch_event_layout(self, event, *args, **kwargs):
        try:
            layout = self.get_layout(self.mode)
        except KeyError:
            pass
        else:
            if hasattr(layout, event):
                eval(f"layout.{event}")(*args, **kwargs)

    def open_layout(self, key_mode: str, *args, **kwargs):
        self.dispatch_event_layout("on_close", *args, **kwargs)

        self.mode = key_mode

        self.dispatch_event_layout("on_open", *args, *kwargs)

    def get_layout(self, key: str):
        return self.__layouts[key]

    def show_arrow(self):
        self.__show_arrow = True

    def hide_arrow(self):
        self.__show_arrow = False

    def set_image_arrow(self, image: pygame.Surface):
        if image is not None:
            self.__image_arrow = pygame.transform.scale(
                image, (20, 20)
            )
            pygame.mouse.set_visible(False)
        else:
            self.__image_arrow = None
            pygame.mouse.set_visible(True)

    def __center_window(self):
        """Центрирование окна"""
        size_window = self.get_matrix()
        pos_x = GetSystemMetrics(0) / 2 - size_window[0] / 2
        pos_y = GetSystemMetrics(1) / 2 - size_window[1] / 2
        os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (int(pos_x), int(pos_y))
        os.environ['SDL_VIDEO_CENTERED'] = '0'

    def run(self):
        self.start(self.config.get("engine", "mode"))
        self.__running = True
        self.__event_loop()
        self.close()

    def start(self, key_mode: str):
        self.open_layout(key_mode)

    def stop(self):
        """
        Останавливает event_loop
        :return:
        """
        self.__running = False

    def __event_loop(self):
        fps_s = []
        self.clock.tick()
        while self.__running:
            tick = self.clock.tick(self.fps)

            layout = self.get_layout(self.mode)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.dispatch_event_layout('on_mouse_press', event)
                elif event.type == pygame.KEYDOWN:
                    self.dispatch_event_layout('on_key_press', event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.dispatch_event_layout('on_mouse_release', event)
                elif event.type == pygame.KEYUP:
                    self.dispatch_event_layout('on_key_release', event)
                else:
                    self.dispatch_event_layout('on_other_events', event)

            layout.update(tick if not self.smooth else round(1 / self.fps * 1000))

            self.screen.fill((100, 0, 0))
            layout.render(self.screen)  # Прорисовка всех объектов пространства

            # Отрисовка курсора, если мышь внутри окна
            if self.__image_arrow and pygame.mouse.get_focused() and self.show_arrow:
                self.screen.blit(self.__image_arrow, (pygame.mouse.get_pos()))

            # Дебаг
            if self.debug:
                fps_s.append(round(self.clock.get_fps()))
                if len(fps_s) > 10000:
                    fps_s.pop(0)
                debug_text = f"FPS: {round(self.clock.get_fps())} (MAX {self.fps}) | " \
                             f"TICK: {tick if not self.smooth else round(1 / self.fps * 1000)} | " \
                             f"Smooth: {self.smooth} | " \
                             f"mFPS ({min(fps_s)} {int(sum(fps_s) / len(fps_s))} {max(fps_s)})"
                self.screen.blit(
                    pygame.transform.rotozoom(
                        pygame.font.Font(None, 50).render(
                            debug_text, True, pygame.color.Color("white")
                        ), 0, 0.5),
                    (0, 0))

            pygame.display.flip()

    def close(self):
        self.stop()
        pygame.quit()

    def terminate(self, code=0):
        """Аварийный выход"""
        self.close()
        sys.exit(code)


class Layout:
    image_background: pygame.Surface = None
    config: dict = None
    """
    Класс для поверхностей
    """

    def __init__(self, application: Application, layout_config_filename=None):
        self.app = application
        if not layout_config_filename:
            self.load_config(
                os.path.join(os.path.dirname(__file__),
                             f"{self.__class__.__name__}.json"))
        else:
            self.load_config(layout_config_filename)

        self.apply_config()
        self.widget_group = pygame.sprite.Group()

    def load_config(self, filename: str):
        with open(filename, encoding='utf8') as file:
            self.config = json.load(file)

    def apply_config(self):
        bg = self.config.get('background')
        if isinstance(bg, str):
            self.set_background(load_image(bg))
        elif isinstance(bg, list):
            img = pygame.Surface(size=(1, 1))
            img.fill(bg)
        else:
            self.set_background(bg)

    def update(self, *args):
        tick = get_tick(args)
        self.widget_group.update(tick)

    def render(self, screen: pygame.Surface):
        if self.image_background:
            screen.blit(self.image_background, (0, 0))  # Накладывет фон
        self.widget_group.draw(screen)

    def set_background(self, image: Union[pygame.Surface, None], scaled=True):
        if image is None:
            # Если указан None то поставит картинку по умолчанию (Чёрный цвет)
            image = pygame.Surface(size=self.app.get_matrix())
            image.fill((0, 0, 0))

        if scaled:
            image = pygame.transform.scale(image, self.app.get_matrix())

        self.image_background = image

    def on_mouse_press(self, event):
        for widget in self.widget_group:
            if isinstance(widget, PPushButton) and widget.on_click(event.pos):
                break

    def add_widget(self, widget):
        widget.add(self.widget_group)

    def add_widgets(self, *widgets):
        for widget in widgets:
            self.add_widget(widget)

    def remove_widget(self, widget):
        widget.remove(self.widget_group)

    def remove_widgets(self, *widgets):
        for widget in widgets:
            self.remove_widget(widget)


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

    def draw(self, actor: pygame.sprite.Sprite):
        if self.size == -1:
            size = actor.rect.size
        else:
            size = self.size
        img = pygame.transform.scale(self.get_screen(), size)

        if self.type_drawing == "b":
            actor.image.blit(img, self.pos)
        elif self.type_drawing == "f":
            if hasattr(actor, 'set_image'):
                actor.set_image(self.get_screen())
            else:
                actor.image = img

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
