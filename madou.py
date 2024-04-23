from Crypto.Cipher import AES
import requests,re,os
from threading import Thread, Lock
import subprocess
from time import sleep
header = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Referer':'https://madou.club/',
    'Origin':'https://madou.club/',

}

def link(url):
    global key
    global path
    r = requests.get(url=url,headers=header).text
    videolink = re.findall('share/.*?\\s',r)
    u = videolink[0].split('/')[-1].rstrip()
    url = 'https://dash.madou.club//videos/'+u+'/index.m3u8'
    print(f'正在下载：{url}')
    r = requests.get(url=url,headers=header).text
    key = re.findall('http.*.+key', r)
    xx = re.findall('index.*.+ts',r)
    for x in xx:
        urls.append('https://dash.madou.club//videos/'+u+'/'+x)
        downloadlist.append(path+x)
def download(url):
    global num
    global key
    global path
    name = url.split('/')[-1]
    sleep(0.6)
    if (not (os.path.exists(path + name))):
        r = requests.get(url=url,headers=header).content
        bankLock.acquire()
        iv = b'0000000000000000' # iv偏移量，bytes类型
        aes = AES.new(key,AES.MODE_CBC,iv) #CBC模式下解密需要重新创建一个aes对象
        den = aes.decrypt(r)
        with open(path + name, 'wb') as f:
            f.write(den)
            if (os.path.getsize(path + name) > 1024):
                print(f"{name}解密成功")
                f.flush()
                f.close()
        num = num +1
        bankLock.release()

def merge(ts,video):
    comm = [ffmpeg, '-i', f'concat:{'|'.join(ts)}','-c','copy', video]
    subprocess.run(comm)
    print(f'{video} ok')

if __name__ == "__main__":
    bankLock = Lock()
    url = 'https://madou.club/ly054-%e5%a5%b3%e5%8f%8b%e5%a7%90%e5%a7%90%e5%af%b9%e6%88%91%e7%9a%84%e7%89%b9%e5%88%ab%e6%8b%9b%e5%be%85-%e5%88%9d%e6%ac%a1%e8%a7%81%e9%9d%a2%e8%82%89%e4%bd%93%e6%8b%9b%e5%be%85.html'
    urls = []
    num = 0
    path = ''
    downloadlist = []
    key = ''
    path = input('输入保存路径：')
    ffmpeg = input('输入ffmpeg路径：')
    link(url)
    key = requests.get(url=key[0],headers=header).text
    key = key.encode()
    threads = []
    for k in urls:
        if (k):
            t = Thread(target=download,
                       args=(k,)
                       )
            t.start()
            threads.append(t)

    for t in threads:
        t.join()
    if (num == len(urls) or len(os.listdir(path))==len(urls)):
        merge(downloadlist,path+'t.mp4')
        print('下载成功')
    else:
        print('下载不完整，请检测网络并重新下载')

