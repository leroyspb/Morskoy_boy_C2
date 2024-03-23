from random import randint

# класс определения и сравнения точек друг с другом
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
#сравниваем точки через метод __eq__
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
#при помощи метода __repr__ выводим точки в консоль
    def __repr__(self):
        return f"({self.x}, {self.y})"

# базовый класс исключений при некорректных действиях пользователя
class BoardException(Exception):
    pass

# класс исключений при выстреле за доску
class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

# класс исключений при выстреле в ту же клетку
class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass

# класс корабля
class Ship:
    # собираем точки: нос корабля, длина корабля, количество жизней, ориентация корабля
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    # по точкам всего корабля проходим циклом от носа на i клеток
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots
# проверка на попадание
    def shooten(self, shot):
        return shot in self.dots

# класс игрового поля
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
# количество пораженных кораблей
        self.count = 0
# сетка игрового поля
        self.field = [["O"] * size for _ in range(size)]
# занятые кораблем точки или точки куда стреляли
        self.busy = []
# список кораблей доски
        self.ships = []

    # метод размещения корабля (проверяет что точка не занята и есть возможэность поставить точку)
    # если условия позволяют ставим символ точки
    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

# метод который ставит соседние точки подбитого корабля занятыми
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

# вывод корабля на доску
    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"
# скрывать корабли или нет
        if self.hid:
            res = res.replace("■", "O")
        return res

    # проверка нахождения точки за пределами доски
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # метод выстрела, проверяет выходит точка за границы или нет
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        # занята или нет точка
        if d in self.busy:
            raise BoardUsedException()
        # если не занята до добавляем к списку занятых
        self.busy.append(d)
        # проходим в списке по короблям и определяем принадлежит к короблю или нет
        for ship in self.ships:
            if d in ship.dots:
                #если был подстрелен то уменьшаем жизни
                ship.lives -= 1
                # и ставим Х
                self.field[d.x][d.y] = "X"
                #когда 0 пишем корабль уничтожен
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                # если корабль ранен, выполняем True и повторяется метод заново
                else:
                    print("Корабль ранен!")
                    return True
        # если мимо принтуем Мимо
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    # начальный список должен быть пустым для расстановки кораблей, а в процессе игры показывает какие клетки заняты
    def begin(self):
        self.busy = []

# класс игрока, определяем 2 доски - свою и противника
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    #метод исключительно для потомков этого класса, ничего не определяет
    def ask(self):
        raise NotImplementedError()

    # если выстрел проходит все инструкции то повторяем ход при попадании
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

#класс игрока-компьютер
# генерируем точки рандомно

class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d

# запрос координат, опредегяем что коорджингат две, что это числа, далее  вычитаем -1 так как индекс идет с 0
class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)

# класс самой игры
# генерируем доски игрока и компьютера с заполненными короблями
# спомощью hid параметра скрываем корабли
class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        #создаем двух игроков передав им заполненные доски
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    #метод гарантированного создания рандомной доски
    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    # метод рандомного расположения кораблей, если попыток больше 2000 вернем None
    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    # приветствие с форматом ввода координат игры
    def greet(self):
        print("-------------------")
        print("  Приветствуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        # метод выбора игрока (чей ход)
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            # если четное ходит пользователь, нечетное компьютер.
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                # нужно ли повторить ход, если да то num - 1 чтобы ход остался у игрока при попадании
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            # количество пораженных кораблей и условия выйгрыша Пользователя
            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break
            # количество пораженных кораблей и условия выйгрыша Компьютера
            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    # метод старт запускает метода greet и loop
    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()