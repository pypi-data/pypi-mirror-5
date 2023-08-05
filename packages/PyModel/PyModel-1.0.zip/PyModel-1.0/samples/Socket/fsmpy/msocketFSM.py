
# pma.py --maxTransitions 100 msocket
# 59 states, 100 transitions, 1 accepting states, 0 unsafe states, 0 finished and 0 deadend states

# actions here are just labels, but must be symbols with __name__ attribute

def send_call(): pass
def send_return(): pass
def recv_call(): pass
def recv_return(): pass

# states, key of each state here is its number in graph etc. below

states = {
  0 : {'msocket': {'send_arg': '', 'recv_arg': 0, 'buffers': ''}},
  1 : {'msocket': {'send_arg': 'a', 'recv_arg': 0, 'buffers': ''}},
  2 : {'msocket': {'send_arg': '', 'recv_arg': 4, 'buffers': ''}},
  3 : {'msocket': {'send_arg': 'bb', 'recv_arg': 0, 'buffers': ''}},
  4 : {'msocket': {'send_arg': 'a', 'recv_arg': 4, 'buffers': ''}},
  5 : {'msocket': {'send_arg': '', 'recv_arg': 0, 'buffers': 'a'}},
  6 : {'msocket': {'send_arg': 'bb', 'recv_arg': 4, 'buffers': ''}},
  7 : {'msocket': {'send_arg': '', 'recv_arg': 0, 'buffers': 'b'}},
  8 : {'msocket': {'send_arg': '', 'recv_arg': 0, 'buffers': 'bb'}},
  9 : {'msocket': {'send_arg': '', 'recv_arg': 4, 'buffers': 'a'}},
  10 : {'msocket': {'send_arg': 'a', 'recv_arg': 0, 'buffers': 'a'}},
  11 : {'msocket': {'send_arg': 'bb', 'recv_arg': 0, 'buffers': 'a'}},
  12 : {'msocket': {'send_arg': '', 'recv_arg': 4, 'buffers': 'bb'}},
  13 : {'msocket': {'send_arg': '', 'recv_arg': 4, 'buffers': 'b'}},
  14 : {'msocket': {'send_arg': 'a', 'recv_arg': 0, 'buffers': 'b'}},
  15 : {'msocket': {'send_arg': 'bb', 'recv_arg': 0, 'buffers': 'b'}},
  16 : {'msocket': {'send_arg': 'a', 'recv_arg': 0, 'buffers': 'bb'}},
  17 : {'msocket': {'send_arg': 'bb', 'recv_arg': 0, 'buffers': 'bb'}},
  18 : {'msocket': {'send_arg': 'a', 'recv_arg': 4, 'buffers': 'a'}},
  19 : {'msocket': {'send_arg': 'bb', 'recv_arg': 4, 'buffers': 'a'}},
  20 : {'msocket': {'send_arg': '', 'recv_arg': 0, 'buffers': 'aa'}},
  21 : {'msocket': {'send_arg': '', 'recv_arg': 0, 'buffers': 'ab'}},
  22 : {'msocket': {'send_arg': '', 'recv_arg': 0, 'buffers': 'abb'}},
  23 : {'msocket': {'send_arg': 'a', 'recv_arg': 4, 'buffers': 'bb'}},
  24 : {'msocket': {'send_arg': 'bb', 'recv_arg': 4, 'buffers': 'bb'}},
  25 : {'msocket': {'send_arg': 'a', 'recv_arg': 4, 'buffers': 'b'}},
  26 : {'msocket': {'send_arg': 'bb', 'recv_arg': 4, 'buffers': 'b'}},
  27 : {'msocket': {'send_arg': '', 'recv_arg': 0, 'buffers': 'ba'}},
  28 : {'msocket': {'send_arg': '', 'recv_arg': 0, 'buffers': 'bbb'}},
  29 : {'msocket': {'send_arg': '', 'recv_arg': 0, 'buffers': 'bba'}},
  30 : {'msocket': {'send_arg': '', 'recv_arg': 0, 'buffers': 'bbbb'}},
  31 : {'msocket': {'send_arg': '', 'recv_arg': 4, 'buffers': 'aa'}},
  32 : {'msocket': {'send_arg': '', 'recv_arg': 4, 'buffers': 'ab'}},
  33 : {'msocket': {'send_arg': '', 'recv_arg': 4, 'buffers': 'abb'}},
  34 : {'msocket': {'send_arg': 'a', 'recv_arg': 0, 'buffers': 'aa'}},
  35 : {'msocket': {'send_arg': 'bb', 'recv_arg': 0, 'buffers': 'aa'}},
  36 : {'msocket': {'send_arg': 'a', 'recv_arg': 0, 'buffers': 'ab'}},
  37 : {'msocket': {'send_arg': 'bb', 'recv_arg': 0, 'buffers': 'ab'}},
  38 : {'msocket': {'send_arg': 'a', 'recv_arg': 0, 'buffers': 'abb'}},
  39 : {'msocket': {'send_arg': 'bb', 'recv_arg': 0, 'buffers': 'abb'}},
  40 : {'msocket': {'send_arg': '', 'recv_arg': 4, 'buffers': 'bba'}},
  41 : {'msocket': {'send_arg': '', 'recv_arg': 4, 'buffers': 'bbbb'}},
  42 : {'msocket': {'send_arg': '', 'recv_arg': 4, 'buffers': 'bbb'}},
  43 : {'msocket': {'send_arg': '', 'recv_arg': 4, 'buffers': 'ba'}},
  44 : {'msocket': {'send_arg': 'a', 'recv_arg': 0, 'buffers': 'ba'}},
  45 : {'msocket': {'send_arg': 'bb', 'recv_arg': 0, 'buffers': 'ba'}},
  46 : {'msocket': {'send_arg': 'a', 'recv_arg': 0, 'buffers': 'bbb'}},
  47 : {'msocket': {'send_arg': 'bb', 'recv_arg': 0, 'buffers': 'bbb'}},
  48 : {'msocket': {'send_arg': 'a', 'recv_arg': 0, 'buffers': 'bba'}},
  49 : {'msocket': {'send_arg': 'bb', 'recv_arg': 0, 'buffers': 'bba'}},
  50 : {'msocket': {'send_arg': 'a', 'recv_arg': 0, 'buffers': 'bbbb'}},
  51 : {'msocket': {'send_arg': 'bb', 'recv_arg': 0, 'buffers': 'bbbb'}},
  52 : {'msocket': {'send_arg': 'a', 'recv_arg': 4, 'buffers': 'aa'}},
  53 : {'msocket': {'send_arg': 'bb', 'recv_arg': 4, 'buffers': 'aa'}},
  54 : {'msocket': {'send_arg': 'a', 'recv_arg': 4, 'buffers': 'ab'}},
  55 : {'msocket': {'send_arg': 'bb', 'recv_arg': 4, 'buffers': 'ab'}},
  56 : {'msocket': {'send_arg': 'a', 'recv_arg': 4, 'buffers': 'abb'}},
  57 : {'msocket': {'send_arg': 'bb', 'recv_arg': 4, 'buffers': 'abb'}},
  58 : {'msocket': {'send_arg': '', 'recv_arg': 0, 'buffers': 'aaa'}},
}

