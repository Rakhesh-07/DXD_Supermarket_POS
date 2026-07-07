import tkinter
from PIL import ImageTk,Image
setup_window=tkinter.Tk()

#background image for setup window
canvas = tkinter.Canvas(setup_window, width=200, height=200)
canvas.grid(columnspan=2)
#image = tkinter.Image.open("logo.png")
canvas.image = ImageTk.PhotoImage(Image.open("logo.png"))
canvas.image.pack()
canvas.create_image(0, 0, image=canvas.image, anchor="nw")
