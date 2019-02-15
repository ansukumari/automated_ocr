import tkinter as tk, os
from tkinter.messagebox import showinfo
from convert_files import read

root = tk.Tk()
# root.geometry("600x400")

def getText():
    import pandas as pd
    import json

    data = []
    with open('result.json', 'r') as fp:
        data = json.load(fp)

    keys = [key for key in data[0]] 
    val = []
    for d in data: val.append([d[k] for k in keys])
    return pd.DataFrame(val, columns=keys)

def createTemp(): 
    os.system('python create_temp.py')

def convertFiles(): 
    os.system('python convert_files.py')
    # read()
    # showinfo('Conversion Complete', 'All files processed. Click "Show Table" to see the fetched data!')

def showTbl():
    # showinfo('Table', 'Tables!')
    import pandas
    pandas.read_json("result.json").to_excel("output.xlsx")
    os.system("libreoffice output.xlsx")
    # text.delete("1.0", "end")
    # text.insert('end', getText())


tk.Button(root, text="Create Template", width=40, command=createTemp).pack()
tk.Button(root, text="Convert Files", width=40, command=convertFiles).pack()
tk.Button(root, text="Show Table", width=40, command=showTbl).pack()


root.title('Automated OCR')
root.mainloop()
