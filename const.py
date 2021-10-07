# Размеры клеток в пикселях
SIZE_MINI_CELL = 8
SIZE_SMALL_CELL = SIZE_MINI_CELL * 2
SIZE_LARGE_CELL = SIZE_SMALL_CELL * 2

# Размеры поля в клетках
SIZE_F = WIDTH_F, HEIGHT_F = 13, 13

# Отступы в пикселях
TOP, BOTTOM = SIZE_SMALL_CELL, SIZE_SMALL_CELL
LEFT, RIGHT = SIZE_LARGE_CELL, SIZE_MINI_CELL * 9

# Размеры окна в пикселях
SIZE_W = WIDTH_W, HEIGHT_W = (
    LEFT + SIZE_LARGE_CELL * WIDTH_F + RIGHT,
    TOP + SIZE_LARGE_CELL * HEIGHT_F + BOTTOM
)

# События (32774 < val < 40966)
EVENT_LEVEL_FINISHED = 32775
IMMORTALITY_END_P1 = 32776
IMMORTALITY_END_P2 = 32777
FREEZING_END = 32778

# Игровые настройки
FRAMES_FROM_EXPLOSIONS = False  # Взрывы от танков наносят урон (Нестандартное дополнение)
ONLY_ONE_BONUS_ON_MAP = False  # Только один бонус на карте (При новом, все старые очищаются)
SHOW_FPS = False  # Переключатель данных о быстродействии

# Настройки ИИ (УСТАРЕЛО)
REVIEW_RADIUS_ENEMY = 2.5  # Обзор танков противника
MAX_REVIEW_WAY = 5  # Максимальный вычисляемый путь
MAX_ATTEMPTS_FOR_CAL_WAY = 2  # Максимальное кол-во попыток для составления пути
MIN_WAIT_TIME, MAX_WAIT_TIME = 0.1, 3  # Минимальное и максимальное время ожидание у врагов (в сек.)

BG_COLOR = (130, 130, 130)  # Цвет фона

# ЧИТЫ
NO_COLLISION_FOR_PLAYERS = False  # Убирает столкновения со статичными объектами и врагами (но не со снарядами)
