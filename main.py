import util
import turtle

win = turtle.Screen()
board_turtle = turtle.Turtle()
board_turtle.speed(10)

board_size = 600

util.draw_board(board_turtle, board_size)

board = util.create_full_board(win)
util.move_board_pieces(board, board_size, board_size / 8)

win.mainloop()
