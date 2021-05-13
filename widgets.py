import pygame
from typing import Tuple


class PWidget(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self._is_show = True
        self._is_enable = True
        self._bg_image = None
        self._color_key = None

        self.image = pygame.Surface(size=(300, 300))
        self.rect = self.image.get_rect()

    def flip(self):
        del self.image
        self.image = pygame.Surface(size=self.get_size())
        if not self._is_show:
            self.image.fill((0, 0, 0))
            self.image.set_colorkey((0, 0, 0))
            return self
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
        pos = tuple(map(int, pos))
        self.rect = self.rect.move(*pos)
        return self

    def get_pos(self):
        return self.rect.x, self.rect.y

    def update(self, *args):
        self.flip()

    def hide(self):
        self._is_show = False
        return self

    def show(self):
        self._is_show = True
        return self


class PLabel(PWidget):
    def __init__(self, text=""):
        super().__init__()
        self._text = text
        self._font = pygame.font.Font(None, 50)
        self._bg_text = None
        self._color_text = (255, 255, 255)
        self.shift_text_px = (1, 1)

    def flip(self):
        super().flip()
        if not self._is_show:
            return self
        img_text: pygame.Surface = (self._font.render(self._text, True, self._color_text, self._bg_text))

        pos = (
            self.shift_text_px[0] + self.image.get_width() / 2 - img_text.get_width() / 2,
            self.shift_text_px[1] + self.image.get_height() / 2 - img_text.get_height() / 2
        )
        self.image.blit(img_text, tuple(map(int, pos)))
        return self

    def set_color_text(self, color_text):
        self._color_text = color_text
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
    def __init__(self, text=""):
        super().__init__(text)
        self._func = (lambda *_, **__: None, tuple(), dict())

    def connect(self, func: callable, *args, **kwargs):
        self._func: Tuple[callable, tuple, dict] = (func, args, kwargs)
        return self

    def get_focused(self, pos: tuple) -> bool:
        """Возвращает True если pos находится на кнопке, иначе False"""
        return self.rect.collidepoint(*pos)

    def on_click(self, pos: tuple) -> bool:
        if not self.get_focused(pos):
            return False
        return self.clicked()

    def clicked(self) -> bool:
        if self._func[0] is None:
            return False
        if not self._is_show:
            return False
        if not self._is_enable:
            return False
        self._func[0](*self._func[1], **self._func[2])
        return True


class PDisplayNumber(PLabel):
    def __init__(self, nums: list = None, count_nums=1):
        super().__init__()
        self.nums = nums
        self.count_nums = count_nums
        self.cur_number = 0
        self.align = "L"
        self.inc_zeros = False

    def set_align(self, align: str):
        if align.upper() not in ['R', 'L']:
            raise ValueError(f"Заначение выравнивания либо R или L (получено {align})")
        self.align = align.upper()

    def show_start_zeros(self, toggle: bool):
        self.inc_zeros = toggle

    def set_cur_number(self, number: int):
        self.cur_number = number
        return self

    def flip(self):
        super().flip()
        if not self._is_show:
            return self
        nums = list(map(int, str(self.cur_number % 10 ** self.count_nums)))
        size_n = (self.get_size()[0] // self.count_nums, self.get_size()[1])
        if self.align == 'L':
            pass
        elif self.align == 'R':
            nums = [0 if self.inc_zeros else ''] * (self.count_nums - len(nums)) + nums

        for i, n in enumerate(nums):
            try:
                self.image.blit(pygame.transform.scale(self.nums[n], size_n), (size_n[0] * i, 0))
            except TypeError:
                pass
        return self
