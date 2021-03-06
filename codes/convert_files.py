from PIL import Image, ImageTk
import tkinter as tk
from .detect_text import detect_text
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

def forceTemp(path, tname):
    temp = {}
    with open('output/template.json', 'r') as fp: temp = json.load(fp)
    pic = Image.open(path)
    result = getRes(temp[tname], pic)
    result['template'] = 'Template'+str(tname)
    saveData(result, path)

def getRes(data, pic):
    result = {}
    # 3. crop pic using dimentions in template and save
    for key in data:
        if key == 'created': continue
        coord  = data[key]['coord']
        for i in range(len(coord)): coord[i] = int(coord[i]*pic.size[i%2]/100)

        temp = pic.crop((coord))
        temp.save('img/tmp.jpg',)

        # 4. send the cropped pic in detect_text
        text = detect_text('img/tmp.jpg')

        # 5. save the text in dict w key from template name
        result[key] = text.rpartition('\n')[2].lstrip()  
    return result  

def saveData(result, root_path):
    data = []
    result['file'] = root_path.rpartition('/')[2]
    if os.path.isfile('output/result.json'): 
        with open('output/result.json', 'r') as fp: data = json.load(fp)
    data.append(result)
    with open('output/result.json', 'w') as fp: json.dump(data, fp, sort_keys=True, indent=4)
    os.rename(root_path, 'processed/' + result['file'])

def read(path):
    result = {}
    if path.split('.')[1] == 'pdf':
        page = convert_from_path(path, 500)
        for p in page: p.save('img/out.jpg', 'JPEG')
        path = 'img/out.jpg'
    pic = Image.open(path)
    
    # 2. read output/template.json one by one
    with open('output/template.json', 'r') as fp:
        templates = json.load(fp)
        if not templates: raise ValueError('No template found.')

        # Iterate through all templates
        for key in templates:
            data = templates[key]
            result = getRes(data, pic)
            if isRightTemp(result): 
                result['template'] = 'Template'+str(key)
                break
            result = {}
            # wait before making the next iteration of requests
            for _ in range(1000): pass  
    if result: saveData(result, path)

    return "done"

if __name__ == '__main__':
    pros_files = ['unprocessed/'+fl for fl in os.listdir('unprocessed/')]
    for pf in pros_files: read(pf)
