import os
import pygame
from const import SIZE_LARGE_CELL, TOP, LEFT


def cache(maximum=1000):
    def wp(func):
        nonlocal maximum
        memory = {}

        def new_func(*args, **kwargs):
            nonlocal memory, maximum
            res = memory.get(args)
            if res is None:
                res = func(*args)
                memory[args] = res
                keys = list(memory.keys())
                if len(keys) >= maximum:
                    del memory[keys[0]]
            return res

        return new_func

    return wp


def load_image(filename: str, color_key=None, using_default=True) -> pygame.Surface:
    """
    Загружает картинку.

    :param filename: Путь к файлу
    :param color_key: Ключ для установки прозрачности через image.set_colorkey.
    Если -1 то возьмётся ключ из (0;0) пикселя
    :param using_default: Если True, то при возникновении ошибок, будет игнорировать их и
    возвращать картинку по умолчанию
    :return: image: pygame.Surface
    """
    filename = os.path.normpath(filename)
    try:
        image = pygame.image.load(filename).convert()
        if color_key is not None:
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        else:
            image = image.convert_alpha()
        return image
    except Exception as E:
        if using_default:
            image = pygame.Surface(size=(10, 10))
            image.fill(pygame.color.Color("purple"))
            return image
        raise E


def get_tick(args) -> int:
    """Получает тик из аргументов передаваемых в update"""
    if len(args) >= 1:
        return args[0]
    return round(1 / 60 * 1000)


def get_m(value) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def cell_to_coords(cell: tuple) -> tuple:
    return cell[0] * SIZE_LARGE_CELL + LEFT, cell[1] * SIZE_LARGE_CELL + TOP
