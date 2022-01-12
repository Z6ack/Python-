from moviepy.editor import *
import requests
import time
import json
from selenium import webdriver
import re
from bs4 import BeautifulSoup


def read_cookie():
    try:

        print("[INFO]:正常尝试读取本地cookie")
        with open('bilibilicookie.txt', 'r', encoding='utf8') as f:
            Cookies = f.read()
            # print(Cookies)
    except:
        print("[ERROR]:读取失败，请手动登录并更新")
        get_cookies()
        read_cookie()
    return Cookies

def get_cookies():
    driver = webdriver.Firefox()
    url = 'https://www.bilibili.com/'
    driver.get(url)  # 发送请求
    # 打开之后，手动登录一次
    time.sleep(3)
    input('完成登陆后点击enter:')
    time.sleep(3)
    dictcookies = driver.get_cookies()  # 获取cookies
    cookie = [item["name"] + "=" + item["value"] for item in dictcookies]
    cookiestr = ';'.join(item for item in cookie)
    print(cookiestr)
    with open('bilibilicookie.txt', 'w') as f:
        f.write(cookiestr)
    print('cookies保存成功！')
    driver.close()

def get_baseurl(bvid):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'Cookie': '{}'.format(Cookies)}
    rs = requests.session()
    r = rs.get('https://www.bilibili.com/video/{}'.format(bvid), headers=headers)
    html=r.text
    str = r'<h1 title="(.*?)" class="'
    title = re.findall(str, html)[0]
    str= r'\<script\>window\.__playinfo__=(.*?)\</script\>'
    result = re.findall(str, html)[0]
    temp = json.loads(result)
    videourl = temp['data']['dash']['video'][0]['baseUrl']
    audiourl = temp['data']['dash']['audio'][0]['baseUrl']
    print("[INFO]:视频链接获取成功")
    # print(videourl)
    # print(audiourl)
    return [title,videourl,audiourl]

def get_file(title,url,m,baseurl):
    print("[INFO]:开始下载")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
        'Cookie': '{}'.format(Cookies),
        'Host': 'cn-sccd3-cmcc-v-14.bilivideo.com',
        'Origin': 'https://www.bilibili.com',
        'Referer': baseurl
    }
    if (m == 0):
        form = 'mp4'
        print("[INFO]:现在下载视频")
    else:
        form = 'mp3'
        print("[INFO]:现在下载音频")
    start=0
    over=1024*1024-1
    k=0
    rs=requests.Session()
    M=0
    while True:

        time.sleep(0.2)
        headers.update({'Range': 'bytes=' + str(start) + '-' + str(over)})
        # print(headers['Range'])
        r = rs.get(url, headers=headers)
        print("[INFO]:网页返回状态码如下:",r.status_code,flush=True)
        if r.status_code==403 or r.status_code== 503:
            print("[ERROR]:请及时更换代理")
        if r.status_code == 206:
            start = over + 1
            over = over + 1024 * 1024
            M=M+1
            print("[INFO]:正在下载请稍后",flush=True)
        else:
            headers.update({'Range': str(over + 1) + '-'})
            # print(headers['Range'])
            r = rs.get(url, headers=headers)
            print("[INFO]:下载完成")
            k = 1
        with open(title + '.' + form, 'wb') as f:
            f.write(r.content)
            f.flush()
            if k==1:
                f.close()
                break

def conbine(title):
    print("[INFO]:正在合并音视频", flush=True)
    video_clip = VideoFileClip(r'F:\爬虫练习案例\{}.mp4'.format(title))
    audio = AudioFileClip(r'F:\爬虫练习案例\{}.mp3'.format(title)).volumex(0.5)
    final_video = video_clip.set_audio(audio)
    final_video.write_videofile("{}!.mp4".format(title))

