import util
import logic
import turtle

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
util.draw_turn_indicator(turn_indicator, is_blacks_turn, FONT, (0, 370))

board_size = 600

util.draw_board(board_turtle, board_size)

board = util.create_full_board(win)
taken_pieces = {color: {shape: 0 for shape in util.shapes} for color in util.colors}
util.move_board_pieces(board, board_size, board_size / 8)

indicators_writer = turtle.Turtle()
indicators_writer.hideturtle()
indicators_writer.up()
taken_indicators = util.create_taken_piece_indicator(win)

util.move_piece_indicators(board_size, taken_indicators)
util.update_piece_indicators(indicators_writer, ('PT Sans', 10, 'normal'), taken_pieces, taken_indicators)

win.register_shape('selection.gif')
selection_indicator = turtle.Turtle(shape='selection.gif')
selection_indicator.hideturtle()
selection_indicator.up()

win.mainloop()
