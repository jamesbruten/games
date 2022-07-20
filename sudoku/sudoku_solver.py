import numpy as np
import time
start_time = time.time()

def check_valid(grid, val, row, col):
    # checks value is not repeated in row, col or 3x3 grid
    g_row = grid[row, :]
    if np.count_nonzero(g_row==val) > 1:
        return False

    g_col = grid[:, col]
    if np.count_nonzero(g_col==val) > 1:
        return False

    min_row = (row // 3) * 3
    max_row = min_row + 3
    min_col = (col // 3) * 3
    max_col = min_col + 3
    
    square = grid[min_row:max_row, min_col:max_col]
    if np.count_nonzero(square==val) > 1:
        return False
    
    return True


def solver(grid, row, col):
    # recursively steps through grid and backtracks if invalid solution
    row_max = np.size(grid, 0)
    col_max = np.size(grid, 1)
    while True:
        if grid[row, col] == 0:
            for guess in range(1, 10):
                grid[row, col] = guess
                allowed = check_valid(grid, guess, row, col)
                if allowed == True:
                    if row == row_max-1 and col == col_max-1:
                        return True, grid
                    test, grid = solver(grid, row, col)
                    if test == True:
                        return True, grid
            grid[row, col] = 0
            return False, grid
        else:
            col += 1
            if col == col_max:
                if row == row_max-1:
                    return True, grid
                col = 0
                row += 1





grid = np.genfromtxt('input_sudoku.txt', dtype=int)

test, grid = solver(grid, 0, 0)

for row in range(np.size(grid,0)):
    if row%3 == 0:
        print('-------------------------')
    for col in range(np.size(grid,1)):
        if col%3 == 0:
            print('| ', end='')
        print('{} '.format(grid[row, col]), end='')
    print('|')
print('-------------------------')

np.savetxt('completed_sudoku.txt', grid, fmt='%d')

print("\n--- %.7s secs ---" % (time.time() - start_time))