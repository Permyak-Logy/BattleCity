import pygame
import random


class PWidget(pygame.sprite.Sprite):
    def __init__(self, layout=None):
        super().__init__()
        self.layout = layout

        self._is_show = True
        self._is_enable = True
        self._bg_image = None
        self._color_key = None

        self.image = pygame.Surface(size=(300, 300))
        self.rect = self.image.get_rect()

    def flip(self):
        del self.image
        self.image = pygame.Surface(size=self.get_size())
        self.image.fill((1, 1, 1) if not self._color_key else self._color_key)
        self.image.set_colorkey(self._color_key)

        if self._bg_image and self._is_show:
            self.image.blit(pygame.transform.scale(self._bg_image, self.get_size()), (0, 0))
        return self

    def set_color_key(self, color_key):
        self._color_key = color_key

    def get_color_key(self):
        return self._color_key

    def set_bg_image(self, image: pygame.Surface):
        self._bg_image = image
        return self

    def get_bg_image(self):
        return self._bg_image

    def resize(self, size: tuple):
        self.rect.width, self.rect.height = tuple(map(int, size))
        return self

    def get_size(self):
        return self.rect.width, self.rect.height

    def move(self, x: int, y: int):
        self.rect.x += x
        self.rect.y += y
        return self

    def set_pos(self, pos: tuple):
        self.rect = self.rect.move(*pos)
        return self

    def get_pos(self):
        return self.rect.x, self.rect.y


class PLabel(PWidget):
    def __init__(self, text="", layout=None):
        super().__init__(layout)
        self._text = text
        self._font = pygame.font.Font(None, 50)
        self._bg_text = None
        self._color_text = (255, 255, 255)

    def flip(self):
        super().flip()
        if not self._is_show:
            return self
        img_text: pygame.Surface = (self._font.render(self._text, True, self._color_text, self._bg_text))

        pos = (
            self.image.get_width() // 2 - img_text.get_width() // 2,
            self.image.get_height() // 2 - img_text.get_height() // 2
        )
        self.image.blit(img_text, pos)
        return self

    def set_text(self, text: str):
        self._text = text
        return self

    def get_text(self):
        return self._text

    def set_font(self, font):
        self._font = font
        return self

    def get_font(self):
        return self._font

    def set_bg_text(self, image: pygame.Surface):
        self._bg_text = image
        return self


class PPushButton(PLabel):
    def __init__(self, text="", layout=None):
        super().__init__(text, layout)
        self._func = (lambda *_, **__: None, tuple(), dict())

    def connect(self, func, *args, **kwargs):
        self._func = (func, args, kwargs)
        return self

    def get_focused(self, pos) -> bool:
        """Возвращает True если pos находится на кнопке, иначе False"""
        return self.rect.collidepoint(*pos)

    def on_click(self, pos):
        pass
        if not self.get_focused(pos):
            return False
        self.clicked()

    def clicked(self):
        if self._func[0] is None:
            return False
        if not self._is_show:
            return False
        if not self._is_enable:
            return False
        self._func[0](*self._func[1], **self._func[2])
        return True


