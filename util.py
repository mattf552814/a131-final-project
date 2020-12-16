import turtle
from pathlib import Path

colors = ['dark', 'light']  # the possible colors (useful for looping through all possible pieces)
shapes = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']  # the possible pieces (^)

end_rows = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']  # the order of pieces in the end rows
promotable_to = ['rook', 'knight', 'bishop', 'queen']  # the pieces to which a pawn can be promoted


def setup_internal_turtle(trtl):
	'''internal turtles are ones that are not used to draw. Characteristics desirable of those turtles are:
	 - not drawing
	 - not showing the turtle
	 - moving very quickly'''
	trtl.penup()  # lift pen: not drawing
	trtl.hideturtle()  # hide turtle: not showing the turtle
	trtl.speed(0)  # set speed to fastest: moving very quickly


def get_piece_path(color, shape):
	'''Construct the path to a piece icon based on the color and the shape, using `pathlib`.'''
	return str(Path('pieces') / color / f'{shape}.gif')  # convert ``Path`` to string before returning


def register_piece_shapes(screen):
	'''Loop through all possible chess pieces and register them with the screen.'''
	# this could be done with only one loop (looping through the pieces), but this is more readable, and takes the same amount of time.
	for color in colors:  # loop through the colors
		for shape in shapes:  # then loop through the shapes
			# for each color-shape combo, get the path to the icon and register it with the screen.
			screen.register_shape(get_piece_path(color, shape))


def square(trtl, side):
	for i in range(4):  # four sides, loop through each side
		# for each side, draw the side, then turn to draw the next
		trtl.forward(side)  # draw side
		trtl.left(90)  # turn to draw the next


def draw_board(trtl, board_size):
	'''Draw the board. This includes the checkerboard pattern and the borders.'''
	# make sure to show the turtle during the drawing process.
	trtl.showturtle()
	# draw borders, of which there are two. Use a loop to avoid repeated code.
	for border_size in [board_size / 2 + 20, board_size / 2 + 10]:  # for a board size of 600, these are 320 and 310.
		# for each border, there are a few steps.
		# first, move the turtle to the corner.
		trtl.up()  # lift
		trtl.goto(-border_size, -border_size)  # move
		# then, set the turtle down and set its pensize to prepare for drawing
		trtl.down()  # set down
		trtl.pensize(4)  # set the pen size
		# then draw the square
		square(trtl, border_size * 2)
		# at the end we end up facing the same direction we started at (90 * 4 == 360).

	# the next step is to draw the light tan square that forms the light squares on the board. This is a bit nicer on the eyes compared to white-on-black.
	# first, go to the corner
	trtl.up()  # lift pen to not trace since we just want to fill
	trtl.goto(-board_size / 2, -board_size / 2)  # go to corner
	trtl.color('#fdfaf7')  # this is a very light tan
	trtl.begin_fill()
	# draw the square, filling
	square(trtl, board_size)
	trtl.end_fill()

	# there are eight squares, so the square size is an eighth of the board size.
	square_size = board_size / 8
	# the pattern "programmed" below fills a 2x8 region, so draw four times.
	for i in range(4):  # draw this pattern four times
		# for each, follow the pattern after going to the correct spot and setting up.
		# lift since we don't want the stroke, just the fill
		trtl.up()
		# go to the corner, using the loop variable to determine the position (2*i squares to the right from the bottom-left corner of the board)
		trtl.goto(-board_size / 2 + square_size * 2 * i, -board_size / 2)
		# make sure we are facing the right way.
		trtl.seth(0)
		trtl.color('black')
		# start filling before drawing the pattern
		trtl.begin_fill()
		instrs = [  # these represent a bunch of right/left commands that draw a 2x8 checkerboard.
			False, True, False, False, True, True, False, False, True, True,
			False, False, True, True, False, True, True, True, False, False,
			True, True, False, False, True, True, False, False, True, True,
			False, True
		]
		for instr in instrs:  # loop through each instruction to draw the pattern
			# for each instruction, we need to either turn left or right, then move forward.
			if instr: trtl.rt(90)  # true means right
			else: trtl.lt(90)  # false means left
			trtl.forward(square_size)  # then move forward
		trtl.end_fill()  # fill the pattern
	# after the drawing is finished, we don't want the board drawing turtle to clutter the image, so hide it.
	trtl.hideturtle()


