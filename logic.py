import util
import turtle
from string import ascii_lowercase as alphabet


class RecordedMove:
	'''Allows a move to be recorded in the move history. Convert to a string to get the algebraic notation.'''
	piece_characters = {  # translation between the full name of the piece and the character used in algebraic notation
		'king': 'K',
		'queen': 'Q',
		'rook': 'R',
		'bishop': 'B',
		'knight': 'N',
		'pawn': ''
	}

	def __init__(self, color, piece, from_pos, to_pos, was_capture, promotion):
		'''Record a move.
		Arguments:
		color: the color of the piece that was moved
		piece: the shape of the piece that was moved
		from_pos: a pair of coordinates that represents where the piece moved from
		to_pos: a pair of coordinates that represents where the piece moved to
		was_capture: if the piece captured another with this move
		promotion: if a pawn is promoted by this move, this field holds the piece that it was promoted to. If no promotion, it is None.'''
		self.piece = (color, piece)
		self.from_pos = from_pos
		self.to_pos = to_pos
		self.was_capture = was_capture
		self.promotion = promotion

	def __str__(self):
		'''Allow the move to be converted to algebraic notation with str(move).'''
		return (f'{self.piece_characters[self.piece[1]]}'  # the character for the piece
			f'{alphabet[self.from_pos[0]]}{8 - self.from_pos[1]}'  # the position is moved from in letter-number format
			# ↓ the position it moved to in letter-number format, including an 'x' if there was a capture
			f'{"x" if self.was_capture else ""}{alphabet[self.to_pos[0]]}{8 - self.to_pos[1]}'
			f'{f"={self.piece_characters[self.promotion]}" if self.promotion is not None else ""}')  # indicate a promotion if there was one


class RecordedCastle:
	'''A companion to ``RecordedMove``, record a castle.'''
	def __init__(self, color, is_kingside):
		'''Record a castle.
		Arguments:
		color: the color of the castling pieces
		is_kingside: a boolean indicating if the move was a kingside (short) castle. If False, it was a queenside (long) castle.
		'''
		self.color = color
		self.is_kingside = is_kingside

	def __str__(self):
		'''Allow the move to be converted to algebraic notation with str(move).'''
		return '0-0' if self.is_kingside else '0-0-0'


class PassantReference:
	'''A utility class to record that a pawn moved through a space when it moved two spaces on its first move.'''
	def __init__(self, trtl):
		'''Create an en passant reference.
		Arguments:
		trtl: a reference to the pawn turtle that passed through the space.'''
		self.trtl = trtl


def convert_file_to_name(file):
	'''Take the piece name out of a path to a piece icon.'''
	return file.split('/')[2].replace('.gif', '')
def convert_file_to_color(file):  # noqa: E302 (two lines between base-level definitions) - these functions are twins
	'''Take the piece color out of a path to a piece icon.'''
	return file.split('/')[1]


def has_moved(trtl):
	'''Check whether a turtle is considered as having moved. Piece turtles must be turned when they are moved to record it for this function to work.
	The turtle library doesn't rotate images when they're used as a turtle shape, so this doesn't have any visual effect.'''
	return trtl.heading() != 0  # it's very hacky, but set the turtle's heading to something other than 0 when it's moved


def convert_to_piece_types(turtle_arr):
	'''Convert the array of turtles to two arrays, the colors of the turtles and the piece types (aka names/shapes) of the turtles.'''
	return (
		[[(convert_file_to_color(piece.shape()) if isinstance(piece, turtle.Turtle) else None) for piece in row] for row in turtle_arr],  # the colors
		[[(convert_file_to_name(piece.shape()) if isinstance(piece, turtle.Turtle) else piece) for piece in row] for row in turtle_arr]  # the types/names/shapes
	)


def exclusive_range(start, stop):
	'''Make a range similar to ``range``, but with a few tweaks.
	First, exclude the start number from the range.
	Second, automatically set the step to either 1 or -1 so that the range always goes from `start` to `stop` even if `stop` is less than `start`.'''
	diff = stop - start
	# step from one beyond the start position to one before the end position. Automatically does nothing if the move is only one.
	return range(start + (1 if diff > 0 else -1), stop, 1 if diff > 0 else -1)


def check_vertical_move_for_pieces(piece_arr, x_cor, from_y, to_y):
	'''Using ``exclusive_range``, check the spaces between two y-coordinates for pieces. Used by ``move_is_valid`` to check for obstructions vertically.'''
	for y_cor in exclusive_range(from_y, to_y):
		# at each spot, check if there is a turtle. If there is, exit early by returning False.
		if isinstance(piece_arr[y_cor][x_cor], turtle.Turtle): return False  # piece obstructing path
	return True
