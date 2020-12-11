import turtle
from pathlib import Path

colors = ['dark', 'light']
shapes = ['bishop', 'king', 'knight', 'pawn', 'queen', 'rook']

end_rows = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook']


def draw_board(trtl, board_size):
	trtl.showturtle()
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
	trtl.hideturtle()


def create_piece(screen, color, shape):
	image_path = str(Path('pieces') / color / f'{shape}.gif')
	screen.register_shape(image_path)
	trtl = turtle.Turtle(shape=image_path)
	trtl.up()
	return trtl


def create_full_board(screen):
	return [
		[create_piece(screen, 'light', piece) for piece in end_rows],
		[create_piece(screen, 'light', 'pawn') for _ in range(8)]
	] + ([[None] * 8] * 4) + [
		[create_piece(screen, 'dark', 'pawn') for _ in range(8)],
		[create_piece(screen, 'dark', piece) for piece in end_rows]
	]


def move_board_pieces(board, board_size, square_size):
	piece_start_x = -0.5 * (board_size - square_size)
	piece_start_y = -piece_start_x
	for y in range(8):
		for x in range(8):
			item = board[y][x]
			if item is not None:
				item.goto(piece_start_x + square_size * x, piece_start_y - square_size * y)
