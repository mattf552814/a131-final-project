def convert_file_to_name(file):
	return file.split('/')[2].replace('.gif', '')
def convert_file_to_color(file):  # noqa: E302 (two lines between base-level definitions) - these functions are twins
	return file.split('/')[1]


def convert_to_piece_types(turtle_arr):
	return (
		[[(None if piece is None else convert_file_to_color(piece.shape())) for piece in row] for row in turtle_arr],
		[[(None if piece is None else convert_file_to_name(piece.shape())) for piece in row] for row in turtle_arr]
	)


def check_vertical_move_for_pieces(piece_arr, x_cor, from_y, to_y):
	# step from one beyond the start position to one before the end position. Automatically does nothing if the move is only one.
	y_diff = to_y - from_y
	for y_cor in range(from_y + (1 if y_diff > 0 else -1), to_y, 1 if y_diff > 0 else -1):
		if piece_arr[y_cor][x_cor] is not None: return False  # piece obstructing path
	return True
def check_horizontal_move_for_pieces(piece_arr, y_cor, from_x, to_x):  # noqa: E302 (two lines between base-level definitions) - these functions are triplets
	# see above for explanation
	x_diff = to_x - from_x
	for x_cor in range(from_x + (1 if x_diff > 0 else -1), to_x, 1 if x_diff > 0 else -1):
		if piece_arr[y_cor][x_cor] is not None: return False  # piece obstructing path
	return True
def check_diagonal_move_for_pieces(piece_arr, from_x, to_x, from_y, to_y):  # noqa: E302 (two lines between base-level definitions) - (see above)
	x_diff = to_x - from_x
	y_diff = to_y - from_y
	for (x_cor, y_cor) in zip(
		range(from_x + (1 if x_diff > 0 else -1), to_x, 1 if x_diff > 0 else -1),  # code from above
		range(from_y + (1 if y_diff > 0 else -1), to_y, 1 if y_diff > 0 else -1)  # also from above
	):  # move in that diagonal line
		if piece_arr[y_cor][x_cor] is not None: return False
	return True


def move_is_valid(turtle_arr, from_pos, to_pos):
	# assumes that the from and to coordinates are within the grid, and that from and to are not the same.
	from_x, from_y = from_pos
	to_x, to_y = to_pos
	color_arr, piece_arr = convert_to_piece_types(turtle_arr)
	moving_piece = piece_arr[from_y][from_x]  # indexed by y and then x
	is_light = color_arr[from_y][from_x] == 'light'  # ^
	if color_arr[from_y][from_x] == color_arr[to_y][to_x]: return False
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
		if x_diff == 0:  # non-capture
			if y_diff == (1 if is_light else -1):  # normal move
				return dest_empty  # only valid for non-capturing moves
			elif y_diff == (2 if is_light else -2) and from_y == (1 if is_light else 6):  # double jump at start
				return dest_empty and piece_arr[to_y - (1 if is_light else -1)][to_x] is None  # can't jump or capture
			return False  # fall through
		elif abs(x_diff) == 1 and not dest_empty:  # capture
			return True
		return False  # fall through