def create_piece(screen, color, shape):
	'''Make a chessboard piece for the given color and shape.'''
	# get the path for the piece icon and use it as the turtle's shape.
	trtl = turtle.Turtle(shape=get_piece_path(color, shape))
	# the chess pieces are not meant to draw, so lift the pen.
	trtl.up()
	# finally, return the turtle to the caller.
	return trtl


def create_full_board(screen):
	'''Make the full board of pieces, using ``create_piece``.
	Really the layout of this board could be flipped horizontally, but flipping it vertically would require a lot of constants to change.
	Regardless, it's kind of ambiguous whether white should be on top or bottom when you're looking from the top, so I just made a decision.'''
	# this is made with a concatenation of three arrays: the white pieces, the empty rows, and the black pieces.
	return [
		[create_piece(screen, 'light', piece) for piece in end_rows],  # make white's end row pieces
		[create_piece(screen, 'light', 'pawn') for _ in range(8)]  # make white's pawns
	] + [[None for __ in range(8)] for _ in range(4)] + [  # four rows of empty space
		[create_piece(screen, 'dark', 'pawn') for _ in range(8)],  # make black's pawns
		[create_piece(screen, 'dark', piece) for piece in end_rows]  # make black's end row pieces
	]


def create_taken_piece_indicator(screen):
	'''Create the turtles that are used to indicate taken pieces. This uses the exact same icons as the actual pieces, for a cool effect where captured pieces
	"dissolve into" the taken piece indicator.'''
	# a dictionary is used for easy access to the turtles. Exclude the king since it can't (↓) be captured—when the king is captured the game ends.
	return {color: {shape: create_piece(screen, color, shape) for shape in shapes if shape != 'king'} for color in colors}


def move_board_pieces(board, board_size, square_size):
	'''Move all of the pieces in the board array to their correct position based on their position in the array.'''
	# the starts of the pieces are the centers. The center is found by taking the negative corner of the board and adding back half of the square size.
	piece_start_x = -board_size / 2 + square_size / 2
	# since the board is a square, we can reuse the x-coordinate calculation for the y-coordinate.
	piece_start_y = -piece_start_x
	# theoretically I could have looped through the board array itself, but it would have been a bit of a pain to get indices as well, so this way is better.
	for y in range(8):  # loop through the row indices of the board
		for x in range(8):  # loop through the column indices of the board
			item = board[y][x]  # get the item at those indices
			if isinstance(item, turtle.Turtle):  # if there is a turtle at that position...
				# ...then move the turtle to the position
				# the y-coordinate calculation uses subtraction because of the way turtle coordinates work.
				item.goto(piece_start_x + square_size * x, piece_start_y - square_size * y)


def draw_turn_indicator(trtl, is_blacks_turn, font, pos):
	'''Write the indicator of whose turn it is, on the side of that player.'''
	# first clear any existing writing
	trtl.clear()
	# then go to the correct position. the x-coordinate is simple, but the y is a bit more complicated since vertical centering needs to be considered.
	# in the end the "magic number" seems to be 1.5. Subtracting 1.5 times the font size centers the text on the coordinate.
	# the ternary operation is to put the text below the board if it's black's turn and above if it's white's.
	trtl.goto(pos[0], (pos[1]) * (-1 if is_blacks_turn else 1) - font[1] * 1.5)
	# then write the text itself at that position.
	trtl.write(f"{'Black' if is_blacks_turn else 'White'}’s Turn", align='center', font=font)


