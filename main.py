import util
import logic
import turtle
import gc

# -- PRINT INSTRUCTIONS

# the instructions are stored in a file since they are a decent amount of text.
with open('instructions.txt', 'r') as instructions_f:
	# using the open file, loop through it (files are `Iterable`s.)
	for line in instructions_f:
		# for each line, print the line. Have `print` add no ending since there is already a line ending from the file.
		print(line, end='')
	# wait for the user to press Enter. This is accomplished by asking for input without an actual prompt.
	input('')

# -- BEGIN GAME

# get a reference to the screen.
win = turtle.Screen()

# make a turtle to draw the board
board_turtle = turtle.Turtle()
# set it up at a very fast speed
board_turtle.speed(10)

is_blacks_turn = False  # false means it's white's turn

# store the font config in a variable as opposed to having it all over the place as a literal.
FONT_SIZE = 20
FONT = ('sans-serif', FONT_SIZE, 'normal')

# register the icons for the pieces with the screen (see the definition for much more info).
util.register_piece_shapes(win)

# make the indicator that shows whose turn it is.
turn_indicator = turtle.Turtle()
# set it up as an internal turtle (pen up, hidden, speed 0).
util.setup_internal_turtle(turn_indicator)
# use the turtle to draw the first turn indicator.
util.draw_turn_indicator(turn_indicator, is_blacks_turn, FONT, (0, 370))

# store the board size in a variable as opposed to having it all over the place as a literal.
board_size = 600

# register the restart button shape (``util.register_piece_shapes`` only registers the chess pieces.)
win.register_shape('restart_button.gif')
# create a turtle using that shape.
restart_button = turtle.Turtle(shape='restart_button.gif')
# set it up as an interal turtle (pen up, hidden, speed 0). It will be shown once the board is set up.
util.setup_internal_turtle(restart_button)
# move it to the left of the board.
restart_button.goto(-(board_size / 2) - 100, 0)
def restart_program():  # noqa: E302 (two lines before function) - Should be an anonymous fn
	'''A function to gather all the actions necessary to reset the data and interface. I considered combining this with the initialization you will see below,
	but decided in the end that the processes are different enough that they would be more confusing that it's worth if they were combined.'''
	global board, taken_pieces, indicators_writer, taken_indicators, move_record, is_blacks_turn, turn_indicator, logic  # many, many variables to modify...
	# reset the selection...
	logic.selection_coord = None
	# ...and update the indicator.
	util.update_selection(selection_indicator, logic.selection_coord, board_size)
	# clear the writers. Their indicators will be rewritten later.
	turn_indicator.clear()
	indicators_writer.clear()
	# hide and then delete every piece.
	for row in board:
		# for each row in the board...
		for piece in row:
			# for each piece in that row...
			if isinstance(piece, turtle.Turtle):
				# if that piece is a turtle...
				# hide the turtle...
				piece.hideturtle()
				# and then delete it...
				del piece
	# replace the old board with a new one, nuking the references to the old turtles.
	board = util.create_full_board(win)
	# tell the garbage collector to collect all of the turtles with no more references.
	gc.collect()
	# reset the dict that tracks the taken pieces for each player.
	taken_pieces = {color: {shape: 0 for shape in util.shapes} for color in util.colors}
	# move the new board pieces to their proper positions.
	util.move_board_pieces(board, board_size, board_size / 8)
	# update the taken piece indicators (all of them are zero).
	util.update_piece_indicators(indicators_writer, ('sans-serif', 10, 'normal'), taken_pieces, taken_indicators)
	# reset the move history.
	move_record = []
	# make it be white's turn again.
	is_blacks_turn = False
	# write the indicator that shows whose turn it is (white's).
	util.draw_turn_indicator(turn_indicator, is_blacks_turn, FONT, (0, 370))
# finally, bind this function to clicking the restart button from before.
restart_button.onclick(lambda *_: restart_program())  # noqa: E305 (two lines after function) - Should be an anonymous fn

# draw the board (checkedboard and borders).
util.draw_board(board_turtle, board_size)

# make the pieces.
board = util.create_full_board(win)
# make the dict that keeps track of the taken pieces for each player.
taken_pieces = {color: {shape: 0 for shape in util.shapes} for color in util.colors}
# move the pieces on the board to their proper positions (see the def for more info).
util.move_board_pieces(board, board_size, board_size / 8)

# make the writer for the taken piece indicators.
indicators_writer = turtle.Turtle()
# set it up as an internal turtle (pen up, hidden, speed 0)
util.setup_internal_turtle(indicators_writer)
# create the turtles to show the icons for the taken indicators.
taken_indicators = util.create_taken_piece_indicator(win)

