import tkinter
from PIL import ImageTk, Image
from functools import partial
import json, os
from tkinter.messagebox import showinfo
from pdf2image import convert_from_path
from tkinter.filedialog import askopenfilename as af

top = tkinter.Tk()
path = af(filetypes=[("Image File",'.jpg'), ("Image File",'.pdf'), ("Image File",'.jpeg'), ("Image File",'.png')])
print(type(path), path)
ext = path.split('.')[1]
if ext == 'pdf': 
    page = convert_from_path(path, 500)
    for p in page: p.save('out.jpg', 'JPEG')
    path = 'out.jpg'
pic = Image.open(path)
x0 = y0 = 0

if pic.size[1] > 700: pic = pic.resize((int(700*pic.size[0]/pic.size[1]), 700), Image.ANTIALIAS)
img = ImageTk.PhotoImage(pic)
frame = tkinter.Canvas(top, width=pic.size[0]*2, height=pic.size[1], cursor="cross")
frame.create_image(0, 0, image=img, anchor='nw')
rec = frame.create_rectangle(0, 0, 0, 0)
temp  = pic.crop((0, 0, 0, 0))
cpic = ImageTk.PhotoImage(temp)
crec = frame.create_image(0, 0, image=cpic)

col_list = ['seller address', 'buyer address', 'date', 'invoice no', 'supplier ref', 'model name', 'price', 'quantity', 'amount', 'tax %', 'tax amount', 'total']
col_ft = {}

def add_col(): pass

menu = tkinter.Menu(top, tearoff=0)
def define_col(col):
    print(col, frame.bbox(rec))
    c = []

    for i in range(len(frame.bbox(rec))): c.append(int(100*frame.bbox(rec)[i]/pic.size[i%2]))
    col_ft[col] = {'coord': (c[0], c[1], c[2], c[3])}

    print(col_ft)

for col in col_list: menu.add_command(label=col, command=partial(define_col, col))#lambda: define_col(col))
menu.add_separator()
menu.add_command(label='+ Add Column', command=add_col)

def onRightClick(event): menu.tk_popup(event.x, event.y)
    
def leftDrag(event):
    global x0, y0, rec, cpic, crec, temp
    x1, y1 = event.x, event.y
    event.widget.delete(crec)
    event.widget.delete(rec)
    temp = pic.crop((x0, y0, x1, y1))
    cpic = ImageTk.PhotoImage(temp)
    rec = event.widget.create_rectangle(x0,y0,x1,y1)
    crec = event.widget.create_image(pic.size[0]+10, 10, image=cpic, anchor='nw')

def onPress(event):
    global x0, y0, rec, crec
    event.widget.delete(crec)
    event.widget.delete(rec)
    x0, y0 = event.x, event.y

frame.bind("<ButtonPress-1>", onPress)
frame.bind("<B1-Motion>", leftDrag)
frame.bind("<Button-3>", onRightClick)
frame.pack(side="top", fill="both", expand=True)

def onSaveClick():
    data = []
    if os.path.isfile('template.json'): 
        with open('template.json', 'r') as fp: data = json.load(fp)
    data.append(col_ft)
    with open('template.json', 'w') as fp: json.dump(data, fp)
    try: 
        pic.save('templates/' + str(len(data)-1) + '.jpg')
        showinfo('Alert', 'Template Saved!')
    except: showinfo('Alert', 'Open a file first!')

but = tkinter.Button(frame, text='Save Template', anchor='w', command=onSaveClick)
frame.create_window(pic.size[0]+5, pic.size[1]//2, anchor='nw', window=but)

top.title("Image Selector")
top.mainloop()
