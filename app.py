from flask import *
import requests
import os
from time import sleep as wait
import cv2 as cv
from datetime import datetime

cached_urls={}

def main(img_url,size):
    if cached_urls.get(img_url):
        return cached_urls[img_url]
    else:
        img_content=requests.get(img_url).content
        img_name=str(datetime.now().replace(microsecond=0)).replace(":","-")+'.png'
        with open(f'./{img_name}','wb') as f:
            f.write(img_content)
        ssDir=os.path.join('./',img_name)
        image=cv.imread(ssDir,cv.IMREAD_UNCHANGED)
        image=cv.cvtColor(image,cv.COLOR_BGR2BGRA)
        currentSize=image.shape
        newSize=[currentSize[1]>255 and 255 or currentSize[1],currentSize[0]>255 and 255 or currentSize[0]]
        if size:
            newSize=size
        image=cv.resize(image,newSize)
        currentSize=image.shape
        cv.imwrite(ssDir,image)
        fullList=[]
        for colum in range(currentSize[0]):
            crow=[]
            for row in range(currentSize[1]):
                BGRA=image[row,colum]
                RGB={"R":BGRA[2],"G":BGRA[1],"B":BGRA[0],"A":BGRA[3]}
                crow.append(RGB)
            fullList.append(str(crow))
        jsonList='[\n\t'+str.join(',\n\t',fullList)+'\n]'
        jsonList=jsonList.replace("'",'"')
        source='[\n\t'+str(fullList).replace('"','').replace("'",'"').replace('[{','\n\t\t[{').replace('}, {','},{').replace(', "',',"').replace('": ','":').replace(']]',']\n\t]')+'\n]'
        os.remove(ssDir)
        cached_urls.setdefault(img_url,source)
        return source


app=Flask(__name__,)
@app.route('/')
def home():
    return 'Ok it work'
@app.route('/idata',methods=['POST'])
def idata():
    payload:dict=request.get_json()
    if payload.get('url'):
        try:
            img_url=payload['url']
            size=False
            if payload.get('x') and payload.get('y'):
                size=[int(payload['x']),int(payload['y'])]
            print(img_url)
            data=main(img_url,size=size)
            return data
        except:
            return 'invalid link'
    else:
        return 'missing key in payload'


@app.route('/bulk',methods=['POST'])
def bulk():
    payload:dict=request.get_json()
    if payload.get('urls'):
            returnValue={}
            for urlDesc in payload['urls']:
                try:
                    img_url=urlDesc.get('url')
                    size=False
                    if urlDesc.get('x') and urlDesc.get('y'):
                        size=[int(urlDesc['x']),int(urlDesc['y'])]
                    print(img_url)
                    data=main(img_url,size=size)
                    returnValue.setdefault(img_url,data)
                except:
                    pass
            return returnValue
    else:
        return 'missing key in payload'