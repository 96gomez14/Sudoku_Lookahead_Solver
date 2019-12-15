import copy
import random
import numpy as np
# from simanneal import Annealer

# from https://neos-guide.org/content/sudoku
_ = 0

"""PROBLEM = np.array([
    1, _, _,  _, _, 6,  3, _, 8,
    _, _, 2,  3, _, _,  _, 9, _,
    _, _, _,  _, _, _,  7, 1, 6,

    7, _, 8,  9, 4, _,  _, _, 2,
    _, _, 4,  _, _, _,  9, _, _,
    9, _, _,  _, 2, 5,  1, _, 4,

    6, 2, 9,  _, _, _,  _, _, _,
    _, 4, _,  _, _, 7,  6, _, _,
    5, _, 7,  6, _, _,  _, _, 3,
])"""

PROBLEM = np.array([
    _, 5, 6,  8, _, _,  9, _, _,
    2, _, _,  _, _, _,  3, 7, _,
    _, 4, 3,  _, _, 9,  1, _, 6,

    4, _, _,  _, _, 7,  _, 3, _,
    8, 6, 2,  _, _, _,  4, 1, 7, 
    _, 3, _,  4, _, _,  _, _, 2,

    3, _, 5,  7, _, _,  8, 6, _,
    _, 2, 4,  _, _, _,  _, _, 1,
    _, _, 8,  _, _, 1,  2, 4, _,    
])

# This code comes from https://www.adrian.idv.hk/2019-01-30-simanneal/

def print_sudoku(state):
    border = "------+-------+------"
    rows = [state[i:i+9] for i in range(0,81,9)]
    for i,row in enumerate(rows):
        if i % 3 == 0:
            print(border)
        three = [row[i:i+3] for i in range(0,9,3)]
        print(" | ".join(
            " ".join(str(x or "_") for x in one)
            for one in three
        ))
    print(border)

def coord(row, col):
    return row*9+col

def block_indices(block_num):
    """return linear array indices corresp to the sq block, row major, 0-indexed.
    block:
       0 1 2     (0,0) (0,3) (0,6)
       3 4 5 --> (3,0) (3,3) (3,6)
       6 7 8     (6,0) (6,3) (6,6)
    """
    firstrow = (block_num // 3) * 3
    firstcol = (block_num % 3) * 3
    indices = [coord(firstrow+i, firstcol+j) for i in range(3) for j in range(3)]
    return indices

def initial_solution(problem):
    """provide sudoku problem, generate an init solution by randomly filling
    each sq block without considering row/col consistency"""
    solution = problem.copy()
    for block in range(9):
        indices = block_indices(block)
        block = problem[indices]
        zeros = [i for i in indices if problem[i] == 0]
        to_fill = [i for i in range(1, 10) if i not in block]
        random.shuffle(to_fill)
        for index, value in zip(zeros, to_fill):
            solution[index] = value
    return solution

class Sudoku_Sq():
    def __init__(self, problem):
        self.problem = problem
        self.state = initial_solution(problem)
       # super().__init__(state)
    def move(self):
        """randomly swap two cells in a random square"""
        block = random.randrange(9)
        indices = [i for i in block_indices(block) if self.problem[i] == 0]
        m, n = random.sample(indices, 2)
        self.state[m], self.state[n] = self.state[n], self.state[m]
        """I slightly modified this function to take as a parameter 
        'result,' to store the returned result when we are running 
        this method with parallel processes."""
    def energy(self, result=None):
        """calculate the number of violations: assume all rows are OK"""
        column_score = lambda n: -len(set(self.state[coord(i, n)] for i in range(9)))
        row_score = lambda n: -len(set(self.state[coord(n, i)] for i in range(9)))
        score = sum(column_score(n)+row_score(n) for n in range(9))
        if score == -162:
            self.user_exit = True # early quit, we found a solution
        if isinstance(result, tuple):
            result[0][result[1]] = score	# Sets the second index (score) of some entry in our dictionary, which is filled with state-score pairs
        return score
