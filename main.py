import util
import turtle

win = turtle.Screen()
board_turtle = turtle.Turtle()
board_turtle.speed(10)

board_size = 600

util.draw_board(board_turtle, board_size)

win.mainloop()
