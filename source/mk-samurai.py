"""
Script to make Samurai Sudoku.

Needs (a lot) more work.
"""

from more_itertools import set_partitions
from more_itertools import collapse
from itertools import combinations
from collections import Counter
from random import choice
from copy import deepcopy
import sys
import os

# Initialize the empty square list
empt = {i for i in range(1, 10)}

# Calculate x + y offsets   [0, 12, 252, 264, 132]
offs = [
    (0 if r in [0, 2] else 12 if r in [1, 3] else 6)
    + (0 if r in [0, 1] else 12 * 21 if r in [2, 3] else 6 * 21)
    for r in range(5)
]

# Populate the grid with spaces and empt
grid = list(" " * 21 * 21)
for r in range(5):
    for i in range(9):
        for j in range(9):
            grid[i * 21 + j + offs[r]] = deepcopy(empt)

def validate(frame, pos, val):
    bfor = deepcopy(frame)
    aftr = deepcopy(frame)
    aftr[pos] = {val}

    # Create references for rows, columns, and squares
    blks = [
        [aftr[i + offs[r] : i + offs[r] + 9] for i in range(0, 9 * 21, 21)]
        for r in range(5)
    ]
    rows = [
        aftr[i + offs[r] : i + offs[r] + 9]
        for r in range(5)
        for i in range(0, 9 * 21, 21)
    ]
    cols = list(
        collapse([[list(row) for row in zip(*blks[r])] for r in range(5)], levels=1)
    )
    sqrs = [
        list(
            collapse(
                [aftr[(p := x + y + z + offs[r]) : p + 3] for x in range(0, 63, 21)],
                levels=1,
            )
        )
        for r in range(5)
        for y in range(0, 9, 3)
        for z in range(0, 21 * 9, 63)
    ]

    for x in rows, cols, sqrs:
        for r in x:
            if [
                v
                for k, v in Counter(collapse([i for i in r if len(i) == 1])).items()
                if v > 1
            ]:
                return False, bfor

    # Attempt to solve the puzzle
    for _ in range(30):
        while bfor != aftr:
            bfor = deepcopy(aftr)
            for x in rows, cols, sqrs:
                for r in x:
                    # Remove single values from other cells
                    for sngt in [
                        k
                        for k, v in Counter(
                            collapse([i for i in r if len(i) == 1])
                        ).items()
                        if (v == 1) and (list(collapse(r)).count(k) > 1)
                    ]:
                        for cell in r:
                            if (sngt in cell) and (len(cell) > 1):
                                cell -= {sngt}

                    # check for a single value appearing only once in all cells
                    for sngt in [
                        k
                        for k, v in Counter(
                            collapse([i for i in r if len(i) > 1])
                        ).items()
                        if v == 1
                    ]:
                        for cell in r:
                            if sngt in cell:
                                cell -= empt.copy() - {sngt}

                    # naked pairs
                    dbls = sorted([s for s in r if (r.count(s) == 2) and (len(s) == 2)])
                    twos = [set.union(*dbls[i : i + 2]) for i in range(0, len(dbls), 2)]
                    for i in twos:
                        for cell in r:
                            if (
                                i.issubset(cell)
                                and (len(cell) > 1)
                                and (len(cell) != 2)
                            ):
                                cell -= i
                                # print("Naked Pairs", twos)

                    # naked triples
                    trps = sorted([s for s in r if (r.count(s) == 3) and (len(s) == 3)])
                    thrs = [set.union(*trps[i : i + 3]) for i in range(0, len(trps), 3)]
                    for i in thrs:
                        for cell in r:
                            if (
                                i.issubset(cell)
                                and (len(cell) > 1)
                                and (len(cell) != 3)
                            ):
                                cell -= i
                                # print("Naked Triples", thrs)

                    # hidden pairs
                    trps = [s for s in r if (len(s) == 3)]
                    dbls = {k for k, v in Counter(collapse(r)).items() if v == 2}
                    twos = set(
                        collapse(
                            set(d)
                            for d in {
                                tuple(sorted(set1 & set2))
                                for set1, set2 in combinations(trps, 2)
                                if len(set1 & set2) == 2
                            }
                        )
                    )
                    if trps and dbls and (dbls == twos):
                        for i in [twos]:
                            for cell in r:
                                if i.issubset(cell) and (len(cell) > 2):
                                    cell &= i
                                else:
                                    cell &= empt.copy() - i

                    # hidden triples
                    trps = {k for k, v in Counter(collapse(r)).items() if v in {2, 3}}
                    thrs = [set(i) for i in combinations(trps, 3)]
                    twos = [set(i) for i in combinations(trps, 2)]
                    pthr = [p for i in r for p in thrs if p < i]
                    ptwo = {tuple(pthr) for i in r for p in twos if p < i and p < pthr}

            for x in rows, cols, sqrs:
                for r in x:
                    if [
                        v
                        for k, v in Counter(
                            collapse([i for i in r if len(i) == 1])
                        ).items()
                        if v > 1
                    ]:
                        return False, bfor

    return True, aftr

