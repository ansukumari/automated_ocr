from PIL import Image, ImageTk
import tkinter as tk
from detect_text import detect_text
from pdf2image import convert_from_path
from tkinter.messagebox import showinfo
import os, sys, json, re
from tkinter.filedialog import askopenfilename as af

def isRightTemp(dic):
    patt = {
        'date': [
            r'^[0-9]{1,2}[\s\/-][0-9]{2,4}[\s\/-][0-9]{1,2}$',
            r'^[0-9]{1,2}[\s\/-][0-9]{1,2}[\s\/-][0-9]{2,4}$',
            r'^[0-9]{1,2}[\s\/-][0-9]{1,2}[\s\/-][0-9]{2,4}$',
            r'^[0-9]{0,2}[\s\/-][a-zA-Z]{2,}[\s\/-][0-9]{2,4}$'
        ],
        'float': r'^[0-9]{1,}([,\.][0-9]{2,3})*[\.,][\d]+$',
        'alnum': r'^[a-zA-z\d]*$',
        'model_code': r'^[\d\s\w\.-]+$',
        'num': r'^[\d]*$'
    }

    date = False

    for key in dic:
        if key == 'date':
            for d in patt['date']: date = True if re.compile(d).match(dic[key]) else False
            if not date: return False
        if key == 'model name': 
            if not re.compile(patt['model_code']).match(dic[key]): return False
        elif key == 'total': 
            if not re.compile(patt['float']).match(dic[key]): return False

    return True

def getRes(data, pic):
    result = {}
    # 3. crop pic using dimentions in template and save
    for key in data:
        coord  = data[key]['coord']
        for i in range(len(coord)): coord[i] = int(coord[i]*pic.size[i%2]/100)

        temp = pic.crop((coord))
        temp.save('tmp.jpg',)

        # 4. send the cropped pic in detect_text
        text = detect_text('tmp.jpg')

        # 5. save the text in dict w key from template name
        result[key] = text.rpartition('\n')[2].lstrip()  
    return result  

def saveData(result, img):
    data = []
    result['file'] = img
    if os.path.isfile('result.json'): 
        with open('result.json', 'r') as fp: data = json.load(fp)
    data.append(result)
    with open('result.json', 'w') as fp: json.dump(data, fp, sort_keys=True, indent=4)
    os.rename('input_img/' + img, 'processed_img/' + img)
    print('done')

def read():
    f = []
    for (dirpath, dirnames, filenames) in os.walk('input_img'):
        print(dirnames, dirpath, filenames)
        f.extend(filenames)
        break

    # 1. input image path and open
    for img in f:
        result = {}
        path = 'input_img/' + img
        ext = img.split('.')[1]
        if ext == 'pdf':
            page = convert_from_path(path, 500)
            for p in page: p.save('out.jpg', 'JPEG')
            path = 'out.jpg'
        print(path)
        pic = Image.open(path)
        
        # 2. read template.json one by one
        with open('template.json', 'r') as fp:
            templates = json.load(fp)

            # Iterate through all templates
            for data in templates:
                result = getRes(data, pic)
                print(json.dumps(result, indent=2))
                if isRightTemp(result): 
                    print(path, 'matched template', templates.index(data))
                    break
                result = {}
                for _ in range(1000): pass        
        result = {}
        if result: saveData(result, img)

        else:
            # Popup - New template required for the image
            print(img, 'neither')
            root = tk.Tk()
            root.geometry('500x700')

            # top = tk.Canvas(root).place(relx=0, rely=0, relheight=0.9)
            # bot = tk.Canvas(root).place(relx=0, rely=0.9, relheight=0.1)

            h, w = 600, 500
            if pic.size[1] > h: pic = pic.resize((int(h*pic.size[0]/pic.size[1]), h), Image.ANTIALIAS)
            if pic.size[0] > w: pic = pic.resize((w, int(w*pic.size[1]/pic.size[0])), Image.ANTIALIAS)
            tkimage = ImageTk.PhotoImage(pic)
            img_holder = tk.Label(root, image=tkimage)
            img_holder.image = tkimage
            img_holder.pack(side='top')
            # img_holder.place(relx=0.5, rely=0, anchor='n')

            def onSkip(): root.destroy()
            
            def forceTemp():
                path = af(filetypes=[("Image File",'.jpg')], initialdir='templates')
                ind = int(path.rpartition('/')[2].split('.')[0])
                root.destroy()
                temp = []
                with open('template.json', 'r') as fp: temp = json.load(fp)
                result = getRes(temp[ind], pic)
                saveData(result, img)

            # Buttons - Skip | Force existing template
            tk.Button(root, text='Skip for now', command=onSkip).place(relx=0.05, rely=0.9)
            tk.Button(root, text='Force Existing Template', command=forceTemp).place(relx=0.6, rely=0.9)
            root.title("Convert File")
            root.resizable(0,0)
            root.mainloop()

if __name__ == '__main__':
    read()
