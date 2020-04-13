from Tkinter import *

import argparse
import time

BOARDS = ['test', 'easy', 'hard']
MARGIN = 20
SIDE = 60
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9


class SudokuError(Exception):
    pass


def parse_arguments():
    """
    python sudoku.py --board <board name>
    where, `board name` must be in the `BOARD` list
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--board",
                            help="Desired board name",
                            type=str,
                            choices=BOARDS,
                            required=True)

    args = vars(arg_parser.parse_args())
    return args['board']


class SudokuBoard(object):
    """
    Sudoku Board
    """
    def __init__(self, board_file):
        self.board = self.__create_board(board_file)

    def __create_board(self, board_file):
        board = []
        for line in board_file:
            line = line.strip()
            if len(line) != 9:
                raise SudokuError(
                    "Each line in the sudoku puzzle must be 9 chars long."
                )
            board.append([])

            for c in line:
                if not c.isdigit():
                    raise SudokuError(
                        "Valid characters for a sudoku puzzle must be in 0-9"
                    )
                board[-1].append(int(c))

        if len(board) != 9:
            raise SudokuError("Each sudoku puzzle must be 9 lines long")
        return board


class SudokuGame(object):
    """
    Sudoku Game : store state of the board
                : check whether puzzle is completed
    """
    def __init__(self, root, board_file):
        self.board_file = board_file
        self.x = root

        self._start = 0.0        
        self._elapsedtime = 0.0
        self._running = 0
        self.timestr = StringVar()

        self.start_puzzle = SudokuBoard(board_file).board

    def start(self):
        self.game_over = False
        self.puzzle = []
        for i in xrange(9):
            self.puzzle.append([])
            for j in xrange(9):
                self.puzzle[i].append(self.start_puzzle[i][j])

        if not self._running:            
            self._start = time.time() - self._elapsedtime
            self._update()
            self._running = 1

    def _update(self): 
        self._elapsedtime = time.time() - self._start
        self._setTime(self._elapsedtime)
        self._timer = self.x.after(50, self._update)
    
    def _setTime(self, elap):
        minutes = int(elap/60)
        seconds = int(elap - minutes*60.0)
        hseconds = int((elap - minutes*60.0 - seconds)*100)                
        self.timestr.set('%02d:%02d:%02d' % (minutes, seconds, hseconds))

    def check_win(self):
        for row in xrange(9):
            if not self.__check_row(row):
                return False
        for column in xrange(9):
            if not self.__check_column(column):
                return False
        for row in xrange(3):
            for column in xrange(3):
                if not self.__check_square(row, column):
                    return False
        self.game_over = True
        return True

    def __check_block(self, block):
        return set(block) == set(range(1, 10))

    def __check_row(self, row):
        return self.__check_block(self.puzzle[row])

    def __check_column(self, column):
        return self.__check_block(
            [self.puzzle[row][column] for row in xrange(9)]
        )

    def __check_square(self, row, column):
        return self.__check_block(
            [
                self.puzzle[r][c]
                for r in xrange(row * 3, (row + 1) * 3)
                for c in xrange(column * 3, (column + 1) * 3)
            ]
        )


class SudokuUI(Frame):
    """
    Tkinter GUI
    """
    def __init__(self, parent, game):
        self.game = game
        Frame.__init__(self, parent)
        self.parent = parent

        self.row, self.col = -1, -1
        self.__initUI()

    def __initUI(self):
        self.parent.title("SUDOKU")
        self.parent.configure(bg='black')
        self.pack(fill=BOTH)
        self.canvas = Canvas(self,
                             width=WIDTH,
                             height=HEIGHT,
                             bg='black')
        self.canvas.pack(fill=BOTH, side=TOP)
        
        clear_button = Button(self,
                              text="CLEAR",
                              bg='blue',
                              fg='white',
                              command=self.__clear_answers)
        clear_button.pack(side=LEFT, fill=BOTH, expand=TRUE)

        timer_label = Label(self, textvariable=self.game.timestr, font="bold")
        self.game._setTime(self.game._elapsedtime)
        timer_label.pack(side=LEFT, fill=BOTH, expand=TRUE)

        solve_button = Button(self,
                              text="SOLVE",
                              bg='blue',
                              fg='white')
                              #command=self.__clear_answers)
        solve_button.pack(side=LEFT, fill=BOTH, expand=TRUE)

        self.__draw_grid()
        self.__draw_puzzle()

        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)

    def __draw_grid(self):
        """
        Draws grid divided with blue lines into 3x3 squares
        """
        for i in xrange(10):
            color = "blue" if i % 3 == 0 else "grey"
            wd = 4 if i % 3 == 0 else 2

            x0 = MARGIN + i * SIDE
            y0 = MARGIN
            x1 = MARGIN + i * SIDE
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, width=wd, fill=color)

            x0 = MARGIN
            y0 = MARGIN + i * SIDE
            x1 = WIDTH - MARGIN
            y1 = MARGIN + i * SIDE
            self.canvas.create_line(x0, y0, x1, y1, width=wd, fill=color)

    def __draw_puzzle(self):
        self.canvas.delete("numbers")
        for i in xrange(9):
            for j in xrange(9):
                answer = self.game.puzzle[i][j]
                if answer != 0:
                    x = MARGIN + j * SIDE + SIDE / 2
                    y = MARGIN + i * SIDE + SIDE / 2
                    original = self.game.start_puzzle[i][j]
                    color = "white" if answer == original else "red"
                    self.canvas.create_text(
                        x, y, text=answer, tags="numbers", fill=color, font=("Pursia", 15)
                    )

    def __draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col * SIDE + 1
            y0 = MARGIN + self.row * SIDE + 1
            x1 = MARGIN + (self.col + 1) * SIDE - 1
            y1 = MARGIN + (self.row + 1) * SIDE - 1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="red", tags="cursor"
            )

    def __draw_result(self, x):
        x0 = y0 = MARGIN + SIDE * 3
        x1 = y1 = MARGIN + SIDE * 6

        if x:
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                tags="victory", fill="green", outline="white"
            )
            x = y = MARGIN + 4 * SIDE + SIDE / 2
            self.canvas.create_text(
                x, y,
                text="Congrats!", tags="victory",
                fill="white", font=("Pursia", 20)
            )
        else:
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                tags="defeat", fill="red", outline="white"
            )
            x = y = MARGIN + 4 * SIDE + SIDE / 2
            self.canvas.create_text(
                x, y,
                text="Try Again!", tags="defeat",
                fill="white", font=("Pursia", 20)
            )

    def __cell_clicked(self, event):
        if self.game.game_over:
            return
        x, y = event.x, event.y
        if (MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN):
            self.canvas.focus_set()

            row, col = (y - MARGIN) / SIDE, (x - MARGIN) / SIDE

            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            elif self.game.puzzle[row][col] == 0:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1

        self.__draw_cursor()

    def __key_pressed(self, event):
        if self.game.game_over:
            return
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            self.game.puzzle[self.row][self.col] = int(event.char)
            self.col, self.row = -1, -1
            self.__draw_puzzle()
            self.__draw_cursor()
            if self.game.check_win():
                self.__draw_result(1)

                if self.game._running:
                    self.after_cancel(self.game._timer)
                    self.game._elapsedtime = time.time() - self.game._start
                    self.game._setTime(self.game._elapsedtime)
                    self.game._running = 0
            else:
                flag = 1
                for i in range(0, 9):
                    for j in range(0, 9):
                        if self.game.puzzle[i][j] == 0:
                            flag = 0
                if flag:
                    self.__draw_result(0)

                    if self.game._running:
                        self.after_cancel(self.game._timer)
                        self.game._elapsedtime = time.time() - self.game._start
                        self.game._setTime(self.game._elapsedtime)
                        self.game._running = 0

    def __clear_answers(self):
        self.game.start()
        self.canvas.delete("victory")
        self.canvas.delete("defeat")
        
        self.game._start = time.time()
        self.game._elapsedtime = 0.0
        self.game._setTime(self.game._elapsedtime)
        
        self.__draw_puzzle()


if __name__ == '__main__':
    board_name = parse_arguments()

    with open('%s.sudoku' % board_name, 'r') as boards_file:
        root = Tk()

        game = SudokuGame(root, boards_file)
        game.start()

        SudokuUI(root, game)
        root.geometry("%dx%d" % (WIDTH, HEIGHT + 40))
        root.mainloop()