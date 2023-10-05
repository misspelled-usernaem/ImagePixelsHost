from flask import *
import image

import requests
import os
from time import sleep as wait
import cv2 as cv
from datetime import datetime

scale=.1
tempDir='C:/Windows/Temp/'
temp=os.path.join(tempDir)
if not os.path.exists(f'{tempDir}rshare'):
    os.mkdir(f'{tempDir}rshare')
    folder=os.path.join(tempDir,'rshare')
else:
    folder=os.path.join(tempDir,'rshare')

folderDir=str(folder)+'/'

def main(img_url):
    img_content=requests.get(img_url).content
    img_name=str(datetime.now().replace(microsecond=0)).replace(":","-")+'.png'
    with open(f'./{img_name}','wb') as f:
        f.write(img_content)
    ssDir=os.path.join('./',img_name)
    image=cv.imread(ssDir)
    currentSize=image.shape
    newSize=[currentSize[1]>255 and 255 or currentSize[1],currentSize[0]>255 and 255 or currentSize[0]]
    print(newSize)
    image=cv.resize(image,newSize)
    currentSize=image.shape
    cv.imwrite(ssDir,image)
    fullList=[]
    for colum in range(currentSize[1]):
        crow=[]
        for row in range(currentSize[0]):
            BGR=image[row,colum]
            RGB={"R":BGR[2],"G":BGR[1],"B":BGR[0]}
            crow.append(RGB)
        fullList.append(str(crow))
    jsonList='[\n\t'+str.join(',\n\t',fullList)+'\n]'
    jsonList=jsonList.replace("'",'"')
    source='[\n\t'+str(fullList).replace('"','').replace("'",'"').replace('[{','\n\t\t[{').replace('}, {','},{').replace(', "',',"').replace('": ','":').replace(']]',']\n\t]')+'\n]'
    os.remove(ssDir)
    return source


app=Flask(__name__)

@app.route('/idata',methods=['POST'])
def idata():
    payload:dict=request.get_json()
    if payload.get('url'):
        try:
            img_url=payload['url']
            print(img_url)
            data=image.main(img_url)
            return data
        except:
            return 'invalid link'
    else:
        return 'missing key in payload'


app.run()