def check_horizontal_move_for_pieces(piece_arr, y_cor, from_x, to_x):  # noqa: E302 (two lines between base-level definitions) - these functions are triplets
	'''Using ``exclusive_range``, check the spaces between two x-coordinates for pieces. Used by ``move_is_valid`` to check for obstructions horizontally.'''
	for x_cor in exclusive_range(from_x, to_x):
		# at each spot, check if there is a turtle. If there is, exit early by returning False.
		if isinstance(piece_arr[y_cor][x_cor], turtle.Turtle): return False  # piece obstructing path
	return True
def check_diagonal_move_for_pieces(piece_arr, from_x, to_x, from_y, to_y):  # noqa: E302 (two lines between base-level definitions) - (see above)
	'''Using ``exclusive_range``, check the spaces along a diagonal (45 + 90n deg) for pieces. Used by ``move_is_valid`` to check for obstructions along a
	diagonal path. Strange things will happen if the move is not actually a diagonal (45 + 90n deg), but since this is only used internally it's not a problem.'''
	for (x_cor, y_cor) in zip(  # by zipping and unpacking we ensure in a simple way that each iteration of the for loop will be given the proper x and y.
		exclusive_range(from_x, to_x),
		exclusive_range(from_y, to_y)
	):  # move in that diagonal (45 + 90n deg) line
		# at each spot, check if there is a turtle. If there is, exit early by returning False.
		if isinstance(piece_arr[y_cor][x_cor], turtle.Turtle): return False  # piece obstructing path
	return True


def strip_passant_references(arr):
	'''En passant capture is only valid in the move directly after the pawn's jump. For that reason, the ``PassantReference``s must be stripped after checking
	for a en passant capture and before moving on to processing the next move. This function just replaces any instance of a ``PassantReference`` with `None`.'''
	return [[(None if isinstance(piece, PassantReference) else piece) for piece in row] for row in arr]