class PDisplayNumber(PLabel):
    def __init__(self, layout=None, nums: list = None, count_nums=1):
        super().__init__(layout=layout)
        self.nums = nums
        self.count_nums = count_nums
        self.cur_number = 0

    def set_cur_number(self, number: int):
        self.cur_number = number
        return self

    def flip(self):
        super().flip()
        nums = list(map(int, str(self.cur_number % 10 ** self.count_nums)))
        size_n = (self.get_size()[0] // self.count_nums, self.get_size()[1])
        for i, n in enumerate(nums):
            self.image.blit(
                pygame.transform.scale(self.nums[n], size_n), (size_n[0] * i, 0))
        return self


class WidgetOld:
    """
    Виджеты (похожи на PushButton и Label из библиотеки PyQt5)
    """
    text = None
    font = None
    image = None
    color = None
    color_active = None
    color_text = None
    func = None
    pos = None
    x = None
    y = None
    size = None
    width = None
    height = None

    def __init__(self, size, **params):
        self.is_showed = None
        self.set_text(params.get('text', None))  # Установка текста
        self.set_font(params.get('font', None))  # Установка шрифта
        self.connect(params.get('func', None))  # Подключение функции

        self.set_color(params.get('color', (100, 100, 100)),  # Цвет фона
                       params.get('color_active', (0, 0, 0)),  # Цвет активного фона
                       params.get('color_text', (0, 0, 0)))  # Цвет текста

        self.show_background = params.get('show_background', True)  # Заливка
        self.bolded = params.get('bolded', True)  # Флаг выделения при наведении курсора
        self.number = params.get('number', random.randint(0, 2 ** 64))  # Установка номера

        self.set_pos(params.get('pos', (0, 0)))  # Установка позиции
        # Установка размера виджета. Если указан size == -1, то размер установится
        # минимальным возможным для отображения надписи
        self.resize(self.get_size_text() if size == -1 else size)

        self.set_image(params.get('image', None))  # Установка картинки
        self.show()  # Отображение

    def get_size(self) -> tuple:
        """Возвращает размеры"""

        return tuple(self.size)

    def get_size_text(self) -> tuple:
        """Возвращает размеры текста"""

        self.font.set_bold(True) if self.bolded else None
        size = self.font.size(self.text)
        self.font.set_bold(False) if self.bolded else None
        return tuple(size)

    def get_focused(self, pos) -> bool:
        """Возвращает True если pos  находится на кнопке, иначе False"""

        if not self.x <= pos[0] <= self.x + self.width:
            return False
        if not self.y <= pos[1] <= self.y + self.height:
            return False
        return True

    def set_text(self, text):
        """Устанавливает текст"""

        self.text = text

    def set_font(self, font):
        """Устанавливает шрифт"""

        self.font = pygame.font.Font(None, 16) if font is None else font

    def set_image(self, image):
        """Устанавливает картинку"""

        self.image = image

    def set_color(self, color=None, color_active=None, color_text=None):
        """Устанавливает цвета элементов"""

        if color is not None:
            # Цвет неактивного фона
            self.color = color
        if color_active is not None:
            # Цвет активного фона
            self.color_active = color_active
        if color_text is not None:
            # Цвет текста
            self.color_text = color_text

    def set_pos(self, pos):
        """Устанавливает координаты пункта"""

        self.pos = self.x, self.y = pos

    def resize(self, size):
        """Меняет размеры"""

        self.size = self.width, self.height = size

    def show(self):
        """Показать виджет"""

        self.is_showed = True

    def hide(self):
        """Скрыть виджет"""

        self.is_showed = False

    def connect(self, func):
        """Подключить функцию"""

        self.func = func

    def draw(self, screen, is_pressed=False):
        """Рисует кнопку на screen"""

        if not self.is_showed:
            # Не рисует если пункт скрыт
            return
        surface = pygame.Surface(size=self.get_size())
        if self.show_background:  # Заливка области
            color_background = self.color if not is_pressed or not self.bolded else self.color_active
            surface.fill(color_background)
        else:  # Преобразование в прозрачный фон
            surface.fill((1, 0, 0))
            surface.set_colorkey((1, 0, 0))

        if self.image is not None:  # наложение картинки если есть она
            surface.blit(self.image, (0, 0))

        if self.text is not None:  # Наложение текста если он есть
            if not is_pressed or not self.bolded:
                # Создание surface текста
                text = self.font.render(self.text, True, self.color_text)
            else:
                # Создание surface выделенного текста
                self.font.set_bold(True)
                text = self.font.render(self.text, True, self.color_text)
                self.font.set_bold(False)

            # Вычесление центра текста
            text_x = self.width // 2 - text.get_width() // 2
            text_y = self.height // 2 - text.get_height() // 2

            # Наложение текста
            surface.blit(text, (text_x, text_y))

        # Наложение получившегося изображения Widget на screen
        screen.blit(surface, self.pos)

    def on_click(self, pos) -> bool:
        """Вызывает функцию подключённую к кнопке, если она была нажата
        Возвращает True если была активирована"""

        if self.func is None:
            return False
        if not self.get_focused(pos):
            return False
        if not self.is_showed:
            return False
        self.func()
        return True