def get_up(name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'Cookie': '{}'.format(Cookies)}
    rs = requests.session()
    r = rs.get('https://search.bilibili.com/upuser?keyword={}'.format(name), headers=headers)
    html = r.text
    soup = BeautifulSoup(r.content, 'lxml')
    first = soup.find('li', {'class': 'user-item'})
    second= first.find('div',{'class':'up-videos clearfix'})
    link=second.find('a',{'class':'video-more'})['href']
    str = r'.com/(.*?)/video'
    link = re.findall(str, link)[0]
    return link

def get_vediourl(num):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'Cookie': '{}'.format(Cookies)}
    rs = requests.session()
    r = rs.get('https://api.bilibili.com/x/space/arc/search?mid={}'.format(num), headers=headers)
    html = r.text
    dict_r = json.loads(html)
    for i in dict_r['data']['list']['vlist']:
        print("="*200)
        print('视频标题：'+i['title'])
        print('视频描述：'+i['description'])
        print('视频长度:'+i['length'])
        print('视频bv号：'+i['bvid'])
        print("=" * 200)

def search_video(name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'Cookie': '{}'.format(Cookies)}
    rs = requests.session()
    r = rs.get('https://search.bilibili.com/video?keyword={}'.format(name), headers=headers)

    soup = BeautifulSoup(r.content, 'lxml')
    all = soup.find_all('li', {'class': 'video-item matrix'})
    for every in all:
        data=[]
        title=every.find('a')['title']
        href = every.find('a')['href']
        watchnum = every.find('span',{'class':'so-icon watch-num'}).text
        watchnum = re.sub('[\n <br> &nbsp; / \\\\]', '', watchnum)
        uploadtime = every.find('span', {'class': 'so-icon time'}).text
        uploadtime = re.sub('[\n <br> &nbsp; / \\\\]', '', uploadtime)
        creator = every.find('a', {'class': 'up-name'}).text
        str = r'/video/(.*?)from=search'
        bvid = re.findall(str, href)[0]
        bvid = re.sub('[?]', '', bvid)
        print("=" * 200)
        print('视频标题：'+title)
        print('视频观看数：' + watchnum)
        print('上传时间：' + uploadtime)
        print('视频作者：' + creator)
        print('视频bv号：' +bvid)
        print("=" * 200)

def print_menu():

    print ("="*200)
    print ("[INFO]:1. 已知视频bv号，输入bv号进行下载")
    print ("[INFO]:2. 搜索视频名称查看视频bv号")
    print ("[INFO]:3. 搜索up主名称查看视频bv号")
    print ("[INFO]:4. 退出系统")
    print("=" * 200)

def main():
    #print_menu()
    while True:
        print_menu()
        # 获取用户输入
        try:
            num = int(input("[INFO]:请输入需要的操作："))
        except ValueError:
            # except Exception:
            print("输入错误，请重新输入（1.2.3）")
            continue
        except IndexError:
            print("请输入一个有效值：（1.2.3）")
            continue
        # 根据用户的数据执行相应的功能
        if num == 1:
           bv=input("[INFO]:请输入bv号：")
           data=get_baseurl(bv)
           print(data[0])
           get_file(data[0],data[1],0,'https://www.bilibili.com/video/{}'.format(bv))
           get_file(data[0],data[2],1,'https://www.bilibili.com/video/{}'.format(bv))
           conbine(data[0])
           print("=" * 500)
        elif num == 2:
            name = input("[INFO]:请输入视频名称：")
            search_video(name)
            print("=" * 500)
        elif num == 3:
            name = input("[INFO]:请输入up主名称：")
            num=get_up(name)
            get_vediourl(num)
            print("=" * 500)
        elif num == 4:
            print("[END]:感谢您的使用，欢迎下次再见")
            print("=" * 500)
            break
        else:
            print("[ERROR]:输入错误")
            print("=" * 500)

if __name__ == "__main__":
    print("=" * 500)
    print("[INFO]:欢迎使用zack的视频查询及下载系统")
    Cookies=read_cookie()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'Cookie': '{}'.format(Cookies)}
    main()
