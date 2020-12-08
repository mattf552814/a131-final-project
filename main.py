import util
import turtle

win = turtle.Screen()
board_turtle = turtle.Turtle()
board_turtle.speed(10)

is_blacks_turn = True  # false means it's white's turn

FONT_SIZE = 20
FONT = ('PT Sans', FONT_SIZE, 'normal')

turn_indicator = turtle.Turtle()
turn_indicator.hideturtle()
turn_indicator.up()
util.draw_turn_indicator(turn_indicator, is_blacks_turn, FONT, (0, 370))

board_size = 600

util.draw_board(board_turtle, board_size)

board = util.create_full_board(win)
util.move_board_pieces(board, board_size, board_size / 8)

win.mainloop()
