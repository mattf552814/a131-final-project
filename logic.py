import util
import turtle
from string import ascii_lowercase as alphabet


class RecordedMove:
	piece_characters = {
		'king': 'K',
		'queen': 'Q',
		'rook': 'R',
		'bishop': 'B',
		'knight': 'N',
		'pawn': ''
	}

	def __init__(self, color, piece, from_pos, to_pos, was_capture, promotion):
		self.piece = (color, piece)
		self.from_pos = from_pos
		self.to_pos = to_pos
		self.was_capture = was_capture
		self.promotion = promotion

	def __str__(self):
		return (f'{self.piece_characters[self.piece[1]]}{alphabet[self.from_pos[0]]}{8 - self.from_pos[1]}'
			f'{"x" if self.was_capture else ""}{alphabet[self.to_pos[0]]}{8 - self.to_pos[1]}'
			f'{f"={self.piece_characters[self.promotion]}" if isinstance(self.promotion, turtle.Turtle) else ""}')


class RecordedCastle:
	def __init__(self, color, is_kingside):
		self.color = color
		self.is_kingside = is_kingside

	def __str__(self):
		return '0-0' if self.is_kingside else '0-0-0'


def convert_file_to_name(file):
	return file.split('/')[2].replace('.gif', '')
def convert_file_to_color(file):  # noqa: E302 (two lines between base-level definitions) - these functions are twins
	return file.split('/')[1]


def has_moved(trtl):
	return trtl.heading() != 0  # it's very hacky, but set the turtle's heading to something other than 0 when it's moved


def convert_to_piece_types(turtle_arr):
	return (
		[[(convert_file_to_color(piece.shape()) if isinstance(piece, turtle.Turtle) else None) for piece in row] for row in turtle_arr],
		[[(convert_file_to_name(piece.shape()) if isinstance(piece, turtle.Turtle) else None) for piece in row] for row in turtle_arr]
	)


def check_vertical_move_for_pieces(piece_arr, x_cor, from_y, to_y):
	# step from one beyond the start position to one before the end position. Automatically does nothing if the move is only one.
	y_diff = to_y - from_y
	for y_cor in range(from_y + (1 if y_diff > 0 else -1), to_y, 1 if y_diff > 0 else -1):
		if isinstance(piece_arr[y_cor][x_cor], turtle.Turtle): return False  # piece obstructing path
	return True
def check_horizontal_move_for_pieces(piece_arr, y_cor, from_x, to_x):  # noqa: E302 (two lines between base-level definitions) - these functions are triplets
	# see above for explanation
	x_diff = to_x - from_x
	for x_cor in range(from_x + (1 if x_diff > 0 else -1), to_x, 1 if x_diff > 0 else -1):
		if isinstance(piece_arr[y_cor][x_cor], turtle.Turtle): return False  # piece obstructing path
	return True
def check_diagonal_move_for_pieces(piece_arr, from_x, to_x, from_y, to_y):  # noqa: E302 (two lines between base-level definitions) - (see above)
	x_diff = to_x - from_x
	y_diff = to_y - from_y
	for (x_cor, y_cor) in zip(
		range(from_x + (1 if x_diff > 0 else -1), to_x, 1 if x_diff > 0 else -1),  # code from above
		range(from_y + (1 if y_diff > 0 else -1), to_y, 1 if y_diff > 0 else -1)  # also from above
	):  # move in that diagonal line
		if isinstance(piece_arr[y_cor][x_cor], turtle.Turtle): return False
	return True


def move_is_valid(turtle_arr, from_pos, to_pos):
	# assumes that the from and to coordinates are within the grid, and that from and to are not the same.
	from_x, from_y = from_pos
	to_x, to_y = to_pos
	color_arr, piece_arr = convert_to_piece_types(turtle_arr)
	moving_piece = piece_arr[from_y][from_x]  # indexed by y and then x
	is_light = color_arr[from_y][from_x] == 'light'  # ^
	if color_arr[from_y][from_x] == color_arr[to_y][to_x]:  # only allowed when castling
		if (
			((moving_piece == 'king' and piece_arr[to_y][to_x] == 'rook') or (moving_piece == 'rook' and piece_arr[to_y][to_x] == 'king'))  # check piece types
			and (not has_moved(turtle_arr[from_y][from_x]) and not has_moved(turtle_arr[to_y][to_x]))  # the rook and king can't have been moved
			and check_horizontal_move_for_pieces(piece_arr, from_y, from_x, to_x)  # make sure space between rook and king
		):
			return 'castle'  # must be a special condition
		else:
			return False
	x_diff = to_x - from_x
	y_diff = to_y - from_y
	assert x_diff != 0 or y_diff != 0  # no non-moves
	if moving_piece == 'king':
		# Within a 3x3 square centered on the piece's position.
		return (abs(x_diff) <= 1) and (abs(y_diff) <= 1)
	elif moving_piece == 'queen':
		# Horizontal, vertical, or diagonal.
		if x_diff == 0:  # vertical move
			# I wish I had C pointers here. This is passed as a reference, but still, I wish it could be explicit.
			return check_vertical_move_for_pieces(piece_arr, from_x, from_y, to_y)
		if y_diff == 0:  # horizontal move
			return check_horizontal_move_for_pieces(piece_arr, from_y, from_x, to_x)
		if abs(x_diff) == abs(y_diff):  # diagonal move
			return check_diagonal_move_for_pieces(piece_arr, from_x, to_x, from_y, to_y)
		return False  # if it fell through
	elif moving_piece == 'rook':
		# Horizontal or vertical.
		if x_diff == 0:  # vertical move
			return check_vertical_move_for_pieces(piece_arr, from_x, from_y, to_y)
		if y_diff == 0:  # horizontal move
			return check_horizontal_move_for_pieces(piece_arr, from_y, from_x, to_x)
		return False  # can't move except in a straight line (fall through condition)
	elif moving_piece == 'knight':
		# The knight's move simply is one where one of the differences has an abs of 2 and the other has an abs of 1.
		abs_x_diff = abs(x_diff)
		abs_y_diff = abs(y_diff)
		return (abs_x_diff == 2 and abs_y_diff == 1) or (abs_x_diff == 1 and abs_y_diff == 2)
	elif moving_piece == 'bishop':
		# Diagonal.
		if abs(x_diff) == abs(y_diff):
			return check_diagonal_move_for_pieces(piece_arr, from_x, to_x, from_y, to_y)
		return False  # fall through if the move is not diagonal.
	elif moving_piece == 'pawn':
		# a bit more complicated, since color, position, and capturing must be considered.
		dest_empty = piece_arr[to_y][to_x] is None
		promoting = to_y == (7 if is_light else 0)
		if x_diff == 0:  # non-capture
			if y_diff == (1 if is_light else -1):  # normal move
				return ('promotion' if promoting else True) if dest_empty else False  # only valid for non-capturing moves
			elif y_diff == (2 if is_light else -2) and from_y == (1 if is_light else 6):  # double jump at start
				return ('promotion' if promoting else True) if (dest_empty and piece_arr[to_y - (1 if is_light else -1)][to_x] is None) else False  # can't jump or capture
			return False  # fall through
		elif abs(x_diff) == 1 and not dest_empty and y_diff == (1 if is_light else -1):  # capture
			return 'promotion' if promoting else True
		return False  # fall through


