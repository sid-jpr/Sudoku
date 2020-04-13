from gui import *

import argparse
import time

class Error(Exception):
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
                            choices=LEVELS,
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
                raise Error(
                    "each row = 9"
                )
            board.append([])

            for c in line:
                if not c.isdigit():
                    raise Error(
                        "allowed characters: 0-9"
                    )
                board[-1].append(int(c))

        if len(board) != 9:
            raise Error("# of rows = 9")
        return board

class SudokuGame(object):
    """
    Sudoku Game : store state of the board
                : check whether puzzle is completed
    """
    def __init__(self, root, board_file):
        self.board_file = board_file
        self.x = root

        # initialize timer
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

        # start timer
        if not self._running:            
            self._start = time.time() - self._elapsedtime
            self._updateTime()
            self._running = 1

    def _updateTime(self):
        self._elapsedtime = time.time() - self._start
        self._setTime(self._elapsedtime)
        self._timer = self.x.after(50, self._updateTime)
    
    def _setTime(self, elap):
        minutes = int(elap/60)
        seconds = int(elap - minutes*60.0)
        hseconds = int((elap - minutes*60.0 - seconds)*100)                
        self.timestr.set('%02d:%02d:%02d' % (minutes, seconds, hseconds))

    def _stopTime(self):                                    
        if self._running:
            self.x.after_cancel(self._timer)            
            self._elapsedtime = time.time() - self._start    
            self._setTime(self._elapsedtime)
            self._running = 0
    
    def _resetTime(self):                                  
        self._start = time.time()         
        self._elapsedtime = 0.0    
        self._setTime(self._elapsedtime)

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

    def _valid(self, num, pos):
        for i in xrange(9):
            if self.puzzle[pos[0]][i] == num and pos[1] != i:
                return False

        for i in xrange(9):
            if self.puzzle[i][pos[1]] == num and pos[0] != i:
                return False

        box_x = pos[1] // 3
        box_y = pos[0] // 3

        for i in xrange(box_y*3, box_y*3 + 3):
            for j in xrange(box_x*3, box_x*3 + 3):
                if self.puzzle[i][j] == num and (i,j) != pos:
                    return False
        return True

    def _find_empty(self):
        for i in xrange(9):
            for j in xrange(9):
                if self.puzzle[i][j] == 0:
                    return (i, j)
        return (-1, -1)

    def _solve(self):
        find = self._find_empty()
        # for debugging purposes
        print find
        
        if find == (-1, -1):
            return True
        else:
            row, col = find

        for i in xrange(1,10):
            if self._valid(i, (row, col)):
                self.puzzle[row][col] = i
                # for debugging purposes
                print i

                if self._solve():
                    return True
                # for debugging purposes
                print "retrace"

                self.puzzle[row][col] = 0
        return False


if __name__ == '__main__':
    board_name = parse_arguments()

    with open('%s.sudoku' % board_name, 'r') as boards_file:
        root = Tk()

        game = SudokuGame(root, boards_file)
        game.start()

        SudokuUI(root, game)
        root.geometry("%dx%d" % (WIDTH, HEIGHT + 40))
        root.mainloop()