def move_piece_indicators(board_size, indicators):
	'''Move the indicators of the taken pieces.'''
	# the y-coordinate of the pieces is above the edge of the board by 150 units.
	y_cor = board_size / 2 + 150
	# the total width that the pieces take up is 2/3rds of the board. Then we divide that by the number of pieces, ...
	# ...which is one minus the length of shapes since we exclude the king.
	step = (board_size / 1.5) / (len(shapes) - 1)
	# the starting position is the left side of that 2/3 middle, which means that we take half of 2/3rds, which is 1/3, ...
	# ...and of course being the left half, it's negative. Then we add half the step to make the pieces be centered.
	start = -board_size / 3 + step / 2
	# though it might arguably be more clear to do a separate loop for the light and the dark, doing it this way makes ...
	# ...the pieces sort of move to their positions in pairs, so I think it's worth it.
	for i, piece in enumerate(indicators['light']):  # `enumerate` to get a loop variable.
		# since looping through a dict gives the keys, we get the light and dark indicators for each piece and move them.
		# the position is found from the loop variable and the step, which were both calculated beforehand.
		# the light pieces have a negated y-coordinate since they are on black's side of the board.
		indicators['light'][piece].goto(start + (i * step), -y_cor)
		indicators['dark'][piece].goto(start + (i * step), y_cor)


def update_piece_indicator(writer, font, number, x, y):
	'''Update a single taken piece indicator. Used by ``update_piece_indicators``.'''
	# using the magic number 1.5, center the text vertically on the given coordinates.
	writer.goto(x, y - font[1] * 1.5)
	# write the given text, converting to a string for good measure. Use the font provided.
	writer.write(str(number), move=False, align='center', font=font)


def update_piece_indicators(writer, font, taken_pieces, indicators):
	'''Update all of the taken piece indicators. Uses ``update_piece_indicator`` under the hood.'''
	# first remove all of the "stale" indicators.
	writer.clear()
	# by updating the indicators like this, we make it so there's only one big jump, significantly speeding up the refresh time.
	# the loop through the colors and indicators to update each.
	for color in colors:
		# for each color, loop through the indicators for that color.
		for piece in indicators[color]:
			# for each indicator, call ``update_piece_indicator`` to write the indicator's value.
			update_piece_indicator(
				writer,  # the turtle
				font,  # the font
				taken_pieces[color][piece],  # the number to write
				indicators[color][piece].xcor(),  # the indicator piece's x coordinate
				indicators[color][piece].ycor() + (40 if color == 'dark' else -40)  # the indicator piece's y coordinate with an offset.
			)


def update_selection(trtl, coord, board_size):
	'''Move and show/hide the blue ring that indicates selection.'''
	# first check if the coordinate is `None`. If it is, then there is no selection and the turtle should be hidden.
	if coord is None:
		# no selection, hide turtle.
		trtl.hideturtle()
	else:
		# there is a selection. The selection is passed as indices, so convert to raw coordinates.
		board_edge = board_size / 2  # the x and y coordinate of any edge of the board (might be negated)
		square_size = board_size / 8  # the size of a square (8 squares in the board)
		trtl.goto(  # move the selection indicator to the selection
			-board_edge + (coord[0] + 0.5) * square_size,  # x is from the left, adding half of a square to the coordinate to center the indicator
			board_edge - (coord[1] + 0.5) * square_size  # y is from the top, doing the same. Again, ``turtle``` handles coordinates in a way that necessitates the...
			# ... negation.
		)
		# finally show the turtle to make the user see the selection.
		trtl.showturtle()


def chunk(iterator, n):
	'''Return the items of the iterator, chunked as groups of ``n`` items.'''
	# first convert the input to an iterator if it isn't one already.
	iterator = iter(iterator)
	# this is a generator function so we can do thing like this.
	while True:
		# this repeats until there is a break statement, generating ``n`` items before yielding them.
		# initialize an empty list to collect the items.
		yield_arr = []
		# needs to be wrapped in try-except since `next` throws `StopIteration` when the iterator "runs dry".
		try:
			# try to collect ``n`` items.
			for _ in range(n):
				# while collecting the items, append them to the collecter array. This throws `StopIteration` when the iterator runs dry.
				yield_arr.append(next(iterator))
		except StopIteration:
			# if this block is reached, the iterator has ran out.
			if len(yield_arr) > 0:  # if there are items left (didn't make an even ``n``-tuple)...
				# ...yield the incomplete array anyway.
				yield yield_arr
			# next time an item is requested, the code will continue from this point.
			# at that time, exit from the loop (which goes to the function's end), since there are no more items to get from the iterator.
			break
		# if `StopIteration` was not thrown, yield the complete ``n``-tuple.
		yield yield_arr