# Constants
nl = os.linesep
trck = []
stck = []
rmvd = 0

while rmvd < 120:
    bfor = deepcopy(grid)

    done = False
    while not done:
        rows = [
            bfor[i + offs[r] : i + offs[r] + 9]
            for r in range(5)
            for i in range(0, 9 * 21, 21)
        ]
        try:
            pos, tup = choice([(i, e) for i, e in enumerate(grid) if len(e) > 1])
        except:
            done = True

        while len(tup):
            val = choice(list(tup))
            test, aftr = validate(bfor, pos, val)
            if test:
                rmvd += 1
                trck.append((rmvd, pos, [val]))  # keep track of guesses
                stck.append(deepcopy(aftr))
                grid = deepcopy(aftr)
                break  # break for/while loop
            else:
                tup.remove(val)

        if not len(tup):  # backtrack
            rmvd += -3
            print(nl, "Backtracking...")
            grid = deepcopy(stck[rmvd])
            aftr = deepcopy(grid)
            stck = stck[:rmvd]
            trck = trck[:rmvd]
            break

        done = True

    # Print the difference
    print(nl + " Pass: ", rmvd, pos, val)
    p = ""
    for m in range(21 * 21):
        if m % 21 == 0:
            p = p + nl + f"{m:03d}"
        if len(grid[m]) == 1:
            if grid[m] == bfor[m]:  # no change
                c = " " + str(list(grid[m])[0]) + " "
            else:  # colourize
                c = "\033[1;31m " + str(list(grid[m])[0]) + " \033[1;30m"
        else:
            c = " • "
        p = p + c
    print(p)

    if bfor == aftr:
        break

# Print the puzzle
# ① ② ③ ④ ⑤ ⑥ ⑦ ⑧ ⑨
p = ""
for m in range(21 * 21):
    if m % 21 == 0:
        p = p + nl + f"{m:03d}"
    if len(aftr[m]) == 1:
        if aftr[m] == bfor[m]:  # no change
            c = " " + str(list(aftr[m])[0]) + " "
        else:  # colourize
            c = "\033[1;31m " + str(list(aftr[m])[0]) + " \033[1;30m"
    else:
        c = " • "
    p = p + c
print(p)

# Initial constraints to be included later
"""
000 •  •  •  •  •  •  •  •  •           •  •  •  •  •  •  •  •  •
021 •  •  •  •  •  •  •  •  •           •  •  •  •  •  •  •  •  •
042 •  •  •  •  •  •  •  •  •           •  •  •  •  •  •  •  •  •
063 •  •  •  •  •  •  •  •  •           •  •  •  •  •  •  •  •  •
084 •  •  •  •  5  •  •  •  •           •  •  •  •  5  •  •  •  •
105 •  •  •  •  •  •  •  •  •           •  •  •  •  •  •  •  •  •
126 •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •
147 •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •
168 •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •
189                   •  •  •  •  •  •  •  •  •
210                   •  •  •  •  5  •  •  •  •
231                   •  •  •  •  •  •  •  •  •
252 •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •
273 •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •
294 •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •  •
315 •  •  •  •  •  •  •  •  •           •  •  •  •  •  •  •  •  •
336 •  •  •  •  5  •  •  •  •           •  •  •  •  5  •  •  •  •
357 •  •  •  •  •  •  •  •  •           •  •  •  •  •  •  •  •  •
378 •  •  •  •  •  •  •  •  •           •  •  •  •  •  •  •  •  •
399 •  •  •  •  •  •  •  •  •           •  •  •  •  •  •  •  •  •
420 •  •  •  •  •  •  •  •  •           •  •  •  •  •  •  •  •  •
"""