# initial state, accepting states, unsafe states, frontier states, deadend states

initial = 0
accepting = [0]
unsafe = []
frontier = [35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58]
finished = []
deadend = []
runstarts = [0]

# finite state machine, list of tuples: (current, (action, args, result), next)

graph = (
  (0, (send_call, ('a',), None), 1),
  (0, (recv_call, (4,), None), 2),
  (0, (send_call, ('bb',), None), 3),
  (1, (recv_call, (4,), None), 4),
  (1, (send_return, (1,), None), 5),
  (2, (send_call, ('a',), None), 4),
  (2, (send_call, ('bb',), None), 6),
  (3, (recv_call, (4,), None), 6),
  (3, (send_return, (1,), None), 7),
  (3, (send_return, (2,), None), 8),
  (4, (send_return, (1,), None), 9),
  (5, (send_call, ('a',), None), 10),
  (5, (recv_call, (4,), None), 9),
  (5, (send_call, ('bb',), None), 11),
  (6, (send_return, (2,), None), 12),
  (6, (send_return, (1,), None), 13),
  (7, (send_call, ('a',), None), 14),
  (7, (recv_call, (4,), None), 13),
  (7, (send_call, ('bb',), None), 15),
  (8, (send_call, ('a',), None), 16),
  (8, (recv_call, (4,), None), 12),
  (8, (send_call, ('bb',), None), 17),
  (9, (send_call, ('a',), None), 18),
  (9, (recv_return, ('a',), None), 0),
  (9, (send_call, ('bb',), None), 19),
  (10, (recv_call, (4,), None), 18),
  (10, (send_return, (1,), None), 20),
  (11, (recv_call, (4,), None), 19),
  (11, (send_return, (1,), None), 21),
  (11, (send_return, (2,), None), 22),
  (12, (send_call, ('a',), None), 23),
  (12, (recv_return, ('bb',), None), 0),
  (12, (recv_return, ('b',), None), 7),
  (12, (send_call, ('bb',), None), 24),
  (13, (send_call, ('a',), None), 25),
  (13, (recv_return, ('b',), None), 0),
  (13, (send_call, ('bb',), None), 26),
  (14, (recv_call, (4,), None), 25),
  (14, (send_return, (1,), None), 27),
  (15, (recv_call, (4,), None), 26),
  (15, (send_return, (1,), None), 8),
  (15, (send_return, (2,), None), 28),
  (16, (recv_call, (4,), None), 23),
  (16, (send_return, (1,), None), 29),
  (17, (recv_call, (4,), None), 24),
  (17, (send_return, (1,), None), 28),
  (17, (send_return, (2,), None), 30),
  (18, (recv_return, ('a',), None), 1),
  (18, (send_return, (1,), None), 31),
  (19, (recv_return, ('a',), None), 3),
  (19, (send_return, (1,), None), 32),
  (19, (send_return, (2,), None), 33),
  (20, (send_call, ('a',), None), 34),
  (20, (recv_call, (4,), None), 31),
  (20, (send_call, ('bb',), None), 35),
  (21, (send_call, ('a',), None), 36),
  (21, (recv_call, (4,), None), 32),
  (21, (send_call, ('bb',), None), 37),
  (22, (send_call, ('a',), None), 38),
  (22, (recv_call, (4,), None), 33),
  (22, (send_call, ('bb',), None), 39),
  (23, (recv_return, ('bb',), None), 1),
  (23, (recv_return, ('b',), None), 14),
  (23, (send_return, (1,), None), 40),
  (24, (send_return, (2,), None), 41),
  (24, (recv_return, ('bb',), None), 3),
  (24, (recv_return, ('b',), None), 15),
  (24, (send_return, (1,), None), 42),
  (25, (recv_return, ('b',), None), 1),
  (25, (send_return, (1,), None), 43),
  (26, (send_return, (2,), None), 42),
  (26, (recv_return, ('b',), None), 3),
  (26, (send_return, (1,), None), 12),
  (27, (send_call, ('a',), None), 44),
  (27, (recv_call, (4,), None), 43),
  (27, (send_call, ('bb',), None), 45),
  (28, (send_call, ('a',), None), 46),
  (28, (recv_call, (4,), None), 42),
  (28, (send_call, ('bb',), None), 47),
  (29, (send_call, ('a',), None), 48),
  (29, (recv_call, (4,), None), 40),
  (29, (send_call, ('bb',), None), 49),
  (30, (send_call, ('a',), None), 50),
  (30, (recv_call, (4,), None), 41),
  (30, (send_call, ('bb',), None), 51),
  (31, (send_call, ('a',), None), 52),
  (31, (recv_return, ('a',), None), 5),
  (31, (recv_return, ('aa',), None), 0),
  (31, (send_call, ('bb',), None), 53),
  (32, (send_call, ('a',), None), 54),
  (32, (recv_return, ('a',), None), 7),
  (32, (recv_return, ('ab',), None), 0),
  (32, (send_call, ('bb',), None), 55),
  (33, (send_call, ('a',), None), 56),
  (33, (recv_return, ('a',), None), 8),
  (33, (recv_return, ('ab',), None), 7),
  (33, (send_call, ('bb',), None), 57),
  (34, (recv_call, (4,), None), 52),
  (34, (send_return, (1,), None), 58),
  (35, (recv_call, (4,), None), 53),
)