def move_is_valid(turtle_arr, from_pos, to_pos):
	'''The most important function in the entire codebase. Checks if a move is valid and if it induces any special conditions.
	Many of the other functions in this file exist to serve this one.
	The construction of this function is just a ton of branching with conditionals.'''
	# assumes that the from and to coordinates are within the grid, and that from and to are not the same.
	from_x, from_y = from_pos  # unpack
	to_x, to_y = to_pos  # unpack
	color_arr, piece_arr = convert_to_piece_types(turtle_arr)  # convert the turtle objects to colors and piece names.
	moving_piece = piece_arr[from_y][from_x]  # indexed by y and then x since the data format is columns within rows
	is_light = color_arr[from_y][from_x] == 'light'  # check whether the currently moving piece is white. If False, that means the piece is black.
	if color_arr[from_y][from_x] == color_arr[to_y][to_x]:  # only allowed when castling
		# For almost every move, the moving piece must not be the same color as the destination piece (if there is one). Castling is the only exception.
		if (  # this code checks if the move is a castle.
			((moving_piece == 'king' and piece_arr[to_y][to_x] == 'rook') or (moving_piece == 'rook' and piece_arr[to_y][to_x] == 'king'))  # check piece types
			and (not has_moved(turtle_arr[from_y][from_x]) and not has_moved(turtle_arr[to_y][to_x]))  # the rook and king can't have been moved
			and check_horizontal_move_for_pieces(piece_arr, from_y, from_x, to_x)  # make sure space between rook and king is empty
		):
			# in that case we return the special condition 'castle'. Note that any sort of special condition like this effectively counts as True
			# (see the relevant section in ``onclick`` for more detail)
			return 'castle'
		else:
			# if the move isn't a castle, then it's not valid so we return False.
			return False
	x_diff = to_x - from_x  # worth it to calculate now since it's used very often below
	y_diff = to_y - from_y  # ^
	assert x_diff != 0 or y_diff != 0  # no non-moves (this will never occur in reality but it's good to check)
	if moving_piece == 'king':
		# this would be better if it could be a switch statement, but python-dev doesn't like that.
		# kings move within a 3x3 square centered on the piece's position.
		# in the diagram below (as well as all other to follow), * represents allowed moves, x represents unallowed moves, arrows represent extendablity (piece can
		# move along that line as far as the player desires), and @ represents the piece.
		# * * *
		# * @ *
		# * * *
		return (abs(x_diff) <= 1) and (abs(y_diff) <= 1)
	elif moving_piece == 'queen':
		# Can move horizontally, vertically, or diagonally (45 + 90n deg).
		# (the diagram below is clipped)
		# ↖ x ↑ x ↗
		# x * * * x
		# ← * @ * →
		# x * * * x
		# ↙ x ↓ x ↘
		if x_diff == 0:  # vertical move (also established that from_x == to_x)
			# the queen must be moving vertically here, so check the vertical move for pieces. The move is allowed if the route is empty.
			# I wish I had C pointers here. This is passed as a reference, but still, I wish it could be explicit.
			return check_vertical_move_for_pieces(piece_arr, from_x, from_y, to_y)
		if y_diff == 0:  # horizontal move (also establishes that from_y == to_y)
			# the queen must be moving horizontally here, so check the horizontal move for pieces. The move is allowed if the route is empty.
			# this statement is not an `elif` because the `return` statement makes it redundant.
			return check_horizontal_move_for_pieces(piece_arr, from_y, from_x, to_x)
		if abs(x_diff) == abs(y_diff):  # diagonal move
			# Diagonal moves are verified by checking that the abs of the x difference equals the abs of the y difference.
			# (Remember tan(45deg+n*90deg) == y/x == 1 or -1, and for y/x to == 1 or -1, abs x must == abs y.)
			# the queen must be moving diagonally (45 + 90n deg) here, so check the diagonal move for pieces. The move is allowed if the route is empty.
			# this statement is not an `elif` because the `return` statements above make it redundant.
			return check_diagonal_move_for_pieces(piece_arr, from_x, to_x, from_y, to_y)
		# ↓ This is not wrapped in an `else` block because the return statements above make it redundant.
		return False  # if it fell through the if statements, then the move is not vertical, horizontal, or diagonal (45 + 90n deg) and the move is invalid.
	elif moving_piece == 'rook':
		# Can move horizontally or vertically.
		# (the diagram below is clipped)
		# x ↑ x
		# ← @ →
		# x ↓ x
		if x_diff == 0:  # vertical move (also establishe that from_x == to_x)
			# the rook must be moving vertically here, so check the vertical move for pieces. The move is allowed if the route is empty.
			return check_vertical_move_for_pieces(piece_arr, from_x, from_y, to_y)
		if y_diff == 0:  # horizontal move (also establishes that from_y == to_y)
			# this statement is not an `elif` because the `return` statements above make it redundant.
			# the rook must be moving horizontally here, so check the horizontal move for pieces. The move is allowed if the route is empty.
			return check_horizontal_move_for_pieces(piece_arr, from_y, from_x, to_x)
		# ↓ This is not wrapped in an `else` block because the return statements above make it redundant.
		return False  # if it fell through the if statements, then the move is not vertical or horizontal and the move is invalid.
	elif moving_piece == 'knight':
		# The knight's move is just one where one of the differences has an abs of 2 and the other has an abs of 1.
		# move diagram:
		# x * x * x
		# * x x x *
		# x x @ x x
		# * x x x *
		# x * x * x
		abs_x_diff = abs(x_diff)  # store in a variable since it would be calculated twice otherwise
		abs_y_diff = abs(y_diff)  # ^
		return (abs_x_diff == 2 and abs_y_diff == 1) or (abs_x_diff == 1 and abs_y_diff == 2)  # either condition is possible and both are permitted.
	elif moving_piece == 'bishop':
		# Can move diagonally (45 + 90n deg). This is verified by checking that the abs of the x difference equals the abs of the y difference.
		# (Remember tan(45deg+n*90deg) == y/x == 1 or -1, and for y/x to == 1 or -1, abs x must == abs y.)
		# move diagram:
		# ↖ x ↗
		# x @ x
		# ↙ x ↘
		if abs(x_diff) == abs(y_diff):
			# the bishop must be moving diagonally (45 + 90n deg) here (see above), so check the diagonal move for pieces. The move is allowed if the route is empty.
			return check_diagonal_move_for_pieces(piece_arr, from_x, to_x, from_y, to_y)
		return False  # if it fell through the if statement, then the move is not diagonal and is therefore invalid.
	elif moving_piece == 'pawn':
		# there are many things to consider when checking a pawn's move. At the very most basic, pawns can move forward away from their player.
		# however, they can only capture when they move diagonally by one square. Also, they can move two squares on their first move. But then
		# another pawn can capture the first pawn if it "captures" the square that the first pawn moved over (which is supposed to be empty!).
		# oh, and don't forget about promotion! ... this gets complicated quickly. luckily we can break it down into simple steps.

		# first check if the destination is empty. when we check this, we consider en passant references as occupied squares. this might have been an issue since we
		# use this also to make sure that pawns moving normally *aren't* capturing, but it doesn't matter since it's not possible for a pawn to be moving forward
		# from behind a pawn that just created an en passant reference. the fact that this is guaranteed allows us to simplify the code.
		dest_empty = not isinstance(turtle_arr[to_y][to_x], (turtle.Turtle, PassantReference))  # (passing a tuple returns True if the obj is an instance of any)
		# then check if the pawn should be promoted. This depends on the color of the piece, so find it based on that.
		promoting = to_y == (7 if is_light else 0)
		# now determine whether the move is capturing or not
		if x_diff == 0:  # when the move is vertical it must be a non-capture move
			# now we need to determine whether the move is a normal move or the two-jump that creates an en passant reference.
			if y_diff == (1 if is_light else -1):  # moving forward (direction based on color) by one = normal move
				# if the destination isn't empty (since pawns can't capture when they make their normal move), return False. Otherwise, return the promotion special
				# condition if we are promoting, or just True if not.
				return ('promotion' if promoting else True) if dest_empty else False
			elif y_diff == (2 if is_light else -2) and from_y == (1 if is_light else 6):  # double jump moves are only allowed when the pawn hasn't moved. However...
				# ...pawns can only move forward, so we don't need to check whether the pawn has moved with ``has_moved``, and instead can just verify the position. ...
				# ... of course we also check that the move is the correct distance.
				# ---
				# we need to make sure that the destination is empty, which we do using ``dest_empty``. The double jump move is a bit of a misnomer since the pawn can't
				# actually jump over a piece, so we need to make sure the spot that the pawn is jumping over is also empty. If it is, then this is a special condition
				# where an en passant reference needs to be created. If the checks do not pass, then the move is invalid.
				# I discussed above why the fact that ``dest_empty`` is False for an en passant reference is not an issue. See line 229 (or somewhere near there).
				return 'make-passant' if (dest_empty and piece_arr[to_y - (1 if is_light else -1)][to_x] is None) else False
			# ┌ if neither of these conditions was satisfied, then the move is invalid. Again, this doesn't need to be in an `else` statement since the if statements
			# ↓ are both guaranteed to return something and exit the function.
			return False
		elif (  # otherwise (i.e., if the move is not vertical), then this needs to be a capturing move, so we'll do all the verification here:
			abs(x_diff) == 1  # - the move moves horizontally by one (combined with the below statements, verifies that the move is diagonal)
			and not dest_empty  # - this is a capture (also works for en passant references; see the initialization of dest_empty near line 232)
			and y_diff == (1 if is_light else -1)  # - the move is in the correct direction based on the color of the moving piece
		):  # if all that is true then this is a valid capture
			# since pawns can promote on capture, we return the promotion special condition if that is the case, otherwise just True.
			return 'promotion' if promoting else True
		return False  # if neither of those conditions was satisfied, then we know that the move is invalid.
	# (there is no `return False` here because the piece could never not be one of the above types.)


