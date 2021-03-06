from tkinter import ttk
import tkinter as tk, os, json, sys
from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import messagebox as mb
from codes.convert_files import read, forceTemp

def getText():
    import pandas as pd
    import json

    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    data = []
    with open('output/result.json', 'r') as fp:
        data = json.load(fp)

    keys = [key for key in data[0]] 
    val = []
    for d in data: val.append([d[k] for k in keys])
    return pd.DataFrame(val, columns=keys)

def openPic(pic_path):
    pic = Image.open(pic_path)
    h, w = 600, 500
    if pic.size[1] > h: pic = pic.resize((int(h*pic.size[0]/pic.size[1]), h), Image.ANTIALIAS)
    if pic.size[0] > w: pic = pic.resize((w, int(w*pic.size[1]/pic.size[0])), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(pic)

    picpop = tk.Toplevel()
    picpop.geometry('500x600')
    picpop.title('Image Preview')
    tk.Label(picpop, image=photo, bg='white').pack()
    picpop.mainloop()

tname = ''
def showTemps():
    top = tk.Toplevel()
    top.title('Template Preview Window')
    top.geometry('500x200')
    top.resizable(0,0)

    frame = tk.Frame(top)
    frame.place(rely=0.05, relwidth=0.7)

    yscroll = tk.Scrollbar(frame, orient=tk.VERTICAL)
    lb = tk.Listbox(frame, yscrollcommand=yscroll.set)

    yscroll.config(command=lb.yview)
    yscroll.pack(side='right', fill='y')

    tk.Label(frame, text='{:15} {:20}'.format('Name', 'Created Date')).pack(side='top')
    lb.pack(side='left', fill='both', expand=1)

    data = {}
    try:
        with open('output/template.json', 'r') as fp: data = json.load(fp)
        for k in data: lb.insert('end', '{:>20}     |      {:20}'.format('Template '+k, data[k]['created'].split(' ')[0]))
    except: pass

    def selt(event): 
        global tname
        tname = lb.get(lb.curselection()).split('|')[0].rstrip().lstrip()[9:]
        top.destroy()
    lb.bind('<Double-Button>', selt)

    def show(): 
        try:
            fname = lb.get(lb.curselection()).split('|')[0].rstrip().lstrip()[9:]
            openPic('templates/'+fname)
        except: mb.showinfo('Alert', 'Please select row first!')
    tk.Button(top, text='Show', command=show).place(relx=0.75, rely=0.15, relwidth=0.2)

    def delete():
        try:
            sel = lb.curselection()
            fname = lb.get(sel).split('|')[0].rstrip().lstrip()[9:]
            sure = mb.askquestion('Alert', 'Would you like to delete Template'+fname+'?')
            if sure != 'yes': return
            os.unlink('templates/'+fname)
            data = {}
            with open('output/template.json', 'r') as fp: data = json.load(fp)
            del data[fname]
            with open('output/template.json', 'w') as fp: json.dump(data, fp)
            lb.delete(sel)
        except: mb.showinfo('Alert', 'Please select row first!')        
    tk.Button(top, text='Delete', command=delete).place(relx=0.75, rely=0.3, relwidth=0.2)

    top.mainloop()

def browse(wid):
    filename = filedialog.askdirectory()
    if filename: wid.configure(text=filename)

'''Top Level/Root'''
root = tk.Tk()
root.title("Optical Character Recognition")
root.geometry('900x550')

'''LG Logo Banner'''
photo = ImageTk.PhotoImage(Image.open('img/banner.jpg'))
tk.Label(root, image=photo, bg='white').place(relx=0, rely=0, relwidth=1, relheight=0.15)

''' Tab Styling (Padding) '''
btn_width = 15
col1, col2, col3 = 0.1, 0.31, 0.7
# row1, row2, row3, row4 = 0.1, 0.25, 0.4, 0.55
row1, row2, row3, row4 = 0.15, 0.35, 0.55, 0.75
mygreen = "#d2ffd2"
style = ttk.Style()
style.theme_create( "MyStyle", parent="alt", settings={
    "TNotebook": {"configure": {"background": 'white'} },
    "TNotebook.Tab": {
        "configure": {"padding": [20, 10], "background": 'white' },
        "map":       {"background": [("selected", root.cget('bg'))], }
    },
})
style.theme_use("MyStyle")

''' Notebook Creation '''
nb = ttk.Notebook(root)
nb.place(rely=0.15, relwidth=1, relheight=0.85)

''' Notebook Pages '''
p1 = ttk.Frame(nb)
p2 = ttk.Frame(nb)

nb.add(p1, text='Process Image')
nb.add(p2, text='Manage / New Template')


''' Page# 1 | Process Images'''

tk.Label(p1, text='Select input image folder').place(relx=col1, rely=row1)
pathp1 = tk.Label(p1, text=os.getcwd() + '/unprocessed')
tk.Button(p1, text='Browse', width=btn_width, command=lambda: browse(pathp1)).place(relx=col3, rely=row1)
pathp1.place(relx=col2, rely=row1)

lf = tk.LabelFrame(p1)
lf.place(relx=col2, rely=row2)
pros = tk.Label(lf, text='Processing: 0/0', width=btn_width+5)
pros.pack()

total = 0
def execute():
    global total
    pros_files = [os.path.join(pathp1.cget('text'), fl) for fl in os.listdir(pathp1.cget('text'))]
    i, total = 0, len(pros_files)
    for pf in pros_files: 
        try: 
            read(pf); i += 1
            pros.config(text='Processing: {}/{}'.format(i, total))
        except Exception as e: 
            info = 'Please create a template first.'
            if type(e).__name__ == 'DefaultCredentialsError': 
                info = 'Please set GOOGLE APPLICATION CREDENTIALS.'
            mb.showinfo('Alert', info)
            break
        
    left = len(os.listdir(pathp1.cget('text')))
    pl.config(text='Processed: '+str(total-left))
    cpl.config(text='Cannot be processed: '+str(left))
    refersh()
    
tk.Button(p1, text='Execute', width=btn_width, command=execute).place(relx=col1, rely=row2)

tk.Button(p1, text='Summary', width=btn_width).place(relx=col1, rely=row3)
fr = tk.Frame(p1)
fr.place(relx=col2, rely=row3)
lb1 = tk.LabelFrame(fr, relief=tk.GROOVE)
lb1.pack(side='left')
tk.Label(fr, width=5).pack(side='left')

pl = tk.Label(lb1, text='Processed: ', width=btn_width+5)
pl.pack()
lb2 = tk.LabelFrame(fr, relief=tk.GROOVE)
lb2.pack()
cpl = tk.Label(lb2, text='Cannot be processed: ', width=btn_width+5)
cpl.pack()

def showOutput(): 
    # nb.select(p3)
    import pandas
    pandas.read_json("output/result.json").to_excel("output/output.xlsx", index=False)
    if sys.platform == 'linux': os.system("libreoffice output/output.xlsx")
    else: os.system("start EXCEL.EXE output/output.xlsx")
tk.Button(p1, text='Show Output', width=btn_width, command=showOutput).place(relx=col1, rely=row4)


''' Page# 2 | Manage / New Template '''

tk.Label(p2, text='Review Existing Templates').place(relx=col1, rely=row1)
tk.Button(p2, text='Show', width=btn_width, command=showTemps).place(relx=col2, rely=row1)

tk.Label(p2, text='Define New Template').place(relx=col1, rely=row2)
pathp2 = tk.Label(p2, text=os.getcwd() + '/unprocessed')
def browseUnp():
    browse(pathp2)
    refersh()
tk.Button(p2, text='Browse', width=btn_width, command=browseUnp).place(relx=col3, rely=row2)
pathp2.place(relx=col2, rely=row2)

fr1 = tk.Frame(p2)
fr1.place(relx=col1, rely=row3, relheight=0.3, relwidth=0.5)
yscroll = tk.Scrollbar(fr1, orient=tk.VERTICAL)
lst = tk.Listbox(fr1, yscrollcommand=yscroll.set)
yscroll.config(command=lst.yview)
yscroll.pack(side='right', fill='y')
tk.Label(fr1, text='Unprocessed Files').pack(side='top')
lst.pack(side='left', fill='both', expand=1)
def showPic(event): openPic(pathp2.cget('text')+'/'+event.widget.get(event.widget.curselection()))
lst.bind('<Double-Button>', showPic)

def refersh():
    lst.delete(0, 'end')
    for f in os.listdir(pathp2.cget('text')): lst.insert('end', f)
def createTemp(): os.system('python codes/create_temp.py')
tk.Button(p2, text='Create', width=btn_width, command=createTemp).place(relx=col3, rely=row3+0.1)
def assign():
    try: imname = lst.get(lst.curselection())
    except: 
        mb.showinfo('Alert', 'Please select a file from the left panel to assign a template to it.')
        return
    path = os.path.join(pathp2.cget('text'), imname)
    showTemps()
    try: forceTemp(path, tname)
    except: return
tk.Button(p2, text='Assign', width=btn_width, command=assign).place(relx=col3, rely=row3+0.2)
refersh()

root.mainloop()
