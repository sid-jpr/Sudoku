from Tkinter import *

LEVELS = ['test', 'easy', 'medium', 'hard']
SIDE = 60
MARGIN = 20
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9

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
                              fg='white',
                              command=self._solve_it)
        solve_button.pack(side=LEFT, fill=BOTH, expand=TRUE)

        self.__draw_grid()
        self.__draw_puzzle()

        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)

    def _solve_it(self):
        self.game._solve()
        self.__draw_puzzle()

        self.game._stopTime()

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
                self.game._stopTime()
            else:
                flag = 1
                for i in xrange(0, 9):
                    for j in xrange(0, 9):
                        if self.game.puzzle[i][j] == 0:
                            flag = 0
                if flag:
                    self.__draw_result(0)
                    self.game._stopTime()

    def __clear_answers(self):
        self.game.start()
        self.canvas.delete("victory")
        self.canvas.delete("defeat")
        
        self.game._resetTime()
        
        self.__draw_puzzle()