selection_coord = None  # no selection
def onclick(selection_trtl, is_blacks_turn, piece_arr, x, y, board_size):  # noqa: E302 (two lines around top-level defs) - related
	# NOTE: the x and y arguments are ints from 0 to 7 as opposed to raw coords.
	global selection_coord
	if selection_coord is None:  # no selection
		if isinstance(piece_arr[y][x], turtle.Turtle):  # make sure we're actually selecting something
			if ('dark' in piece_arr[y][x].shape()) ^ is_blacks_turn: return  # exit if the selection was not correct based on whose turn it is
			selection_coord = (x, y)
	elif selection_coord[0] != x or selection_coord[1] != y:  # selection, should now move (but make sure the selection is in a different place)
		result_of_check = move_is_valid(piece_arr, selection_coord, (x, y))
		if result_of_check is not False:
			if result_of_check == 'castle':
				selected_piece = piece_arr[y][x].shape()
				move_color = convert_file_to_color(selected_piece)
				if convert_file_to_name(selected_piece) == 'rook':
					is_kingside = x == 7
				else:
					is_kingside = selection_coord[0] == 7
				if is_kingside:
					piece_arr[y][6], piece_arr[y][4] = piece_arr[y][4], None  # move king
					piece_arr[y][5], piece_arr[y][7] = piece_arr[y][7], None  # move rook
				else:  # queenside
					piece_arr[y][2], piece_arr[y][4] = piece_arr[y][4], None  # move king
					piece_arr[y][3], piece_arr[y][0] = piece_arr[y][0], None  # move rook
				selection_coord = None
				util.update_selection(selection_trtl, selection_coord, board_size)
				return None, piece_arr, RecordedCastle(move_color, is_kingside)
			else:
				promoting = result_of_check == 'promotion'
				if promoting:
					promotion = ''
					while promotion not in util.promotable_to:
						choice = turtle.textinput('Pawn Promotion', 'Choose the piece you want to promote to: Rook, Knight, Bishop, or Queen. To cancel the move, press Cancel.')
						if choice is None: return  # if the promotion is cancelled, undo the move.
						else: promotion = choice.lower()  # ignore case
				killed_piece = piece_arr[y][x]
				moving_shape = piece_arr[selection_coord[1]][selection_coord[0]].shape()
				move_obj = RecordedMove(
					convert_file_to_color(moving_shape),
					convert_file_to_name(moving_shape),
					selection_coord,
					(x, y),
					isinstance(killed_piece, turtle.Turtle),  # true if a piece was captured
					promotion if promoting else None  # provide the name of the piece in case of promotion
				)
				if promoting:
					old_shape = piece_arr[selection_coord[1]][selection_coord[0]].shape()
					piece_arr[selection_coord[1]][selection_coord[0]].shape(old_shape.replace('pawn', promotion))
				piece_arr[y][x] = piece_arr[selection_coord[1]][selection_coord[0]]
				piece_arr[y][x].seth(10)  # record that the piece was moved (very hacky method)
				piece_arr[selection_coord[1]][selection_coord[0]] = None
				selection_coord = None
				util.update_selection(selection_trtl, selection_coord, board_size)
				return killed_piece, piece_arr, move_obj
	else:  # double click, just cancel the selection
		selection_coord = None
	util.update_selection(selection_trtl, selection_coord, board_size)


def print_history(history):
	print('History:')
	for i, move_pair in enumerate(util.chunk(history, 2)):
		print(f' {i+1}. {str(move_pair[0])}  {str(move_pair[1]) if len(move_pair) == 2 else ""}')