selection_coord = None  # initialize with no selection (what None indicates)
def onclick(selection_trtl, is_blacks_turn, piece_arr, x, y, board_size):  # noqa: E302 (two lines around top-level defs) - related
	'''This is the second most important function in this file. It handles the move selection and the manipulation of the piece array.'''
	# NOTE: the x and y arguments are ints from 0 to 7 as opposed to raw coords.
	global selection_coord  # allow us to modify this from within the function
	if selection_coord is None:
		# a selection coordinate of None indicates that there is no mark set, so the user is setting the mark.
		if isinstance(piece_arr[y][x], turtle.Turtle):  # by checking if the piece is a turtle, we are making sure we're actually selecting a piece
			# now that we know we're selecting a piece, we have to verify that the piece is one the current player is allowed to select.
			# with the following statement, the function exits if the selection was not correct based on whose turn it is. The XOR operator has so many uses. In this
			# case we are using it as a "difference" operator, which checks if the inputs differ, returning True if they do, otherwise False. The first argument
			# is whether the piece being clicked is a black piece. While ``convert_piece_to_name`` could have been used here along with a test for equality, I think
			# that using this method that returns a boolean naturally is more concise and simpler.
			# The other side of the XOR is the variable passed in by the caller to indicate if it is black's turn. Together, the XOR will return False is the piece is
			# white and it's white's turn, or if the piece is black and it's black's turn. If the piece color and the player whose turn it is don't match, the XOR
			# returns True.
			# If it does return True, then the piece can't be selected, so we exit immediately with a bare `return`.
			if ('dark' in piece_arr[y][x].shape()) ^ is_blacks_turn: return
			# If not, then we set the selection coordinate to the correct value. Later on at the end of this function we update the selection indicator.
			selection_coord = (x, y)
	elif selection_coord[0] != x or selection_coord[1] != y:  # make sure that the click position is different from the marked position before making the move.
		# if we've reached this section, then we are making a move.
		# begin by checking whether the result is valid. This uses the ``move_is_valid`` function.
		result_of_check = move_is_valid(piece_arr, selection_coord, (x, y))
		# instead of using something like `if result_of_check`, we use the below code because there are special conditions that cause ``move_is_valid`` to return a
		# string, so we just check if it didn't return False. Since False is like None in that there's only one instance of it throughout the duration of the
		# program, we use the `is not` operator instead of `!=`.
		if result_of_check is not False:
			# in this case we know that some sort of move is being made, but we need to check for some special conditions that have different behavior from the norm.
			if result_of_check == 'castle':  # castling is one such condition
				# in this block we need to handle two moves instead of just one, hence it being separate from the "normal move" block.
				selected_piece = piece_arr[y][x].shape()  # save since it's used often
				move_color = convert_file_to_color(selected_piece)  # ^
				# we need to find the piece that is the rook, to determine whether the castle is kingside (short) or queenside (long).
				if convert_file_to_name(selected_piece) == 'rook':  # remember `selected_piece = piece_arr[y][x].shape()`.
					# therefore we know that the rook was selected after the king, and therefore the x-coordinate of the rook is `x`.
					is_kingside = x == 7
				else:
					# if not, we know that the rook was selected first, so we need to use ``selection_coord`` to get it.
					is_kingside = selection_coord[0] == 7
				# either way, now we know if the castle is kingside or not. the following code depends on it.
				# within both of the blocks below, `y` is used for the coordinate. This is just simpler than using something like `7 if move_color == 'dark' else 0`,
				# and it is guaranteed to be identical, because we know that the pieces haven't moved (see ``move_is_valid`` for more info).
				if is_kingside:  # process the kingside castle
					# we need to move the king and rook. We don't need to worry about swapping since we know the spaces are empty
					# (and they can't be en passant references). Therefore we can just replace the old square's piece with `None`.
					piece_arr[y][6], piece_arr[y][4] = piece_arr[y][4], None  # move king
					piece_arr[y][5], piece_arr[y][7] = piece_arr[y][7], None  # move rook
				else:  # process the queenside castle, which is what it is if it isn't kingside.
					# we also need to move the king and the rook, but here we are moving them to different positions. See above for more detail.
					piece_arr[y][2], piece_arr[y][4] = piece_arr[y][4], None  # move king
					piece_arr[y][3], piece_arr[y][0] = piece_arr[y][0], None  # move rook
				selection_coord = None  # reset the selection coord as we do for normal moves.
				util.update_selection(selection_trtl, selection_coord, board_size)  # consequently update the selection
				# returning: captured piece (None since there is no capture in castling), piece array, the move to be recorded (naturally a ``RecordedCastle``)
				return None, piece_arr, RecordedCastle(move_color, is_kingside)
			else:
				# this is a "normal" move. By normal I mean that one piece is moving, and there is an opportunity for a capture.
				# these special conditions below don't necesitate a separate section, and can instead be integrated into the normal move handler.
				promoting = result_of_check == 'promotion'  # pawn being promoted (will trigger dialog to pick promotion)
				make_passant = result_of_check == 'make-passant'  # a pawn is moving two spaces (necessitates the creation of a ``PassantReference``)
				if promoting:  # handle the promotion
					# this is the piece that the pawn is being promoted to
					promotion = ''
					# ``util.promotable_to`` is the list of pieces that a pawn can be promoted to (rook, knight, bishop, queen). Loop while the selected promotion is not
					# one of those.
					while promotion not in util.promotable_to:
						# this block serves to let the user choose the promotion.
						# show a dialog asking the user to input their chosen promotion.
						choice = turtle.textinput('Pawn Promotion', 'Choose the piece you want to promote to: Rook, Knight, Bishop, or Queen. To cancel the move, press Cancel.')
						# when the dialog is canceled, None is returned. In that case, cancel the move entirely (no changes are made) by returning early.
						if choice is None: return
						# otherwise, store the answer in the promotion variable to be checked when the loop repeats.
						else: promotion = choice.lower()  # ignore case
				killed_piece = piece_arr[y][x]  # save the captured piece since it is replaced by the moving piece further along
				# if ``killed_piece`` is an en passant reference, then the pawn it references should be the one to be captured. This can easily be accomplished:
				if isinstance(killed_piece, PassantReference): killed_piece = killed_piece.trtl  # replace ``killed_piece`` with the piece that it references.
				moving_shape = piece_arr[selection_coord[1]][selection_coord[0]].shape()  # store for use throughout the next segments.
				# another reason that the castling needed to be separate was that it has a completely different algebraic notation, and therefore a different class
				# to record it in the move history. Here we use the more generic ``RecordedMove`` to record information about the move.
				move_obj = RecordedMove(
					convert_file_to_color(moving_shape),  # color of the moving piece
					convert_file_to_name(moving_shape),  # type/shape/name of the moving piece
					selection_coord,  # moving from
					(x, y),  # moving to
					isinstance(killed_piece, turtle.Turtle),  # True if a piece was captured
					promotion if promoting else None  # provide the name of the piece in case of promotion, None otherwise
				)
				if promoting:  # we need to handle the actual replacement of the pawn. Since all the code simply relies on the turtle's shape to determine its type/...
					# ...shape/name, by changing the shape we have done all that is required to change the piece.
					# ---
					# record the old shape to shorten the line length and also make more clear what is happening.
					old_shape = piece_arr[selection_coord[1]][selection_coord[0]].shape()
					# string manipulation, yes indeed! replace `pawn` in the old shape string with the chosen promotion and set the turtle's shape to the resulting string.
					piece_arr[selection_coord[1]][selection_coord[0]].shape(old_shape.replace('pawn', promotion))
				# move the old piece to the new position in the data structure, replacing the old piece (it is saved in ``killed_piece``)
				piece_arr[y][x] = piece_arr[selection_coord[1]][selection_coord[0]]
				# by setting the piece's heading, we record that it has been moved. see ``has_moved`` for more information about how this works and why.
				piece_arr[y][x].seth(10)
				# after analyzing the move for validity and special conditions, but before making the new en passant references, we need to remove any old ones.
				piece_arr = strip_passant_references(piece_arr)
				# now we make any en passant references if they are necessary
				if make_passant:  # if an en passant reference was made
					# as opposed to manipulating ``y`` to get the coordinate, we know what the coordinate will be so we use the known coordinate as a literal instead.
					piece_arr[5 if is_blacks_turn else 2][x] = PassantReference(piece_arr[y][x])
				# where the moving piece used to be, we replace with `None` to make it empty. There is no possibility that this will remove an en passant reference
				# since the pawn has to move two pieces, over the position where the reference will be, to make one.
				piece_arr[selection_coord[1]][selection_coord[0]] = None
				# reset the selection
				selection_coord = None
				# consequently, update the selection immediately to give feedback
				util.update_selection(selection_trtl, selection_coord, board_size)
				# returning: the piece that was captured, the modified piece array, and the ``RecordedMove`` representing this move.
				return killed_piece, piece_arr, move_obj
	else:  # n this case the user clicked where the selection already is.
		# that means that they want to remove the selection, so do that.
		selection_coord = None
	# this code will only be reached if the `else` statement is the one that is run. Update the selection that was modified there. I considered putting this in
	# the `else` statement, but wanted to show that it was the final action if nothing was returned.
	util.update_selection(selection_trtl, selection_coord, board_size)
	# implicitly return None.


def print_history(history):
	'''Print the move history passed through ``history`` in algebraic notation'''
	# a heading
	print('History:')
	# loop through the pairs of moves to print each one.
	for i, move_pair in enumerate(util.chunk(history, 2)):
		# print the move pair. Begin with the move number, then print the first move, then print the second if it exists. The moves are converted to strings to get
		# algebraic notation from the ``RecordedMove``/``RecordedCastle``. If there is an odd number of moves, then ``move_pairs`` is a monuple (1-tuple). For that
		# reason we can't use unpacking and instead have to index and check the length of the tuple before printing the second move (since it might not exist).
		print(f' {i+1}. {str(move_pair[0])}  {str(move_pair[1]) if len(move_pair) == 2 else ""}')
