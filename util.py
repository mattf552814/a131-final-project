import turtle
from pathlib import Path

colors = ['dark', 'light']
shapes = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']

end_rows = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook']


def register_piece_shapes(screen):
	for color in colors:
		for shape in shapes:
			screen.register_shape(str(Path('pieces') / color / f'{shape}.gif'))


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
		instrs = [
			False, True, False, False, True, True, False, False, True, True,
			False, False, True, True, False, True, True, True, False, False,
			True, True, False, False, True, True, False, False, True, True,
			False, True
		]
		for instr in instrs:
			if instr: trtl.rt(90)
			else: trtl.lt(90)
			trtl.forward(square_size)
		trtl.end_fill()
	trtl.hideturtle()


def create_piece(screen, color, shape):
	trtl = turtle.Turtle(shape=str(Path('pieces') / color / f'{shape}.gif'))
	trtl.up()
	return trtl


def create_full_board(screen):
	return [
		[create_piece(screen, 'light', piece) for piece in end_rows],
		[create_piece(screen, 'light', 'pawn') for _ in range(8)]
	] + [[None for __ in range(8)] for _ in range(4)] + [
		[create_piece(screen, 'dark', 'pawn') for _ in range(8)],
		[create_piece(screen, 'dark', piece) for piece in end_rows]
	]


def create_taken_piece_indicator(screen):
	return {color: {shape: create_piece(screen, color, shape) for shape in filter(lambda x: x != 'king', shapes)} for color in colors}


def move_board_pieces(board, board_size, square_size):
	piece_start_x = -0.5 * (board_size - square_size)
	piece_start_y = -piece_start_x
	for y in range(8):
		for x in range(8):
			item = board[y][x]
			if item is not None:
				item.goto(piece_start_x + square_size * x, piece_start_y - square_size * y)


def draw_turn_indicator(trtl, is_blacks_turn, font, pos):
	trtl.clear()
	trtl.goto(pos[0], (pos[1]) * (-1 if is_blacks_turn else 1) - font[1] * 1.5)
	trtl.write(f"{'Black' if is_blacks_turn else 'White'}'s Turn", align='center', font=font)


def move_piece_indicators(board_size, indicators):
	y_cor = board_size / 2 + 150
	step = (board_size / 1.5) / (len(shapes) - 1)  # exclude king
	start = -board_size / 3 + step / 2
	for i, piece in enumerate(indicators['light']):
		indicators['light'][piece].goto(start + (i * step), -y_cor)
		indicators['dark'][piece].goto(start + (i * step), y_cor)


def update_piece_indicators(writer, font, taken_pieces, indicators):
	writer.clear()
	for piece in indicators['light']:
		x, y = indicators['light'][piece].pos()
		writer.goto(x, y - 40 - font[1] * 1.5)  # vertically center
		writer.write(taken_pieces['light'][piece], move=False, align='center', font=font)
	for piece in indicators['dark']:
		x, y = indicators['dark'][piece].pos()
		writer.goto(x, y + 40 - font[1] * 1.5)  # vertically center
		writer.write(taken_pieces['dark'][piece], move=False, align='center', font=font)
