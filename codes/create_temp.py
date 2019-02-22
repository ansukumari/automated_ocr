import tkinter as tk
from PIL import ImageTk, Image
from functools import partial
import json, os, shutil, datetime
from os import walk
from tkinter.messagebox import showinfo
from pdf2image import convert_from_path
from tkinter.filedialog import askopenfilename as af

top = tk.Tk()
path = af(filetypes=[("Image File",'.jpg'), ("Image File",'.pdf'), ("Image File",'.jpeg'), ("Image File",'.png')])
if not path: 
    top.destroy()
    exit()
ext = path.split('.')[1]
if ext == 'pdf': 
    page = convert_from_path(path, 500)
    for p in page: p.save('img/out.jpg', 'JPEG')
    path = 'img/out.jpg'
pic = Image.open(path)
x0 = y0 = 0

if pic.size[1] > 700: pic = pic.resize((int(700*pic.size[0]/pic.size[1]), 700), Image.ANTIALIAS)
img = ImageTk.PhotoImage(pic)
frame = tk.Canvas(top, width=pic.size[0]*2, height=pic.size[1], cursor="cross")
frame.create_image(0, 0, image=img, anchor='nw')
rec = frame.create_rectangle(0, 0, 0, 0)
temp  = pic.crop((0, 0, 0, 0))
cpic = ImageTk.PhotoImage(temp)
crec = frame.create_image(0, 0, image=cpic)

col_list = []
with open('output/cols.json', 'r') as fp: col_list = json.load(fp)
col_ft = {}

menu = tk.Menu(top, tearoff=0)
def define_col(col):
    c = []
    for i in range(len(frame.bbox(rec))): c.append(int(100*frame.bbox(rec)[i]/pic.size[i%2]))
    col_ft[col] = {'coord': (c[0], c[1], c[2], c[3])}

def add_col():
    root = tk.Toplevel(top)
    e=tk.Entry(root)
    e.pack()
    def cleanup():
        col=e.get()
        root.destroy()
        col_list.append(col)
        define_col(col)
        menu.add_command(label=col, command=partial(define_col, col))
        with open('output/cols.json', 'w') as fp: json.dump(col_list, fp)

    b=tk.Button(root,text='Add Column',command=cleanup)
    b.pack()

for col in col_list: menu.add_command(label=col, command=partial(define_col, col))
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
    if 'model name' not in col_ft: 
        showinfo('Alert', 'Please add the column "model name".')
        return
    if 'date' not in col_ft: 
        showinfo('Alert', 'Please add the column "date".')
        return
    if 'total' not in col_ft: 
        showinfo('Alert', 'Please add the column "total".')
        return
        
    data = {}
    col_ft['created'] = str(datetime.datetime.now())
    if os.path.isfile('output/template.json'): 
        with open('output/template.json', 'r') as fp: data = json.load(fp)
    
    f = []
    for filenames in walk('templates'):
        f.extend(map(int, filenames[2]))
        break

    fname = str(max(f)+1) if f else '1'
    data[fname] = col_ft
        
    with open('output/template.json', 'w') as fp: json.dump(data, fp)
    shutil.copyfile(path, 'templates/'+fname)
    showinfo('Alert', 'Template Saved!')
    top.destroy()

but = tk.Button(frame, text='Save Template', command=onSaveClick)
frame.create_window(pic.size[0]+5, pic.size[1]//2, anchor='nw', window=but)

top.title("Create Template")
top.mainloop()
