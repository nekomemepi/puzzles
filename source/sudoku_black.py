"""
Script to solve Sudoku by removing single values
"""

from more_itertools import collapse
from collections import Counter
from copy import deepcopy
import os

# Example test frames
frame_0 = (
    "69......5....9.28..73.54.........6.2....6..7....1385...6.....4...43..7.9...9....."
)
frame_1 = (
    ".5...79.47.9..4....4.2.97.3..1.7.482...9.1...567.4.1..9.57.3.4....4..2.72.45...9."
)
frame_2 = (
    "...1.2....6.....7...8...9..4.......3.5...7...2...8...1..9...8.5.7.....6....3.4..."
)

# Populate the frame with default values
frame = [deepcopy([i for i in range(1, 10)]) for _ in range(81)]

# Process the puzzle
for tple in [(i, [int(c)]) for i, c in enumerate(frame_2) if c.isdigit()]:
    frame[tple[0]] = tple[1]

# Create references for rows, columns, and squares
rows = [frame[i : i + 9] for i in range(0, 81, 9)]
cols = [list(row) for row in zip(*rows)]
sqrs = [
    [frame[(h * 27) + (j * 9) + (i * 3) + k] for k in range(3) for j in range(3)]
    for i in range(3)
    for h in range(3)
]

# Initialize conditions
count = 0

while True:
    count += 1
    bfor = deepcopy(frame)

    for x in cols, sqrs, rows:
        for r in range(9):
            for cell in x[r]:
                if len(cell) == 1:  # Remove single values
                    for i in x[r]:
                        if (len(i) > 1) and (cell[0] in i):
                            i.remove(cell[0])
                else:  # check for naked singles
                    ones = set(
                        [k for k, v in Counter(collapse(x[r])).items() if v == 1]
                    )
                    for i in x[r]:
                        if len(i) > 1:
                            if len(drop := list(set(i) & ones)) == 1:
                                i[:] = drop

    aftr = deepcopy(frame)
    if bfor == aftr:
        break

    # Print the frame
    print(os.linesep + " Pass: " + str(count))
    p = ""
    for m in range(81):
        if m % 9 == 0:
            p = p + os.linesep
        if len(frame[m]) == 1:
            if frame[m] == bfor[m]:  # no change
                c = " " + str(frame[m][0]) + " "
            else:  # colourize
                c = "\033[0;31m " + str(frame[m][0]) + " \033[1;30m"
        else:
            c = " • "
        p = p + c
    print(p)
