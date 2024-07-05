# -*- coding: utf-8 -*-
import requests
import os
import sys
import json
from lxml import etree
from time import sleep, time
from threading import Thread, Lock


def img_list(url):
    xx = requests.get(url=url, headers=headers).text
    xxx = etree.HTML(xx)
    xxx = xxx.xpath('//*[@id="content"]/div/img/@src')
    bankLock.acquire()
    for i in range(len(xxx)):
        images.append('https://www.117w.one/'+xxx[i])
    bankLock.release()


def download(url, name):
    img = requests.get(url=url, headers=headers).content
    bankLock.acquire()
    with open('./'+imgname+'/'+str(name)+'.jpg', 'wb') as f:
        f.write(img)
        f.close()
    bankLock.release()
    if (os.path.exists('./'+imgname+'/'+str(name)+'.jpg')) and (os.path.getsize('./'+imgname+'/'+str(name)+'.jpg') > 1024):
        print(f'{name}.jpg保存成功')
    else:
        print(f'{name}.jpg保存失败请检查网络或者更换代理')


if __name__ == "__main__":
    bankLock = Lock()
    start_time = time()
    # url = input('输入写真网址：')
    url = 'https://www.117w.one/mc49.aspx'
    # url = 'https://www.117w.one/mn107531c49.aspx'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 uacq'
    }
    headers['Referer'] = url
    imagelist = []
    lists = []
    images = []
    imgdic = {}
    imgl = url.split('/')[-1].split('.')[0]
    if os.path.exists('./'+imgl+'.txt'):
        print(f'正在继续下载: {imgl}...')
        with open('./'+imgl+'.txt', 'r', encoding='utf-8') as f:
            n = f.read()
            n = json.loads(n)
            f.close()
    else:
        print(f'正在下载: {imgl}')
        r = requests.get(url=url, headers=headers).text
        r = etree.HTML(r)
        r = r.xpath('/html/body/ul[3]/li/a')
        for xx in r:
            name = xx.xpath('./text()')[0]
            url = xx.xpath('./@href')[0]
            url = 'https://www.117w.one/'+url
            imgdic.update({name: url})
        with open('./'+imgl+'.txt', 'w', encoding='utf-8') as f:
            f.write(json.dumps(imgdic, ensure_ascii=False))
            f.close()
        with open('./'+imgl+'.txt', 'r', encoding='utf-8') as f:
            n = f.read()
            n = json.loads(n)
            f.close()
    num = 0
    maxnum = 2
    allimg = 0
    for name, url in n.items():
        if num < maxnum:
            imgname = name
            if os.path.exists(imgname):
                print(f'正在继续下载{imgname}')
            else:
                os.mkdir(imgname)
                print(f'正在下载{imgname}')

            if os.path.exists('./'+imgname+'.txt'):
                print(f'正在读取图片列表。。。')
            else:
                print(f'正在保存图片列表。。。')
                imagelist.append(url)
                u = requests.get(url=url, headers=headers).text
                u = etree.HTML(u)
                alist = u.xpath(
                    '//div[@class="pager"]//child::a/@href')
                for x in range(len(alist)-1):
                    imagelist.append('https://www.117w.one/'+alist[x])
                print('正在获取图片列表，请耐心等待。。。')
                for l in range(len(imagelist)):
                    tt = Thread(target=img_list,
                                args=(imagelist[l], )
                                )
                    tt.start()
                    lists.append(tt)
                for tt in lists:
                    sleep(0.1)
                    tt.join()
                if (images):
                    print(f'获取图片列表成功，正在下载。。。共{len(images)}张写真')
                    with open('./'+imgname+'.txt', 'w+') as f:
                        f.writelines(images)
                        f.close()
                        print(f'保存完成{imgname}.txt')
            num = num + 1
            with open('./'+imgname+'.txt', 'r') as f:
                n = f.readlines()
                n = n[0].split('https://')
            allimg = allimg + (len(n) - 1)
            threads = []
            name = 0
            for k in range(len(n)):
                if (k):
                    url = 'https://'+n[k]
                    t = Thread(target=download,
                               args=(url, name)
                               )
                    t.start()
                    threads.append(t)
                    name = name+1

            for t in threads:
                t.join()
            images = []
            imagelist = []
    stop_time = time()
    print('下载完成，time:%d秒' % int(stop_time-start_time))
    print(f'共{allimg}张图片')