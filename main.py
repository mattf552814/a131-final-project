import util
import logic
import turtle
import gc

win = turtle.Screen()
board_turtle = turtle.Turtle()
board_turtle.speed(10)

is_blacks_turn = False  # false means it's white's turn

FONT_SIZE = 20
FONT = ('PT Sans', FONT_SIZE, 'normal')

util.register_piece_shapes(win)

turn_indicator = turtle.Turtle()
turn_indicator.hideturtle()
turn_indicator.up()
turn_indicator.speed('fastest')
util.draw_turn_indicator(turn_indicator, is_blacks_turn, FONT, (0, 370))

board_size = 600

win.register_shape('restart_button.gif')
restart_button = turtle.Turtle(shape='restart_button.gif')
restart_button.penup()
restart_button.hideturtle()  # don't show the restart button until everything is initialized
restart_button.speed(0)
restart_button.goto(-(board_size / 2) - 100, 0)
def restart_program():  # noqa: E302 (two lines before function) - Should be an anonymous fn
	global board, taken_pieces, indicators_writer, taken_indicators, move_record, is_blacks_turn, turn_indicator, logic
	logic.selection_coord = None
	util.update_selection(selection_indicator, logic.selection_coord, board_size)
	turn_indicator.clear()
	indicators_writer.clear()
	for row in board:
		for piece in row:
			if isinstance(piece, turtle.Turtle):
				piece.hideturtle()
				del piece
	board = util.create_full_board(win)
	gc.collect()  # remove the old turtle completely
	taken_pieces = {color: {shape: 0 for shape in util.shapes} for color in util.colors}
	util.move_board_pieces(board, board_size, board_size / 8)
	util.update_piece_indicators(indicators_writer, ('PT Sans', 10, 'normal'), taken_pieces, taken_indicators)
	move_record = []
	is_blacks_turn = False
	util.draw_turn_indicator(turn_indicator, is_blacks_turn, FONT, (0, 370))
restart_button.onclick(lambda *_: restart_program())  # noqa: E305 (two lines after function) - Should be an anonymous fn

util.draw_board(board_turtle, board_size)

board = util.create_full_board(win)
taken_pieces = {color: {shape: 0 for shape in util.shapes} for color in util.colors}
util.move_board_pieces(board, board_size, board_size / 8)

indicators_writer = turtle.Turtle()
indicators_writer.hideturtle()
indicators_writer.up()
indicators_writer.speed('fastest')
taken_indicators = util.create_taken_piece_indicator(win)

util.move_piece_indicators(board_size, taken_indicators)
util.update_piece_indicators(indicators_writer, ('PT Sans', 10, 'normal'), taken_pieces, taken_indicators)

win.register_shape('selection.gif')
selection_indicator = turtle.Turtle(shape='selection.gif')
selection_indicator.speed(0)
selection_indicator.hideturtle()
selection_indicator.up()

restart_button.showturtle()  # don't show the restart button until everything is initialized


move_record = []


def click_handler(x, y):
	global selection_indicator, board, is_blacks_turn, taken_pieces
	board_edge = board_size / 2
	square_size = board_size / 8
	if x <= board_edge and x >= -board_edge and y <= board_edge and y >= -board_edge:
		ret = logic.onclick(
			selection_indicator,
			is_blacks_turn,
			board,
			int((x + board_edge) // square_size),
			min(7, int((-y + board_edge) // square_size)),  # y calculation sometimes returns 8, so max out at 7
			board_size)
		if ret is not None:  # a move was made
			killed_piece, board, resulting_move = ret
			move_record.append(resulting_move)
			if isinstance(killed_piece, turtle.Turtle):
				util.move_board_pieces(board, board_size, board_size / 8)
				killed_color = logic.convert_file_to_color(killed_piece.shape())
				killed_piece_name = logic.convert_file_to_name(killed_piece.shape())
				killed_piece.goto(taken_indicators[killed_color][killed_piece_name].pos())
				killed_piece.hideturtle()
				taken_pieces[killed_color][killed_piece_name] += 1
				is_blacks_turn = not is_blacks_turn
				util.draw_turn_indicator(turn_indicator, is_blacks_turn, FONT, (0, 370))
				util.update_piece_indicators(indicators_writer, ('PT Sans', 10, 'normal'), taken_pieces, taken_indicators)
			else:
				util.move_board_pieces(board, board_size, board_size / 8)
				is_blacks_turn = not is_blacks_turn
				util.draw_turn_indicator(turn_indicator, is_blacks_turn, FONT, (0, 370))
win.onclick(click_handler)  # noqa: E305 (two lines around top-level defs) - ↓
# function defined only due to Python's insistence to not allow inline function definitions except as exceedingly restricted lambdas.
win.onkeypress(lambda: logic.print_history(move_record), 'h')

win.listen()
win.mainloop()
