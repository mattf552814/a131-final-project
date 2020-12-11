import turtle
from pathlib import Path

colors = ['dark', 'light']
shapes = ['bishop', 'king', 'knight', 'pawn', 'queen', 'rook']

end_rows = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook']


def draw_board(trtl, board_size):
	for border_size in [board_size / 2 + 20, board_size / 2 + 10]:
		trtl.up()
		trtl.goto(-border_size, -border_size)
		trtl.down()
		trtl.pensize(4)
		for i in range(4):
			trtl.forward(border_size * 2)
			trtl.left(90)

	trtl.up()
	trtl.goto(-board_size / 2, -board_size / 2)
	trtl.color('#fdfaf7')
	trtl.begin_fill()
	for i in range(4):
		trtl.forward(board_size)
		trtl.left(90)
	trtl.end_fill()

	square_size = board_size / 8
	for i in range(4):
		trtl.up()
		trtl.goto(-board_size / 2 + square_size * 2 * i, -board_size / 2)
		trtl.seth(0)
		trtl.color('black')
		trtl.begin_fill()
		instrs = [False, True, False, False, True, True, False, False, True, True, False, False, True, True, False, True, True, True, False, False, True, True, False, False, True, True, False, False, True, True, False, True]
		for instr in instrs:
			if instr: trtl.rt(90)
			else: trtl.lt(90)
			trtl.forward(square_size)
		trtl.end_fill()
