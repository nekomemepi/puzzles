BEGIN {
  # init arrays for looping
  split("12", a2, "")
  split("123", a3, "")
  split("12345678", a8, "")
  split("123456789", a9, "")
  a2[0] = a8[0] = 0
  s9 = "123456789"
}

# input is either a string of 81 chars, or 9 lines of 9
length($0) == 81 {
  split($0, puzzle_arr, "")
}

length($0) == 9 {
  string = (string) ? string $0 : string
  if (length(string) == 81) {
    split(string, puzzle_arr, "")
  }
}

function init_frame(puzzle_arr,    g) {
  # frame[1..81] = "123456789" or value
  for (g=1;g<82;g++) {
    frame[g] = (puzzle_arr[g] == ".") ? s9 : puzzle_arr[g]
  }
  return frame
}

function init_lookups(rows, cols, sqrs,   g, h, i, j, k, count) {
  # rows[1..9] of frame positions
  for (i in a8) {
    for (j in a9) {
      g = (i * 9) + j
      rows[i+1] = rows[i+1] g ","
    }
    rows[i+1] = rows[i+1] ","
    sub(",,", "", rows[i+1])
  }

  # cols[1..9] of frame positions
  for (i in a9) {
    for (j in a8) {
      g = (j * 9) + i
      cols[i] = cols[i] g ","
    }
    cols[i] = cols[i] ","
    sub(",,", "", cols[i])
  }

  # sqrs[1..9] of frame positions
  for (h in a2) {
    for (i in a2) {
      count += 1
      for (j in a2) {
        g = (h * 27) + (i * 3) + (j * 9) + 1
        for (k in a2) {
          sqrs[count] = sqrs[count] g+k ","
        }
      }
      sqrs[count] = sqrs[count] ","
      sub(",,", "", sqrs[count])
    }
  }
}

function scan_frame(rcs,   g, h, i, k, t, u, v) {
  # loop over the nine rows, cols, and sqrs
  for (i in a9) {
    split(rcs[i], arr, ",")
    for (g in arr) {
      if (length(frame[arr[g]]) == 1) {
        for (h in arr) {
          if (length(frame[arr[h]]) > 1) sub(frame[arr[g]], "", frame[arr[h]])
        }
      }
    }

    # check for naked singles
    v = ""
    for (g in arr) {
      v = v frame[arr[g]]
    }

    # naked singles appear once and will array split into 2
    for (k in a9) {
      if (split(v, a, k) == 2) {
        for (g in arr) {
          if (match(frame[arr[g]], k)) {
            frame[arr[g]] = k
          }
        }
      }
    }
  }
}

function to_string(frame,     i, this, string) {
  for (i=1; i<82; i++) {
    this = frame[i]
    this = (length(this) == 1) ? this : "."
    string = string this
  }
  return string
}

function show(curr, prev,      i, c, p) {
  split(curr, c, "")
  split(prev, p, "")
  for (i=1; i<=81; i++) {
    printf("%s",
        (( c[i] == p[i] ) ? " " c[i] " " : "\033[31;1m " c[i] " \033[0m")
        (( i % 9 == 0 ) ? "\n" : "")
    )
  }
}

END {
  frame = init_frame(puzzle_arr)
  init_lookups(rows, cols, sqrs)

  # process frame
  curr = to_string(frame)

  do {
    prev = curr
    scan_frame(rows)
    scan_frame(cols)
    scan_frame(sqrs)
    curr = to_string(frame)
    print "\nPass = " ++number "\n"
    show(curr, prev)
  } while (curr != prev)
}
