from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog
from PyQt5.QtCore import QSize, Qt
import sys

INDENT_LEFT, INDENT_TOP = 150, 0
SIZE_CELL = QSize(20, 20)


class EditorLevels(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edit_filename = None

        self.btn_save = QPushButton('Сохранить', self)
        self.btn_save.move(10, 10)
        self.btn_load = QPushButton('Загрузить', self)
        self.btn_load.move(10, 50)
        self.btn_new_level = QPushButton('Новый', self)
        self.btn_new_level.move(10, 90)

        self.field = [[Cell(self, pos=(x, y)) for x in range(26)] for y in range(26)]
        self.setFixedSize(INDENT_LEFT + SIZE_CELL.width() * 26, INDENT_TOP + SIZE_CELL.height() * 26)

        self.cur_state = 0

        self.btn_cur_state = QPushButton(self)
        self.btn_cur_state.setStyleSheet(Cell.icons[self.cur_state][0])
        self.btn_cur_state.resize(SIZE_CELL)
        self.btn_cur_state.move(20, 170)

        self.lbl_cur_state = QLabel("Текущий", self)
        self.lbl_cur_state.move(50, 165)

        self.help_sheet = []
        for i, (sheet, _, description) in Cell.icons.items():
            pos_y = 200 + (SIZE_CELL.height() + 10) * i
            btn, lbl = Brush(self, sheet, i, SIZE_CELL, (10, pos_y)), QLabel(description, self)
            lbl.move(40, pos_y - 5)

            self.help_sheet.append((btn, lbl))

        self.btn_save.clicked.connect(self.save_level)
        self.btn_load.clicked.connect(self.load_level)
        self.btn_new_level.clicked.connect(self.new_level)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_S:
            self.save_level()

    def new_level(self):
        self.edit_filename = None
        [[cell.set_state(0) for cell in row] for row in self.field]
        self.setWindowTitle(f'Новый')

    def load_level(self):
        try:
            filename = QFileDialog.getOpenFileName(self, 'Выбрать уровень', '')[0]
            if not filename:
                return
            with open(filename, encoding='utf8') as file:
                data = file.read()

            data = [list(line)[:26] for line in data.split('\n')][:26]

            [[elem.set_state(0) for elem in col] for col in self.field]

            for x, col in enumerate(data):
                for y, elem in enumerate(col):
                    if x >= len(self.field) or y >= len(self.field[0]):
                        continue

                    for i, (style_sheet, code, _) in Cell.icons.items():
                        if code == elem:
                            self.field[x][y].set_state(i)
                            break

            self.edit_filename = filename
            self.setWindowTitle(f'Редактируется {filename.split("/")[-1]}')
        except Exception as E:
            print(E)

    def save_level(self):
        data = '\n'.join([''.join(list(map(lambda x: x.get_symbol(), row))) for row in self.field])
        with open('level_2.txt' if not self.edit_filename else self.edit_filename, mode='w', encoding='utf8') as file:
            file.write(data)
        try:
            self.setWindowTitle(f'Файл был сохранён как {self.edit_filename if self.edit_filename else "level_2.txt"}')
        finally:
            pass


class Brush(QPushButton):
    def __init__(self, window: EditorLevels, sheet: str, state: int, size=(10, 10), pos=(0, 0)):
        super().__init__(window)
        self.window_ = window
        self.state = state
        self.resize(size)
        self.move(*pos)
        self.setStyleSheet(sheet)

        self.clicked.connect(self.set_window_cur_brush)

    def set_window_cur_brush(self):
        self.window_.cur_state = self.state
        self.window_.btn_cur_state.setStyleSheet(Cell.icons[self.state][0])


class Cell(QPushButton):
    icons = {
        0: ('QPushButton{background-color: #101010}', ' ', 'Пустота'),
        1: ('QPushButton{background-color: #aa0000;}', '-', 'Кирпич'),
        2: ('QPushButton{background-color: gray;}', '=', 'Бетон'),
        3: ('QPushButton{background-color: blue;}', '0', 'Вода'),
        4: ('QPushButton{background-color: green;}', '#', 'Кусты'),
        5: ('QPushButton{background-color: white;}', '/', 'Лёд'),
        6: ('QPushButton{background-color: red;}', 'S', 'Враг'),
        7: ('QPushButton{background-color: yellow;}', 'P', 'Игрок'),
        8: ('QPushButton{background-color: purple;}', 'H', 'База')
    }

    def __init__(self, window: EditorLevels, state=0, pos=(0, 0)):
        super().__init__(window)
        self.window_ = window
        self.resize(SIZE_CELL)
        self.move(INDENT_LEFT + SIZE_CELL.width() * pos[0], INDENT_TOP + SIZE_CELL.height() * pos[1])
        self.state = state
        self.setStyleSheet(self.icons[self.state][0])
        self.clicked.connect(self.change_state)

    def change_state(self, event):
        if self.state == self.window_.cur_state:
            self.state = 0
        else:
            self.state = self.window_.cur_state
        self.setStyleSheet(self.icons[self.state][0])

    def get_symbol(self):
        return self.icons[self.state][1]

    def set_state(self, state):
        self.state = state
        self.setStyleSheet(self.icons[self.state][0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EditorLevels()
    ex.show()
    sys.exit(app.exec_())
