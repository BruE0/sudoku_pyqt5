#!/usr/bin/env python3

"""
    sudoku_board.py
    2020
    Implements a Board class that can use a simple brute-force backtracking algorithm
    to be solved.
"""



class Board:
    def __init__(self, data):
        self.data = data
        self.static_digits_index = frozenset(
            (i, j)
            for i, row in enumerate(data)
            for j, element in enumerate(row)
            if element is not None
        )

    def __str__(self):
        chars = []
        for i in range(9):
            for j in range(9):
                item = self.data[i][j]
                chars.append(f"{item}" if item is not None else '_')
                if j%3 == 2:
                    chars.append('|')
                else:
                    chars.append('_' if i%3 == 2 else ' ')
            chars.append('\n')
        return ''.join(chars)

    def __getitem__(self, coord):
        return self.data[coord[0]][coord[1]]

    def __setitem__(self, coord, value):
        if self.is_available(coord):
            self.data[coord[0]][coord[1]] = value
        else:
            raise IndexError("Cannot assign numbers to coordinates with initial values.")

    def is_available(self, coord):
        """ Returns true if the coordinate is a valid slot (not one of the initial digits). """
        return coord not in self.static_digits_index

    def next_coord(self, coord):
        """ Returns `next` coordinate (i, j) in grid. 
            (... -> (1, 8) -> (2, 0) -> (2, 1) -> ...)
        If coord is (8, 8) [last], it returns (9, 0).
        """
        return (coord[0] + (coord[1]==8), (coord[1] + 1) % 9)

    def get_digits_available(self, coord):
        """ Returns all the digits available for the coord, considering sudoku's rules. """
        ii, jj = coord
        block_start_i = (ii//3)*3 # rounds ii down to either 0, 3 or 6
        block_start_j = (jj//3)*3 # rounds jj down to either 0, 3 or 6
        digits_in_block = set(
            self.data[y][x]
            for y in range(block_start_i, block_start_i + 3)
            for x in range(block_start_j, block_start_j + 3)
            if (y,x) != coord
        )
        digits_in_row = set(self.data[ii][x] for x in range(9) if x != jj)
        digits_in_column = set(self.data[y][jj] for y in range(9) if y != ii)
        return set(range(1, 10)) - (digits_in_block | digits_in_column | digits_in_row)

    def is_solvable(self):
        """ Validates static digits and check if it is solvable using recursion. 
            If it is, returns the board, otherwise returns False.
        """
        new_board = Board([row.copy() for row in self.data])
        for i, j in new_board.static_digits_index:
            if new_board.data[i][j] not in new_board.get_digits_available((i, j)):
                return False

        new_board.recursion_solve()
        if new_board.is_solved():
            return new_board
        return False

    def is_solved(self):
        return all(
            len(self.get_digits_available((i, j))) == 1
            for i in range(9)
            for j in range(9)
        )

    def clear(self):
        """ Clears all the digits that aren't initial """
        for i in range(9):
            for j in range(9):
                if (i, j) not in self.static_digits_index:
                    self.data[i][j] = None

    def recursion_solve(self, coord=(0, 0)):
        """ Solves sudoku board using brute-force backtracking algorithm. """
        if coord == (9, 0):
            return True
            
        if not self.is_available(coord): # if coord has initial digit, then ignore.
            return self.recursion_solve(self.next_coord(coord))

        digits = self.get_digits_available(coord)
        while digits:
            self[coord] = digits.pop()
            result = self.recursion_solve(self.next_coord(coord))
            if result:
                return True

        self[coord] = None
        return False



def main():
    test1 = [[4,8,9,None,None,5,None,None,None],
             [7,None,2,None,4,6,8,3,None],
             [None,None,6,None,None,None,None,4,9],
             [8,7,3,None,6,None,None,None,5],
             [None,2,None,None,8,1,None,6,3],
             [1,None,5,4,7,None,9,None,8],
             [None,None,None,None,None,None,None,8,None],
             [None,3,None,6,None,None,1,5,7],
             [None,None,None,8,1,None,None,None,6]]
    board = Board(test1)
    print(f"Is solvable: {bool(board.is_solvable())}")
    print(board)
    board.recursion_solve()
    print(f"Solved board:\n\n{board}")
    print(f"Is solved: {board.is_solved()}")

if __name__ == "__main__":
    main()