# move the taken piece indicators to their proper positions.
util.move_piece_indicators(board_size, taken_indicators)
# write the indicators above the pieces that were just moved, using the writer turtle that was just created.
util.update_piece_indicators(indicators_writer, ('sans-serif', 10, 'normal'), taken_pieces, taken_indicators)

# register the selection halo shape (``util.register_piece_shapes`` only registers the chess pieces).
win.register_shape('selection.gif')
# make the turtle that is the selection indicator.
selection_indicator = turtle.Turtle(shape='selection.gif')
# set is up as an internal turtle (pen up, hidden, speed 0). The turtle is hidden until a selection is made.
util.setup_internal_turtle(selection_indicator)

# show the restart button now that the whole interface is set up.
restart_button.showturtle()


# create an empty list to hold the move history.
move_record = []


def click_handler(x, y):
	'''Handles any move the player makes. Translates raw coordinates into clicked squares and calls ``logic.onclick``.'''
	global selection_indicator, board, is_blacks_turn, taken_pieces  # many variables to be modified...
	# the edge of the board is half of the board's size, since the board is centered around (0, 0).
	board_edge = board_size / 2
	# the squares are each an eighth of the board since the board has eight squares.
	square_size = board_size / 8
	# make sure that the click was within the board.
	if x <= board_edge and x >= -board_edge and y <= board_edge and y >= -board_edge:
		# if the click is within the board, we can continue processing it.
		# begin by having ``logic.onclick`` modify the piece array as necessary.
		ret = logic.onclick(
			selection_indicator,  # the selection indicator may need to be moved.
			is_blacks_turn,  # must know whose turn it is to validate a click (white can't move black's pieces and vice versa)
			board,  # the actual piece array
			int((x + board_edge) // square_size),  # the x index of the clicked square. Goes from 0 to 7.
			min(7, int((-y + board_edge) // square_size)),  # the y index of the clicked square. Goes from 0 to 7. y calculation sometimes returns 8, so max out at 7.
			board_size  # the size of the board, used for various movements within the function
		)
		# check if a move was made (the function will return None if there was no move).
		if ret is not None:
			# if a move was made, we can now process that move.
			# unpack the return value. The function returns the captured piece if there was one, otherwise `None`; the modified piece array; and the...
			# ...``logic.RecordedMove`` or ``logic.RecordedCastle`` that will represent the move in the move history.
			killed_piece, board, resulting_move = ret
			# add the move object to the move history.
			move_record.append(resulting_move)
			# check whether a piece was captured in the move.
			if isinstance(killed_piece, turtle.Turtle):
				# if a piece was captured, we need to process the implications.
				# first move the pieces of the board (this is in common).
				util.move_board_pieces(board, board_size, board_size / 8)
				# then find the color and the name/shape/type of the piece that was captured.
				killed_color = logic.convert_file_to_color(killed_piece.shape())  # stored in a variable since it used multiple times.
				killed_piece_name = logic.convert_file_to_name(killed_piece.shape())  # ^
				# move the piece to its indicator and then hide it, making it appear to dissolve into that indicator in a very visually descriptive way.
				killed_piece.goto(taken_indicators[killed_color][killed_piece_name].pos())
				killed_piece.hideturtle()
				# increment the counter for that name/shape/type and color of captured piece.
				taken_pieces[killed_color][killed_piece_name] += 1
				# change the turn. This is done before redoing the indicators to prevent the person who just moved from making another move while the indicators are...
				# ...updating. (also in common)
				is_blacks_turn = not is_blacks_turn
				# update the indicators, starting with the indicator of whose turn it is to reflect the change just made... (last part in common)
				util.draw_turn_indicator(turn_indicator, is_blacks_turn, FONT, (0, 370))
				# ...then moving on that of the captured pieces (now updated with the just-captured piece).
				util.update_piece_indicators(indicators_writer, ('sans-serif', 10, 'normal'), taken_pieces, taken_indicators)
			else:
				# if no piece was captured, there are only a few operations we need to do. Some code is duplicated here, but the order matters so this couldn't be...
				# ...converted to a function unfortunately.
				# first move the pieces of the board
				util.move_board_pieces(board, board_size, board_size / 8)
				# then change the turn, before updating the turn indicator for the reason stated above.
				is_blacks_turn = not is_blacks_turn
				# finally update the indicator of whose turn it is to reflect that change.
				util.draw_turn_indicator(turn_indicator, is_blacks_turn, FONT, (0, 370))
		# (if no move was made then we're done here and can exit.)
# attach this handler to the window's click event.
win.onclick(click_handler)  # noqa: E305 (two lines around top-level defs) - ↓
# function defined only due to Python's insistence to not allow inline function definitions except as exceedingly restricted lambdas.

# and finally attach the function to print the history to the keypress event for the letter H.
win.onkeypress(lambda: logic.print_history(move_record), 'h')

# listen for keypresses.
win.listen()
# make the window persist in its event loop.
win.mainloop()
