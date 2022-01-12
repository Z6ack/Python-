# Python-
爬取A和C中间那个站的视频进行下载，支持两种查找，和音频视频合并
写在前面：
	此博客仅用于记录个人学习进度，学识浅薄，若有错误观点欢迎评论区指出。欢迎各位前来交流。（部分材料来源网络，若有侵权，立即删除）


@[TOC](Python实现爬取某站视频|根据视频编号|支持通过视频名称和创作者名称寻找编号|以及python moviepy合并音频视频)
#  免责声明

 - 代码仅用于学习，如被转载用于其他非法行为，自负法律责任
 - 代码全部都是原创，不允许转载，转载侵权

#  情况说明

 - python爬虫
 - 实现了对视频的爬取并进行音画合并
 - 支持通过视频名称和创作者名称寻找编号



 
#  代码讲解
##  cookie
[参考博客](https://blog.csdn.net/Q_U_A_R_T_E_R/article/details/120241011)

 - 这边使用的是Selenium模拟登录的方法
 - 函数如下：

```python
def get_cookies():
    driver = webdriver.Firefox()#启动浏览器
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
    with open('wyycookie.txt', 'w') as f:
        f.write(cookiestr)
    print('cookies保存成功！')
    driver.close()
```
 

 - 这一行代码是将driver中获取到的cookie转换成requests能直接使用的格式

```python
 cookie = [item["name"] + "=" + item["value"] for item in dictcookies]
 cookiestr = ';'.join(item for item in cookie)
```

 - 然后写入文件

```python
with open('wyycookie.txt', 'w') as f:
        f.write(cookiestr)
    print('cookies保存成功！')
    driver.close()
```

 - 读取cookie

```python
def read_cookie():
    try:

        print("[INFO]:正常尝试读取本地cookie")
        with open('wyycookie.txt', 'r', encoding='utf8') as f:
            Cookies = f.read()
            # print(Cookies)
    except:
        print("[ERROR]:读取失败，请手动登录并更新")
        get_cookies()
        read_cookie()
    return Cookies
```

 - 这边也有读取的机制和读取失败的机制

##  获取视频链接

 - 首先我们打开一个视频
 - F12后，在播放的过程中，查看发送过来的mp4类型的包，我使用的是火狐浏览器
 - 我们可以理解为视频是分片发过来的
 - 我们去查看网页源码

 - 发现一个问题就是音频和视频是分开的
 - 这个先不考虑
 - 但是可以确认是通过这两个URL进行数据请求的
 - 那先进行获取

```python
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
```


 - 这个函数也只是普普通通的爬虫函数然后解析页面重点json字典
 - 很容易得到对应的视频标题以及两个URL
##  获取音视频文件

 - 继续观察F12
![在这里插入图片描述](https://img-blog.csdnimg.cn/186ebbe18ec74af99d8e59a595c29b6a.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBA5qGD5Zyw552h5LiN552A,size_20,color_FFFFFF,t_70,g_se,x_16)
 - 可以看到发送mp4的状态码都是206
 - MP4的url请求来自于视频和音频两个url
 - 仔细对照可以发现和上面获得的两个URL相同
 - 单独看一个
 - 发送的目的url相同
 - 那看看请求头
![在这里插入图片描述](https://img-blog.csdnimg.cn/85bdf2b6101f48048b3d9644072edada.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBA5qGD5Zyw552h5LiN552A,size_20,color_FFFFFF,t_70,g_se,x_16)
![在这里插入图片描述](https://img-blog.csdnimg.cn/46b98a323c48413cadd5c52df418cbee.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBA5qGD5Zyw552h5LiN552A,size_15,color_FFFFFF,t_70,g_se,x_16)
 - 这个请求头中的Range参数会变化
 - 是请求对应媒体字节的段数
 - 所以我们在构造header的时候需要尽可能的详细
 - 每一次的range参数会变化
 - 所以我们需要更新headers
 - range一次的值设置为1024*1024
 - 逐次更替比如1-100、101-200，依次类推
 - 

```python
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

```

 - 通过这个函数可以得到一个无声的mp4文件和一个mp3音频文件
 - 接下来需要合并
##  音画合并
 - 视频作者是我自己，所以不存在侵权

![在这里插入图片描述](https://img-blog.csdnimg.cn/198e7b14db6f4c48bd97080fa88c87c1.png)

 - 这边采用的一个python库是 moviepy
 - MoviePy是一个用于视频编辑的Python模块，它可被用于一些基本操作（如剪切、拼接、插入标题）、视频合成（即非线性编辑）、视频处理和创建高级特效。它可对大多数常见视频格式进行读写，包括GIF。
 - [使用文档](http://doc.moviepy.com.cn/)
 - 没什么好说的，路径记得写对

```python
def conbine(title):
    print("[INFO]:正在合并音视频", flush=True)
    video_clip = VideoFileClip(r'F:\{}.mp4'.format(title))
    audio = AudioFileClip(r'F:\{}.mp3'.format(title)).volumex(0.5)
    final_video = video_clip.set_audio(audio)
    final_video.write_videofile("{}!.mp4".format(title))
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/7a25adf4a9e94c4481257e2c317a7e7c.png)
##  查询
###  根据视频名称

 - 由于最终的目的是查看视频编号
 - 所以减少了很多元素的爬取
 - 可以看到也是一个很简单的爬虫模块
 - 通过搜索返回结果进行爬取

```python
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
```
###  根据创作者

 - 和前一个的目的相同
 - 也是通过搜索得到创作者编号
 - 然后组合成url访问该作者的视频列表接口
 - 思路和以前爬取ajax一样
 
 - 再根据返回的视频列表，依次提取每一个视频的基本参数，提供给使用者选择

```python
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

```

##  主菜单

```python
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
            name = input("[INFO]:请输入创作者名称：")
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


def print_menu():

    print ("="*500)
    print ("[INFO]:1. 获取指定音乐歌词")
    print ("[INFO]:2. 生成指定音乐评论词云图")
    print ("[INFO]:3. 下载歌曲")
    print ("[INFO]:4. 退出系统")
    print("=" * 500)
```




#  使用的库函数

```python
from moviepy.editor import *
import requests
import time
import json
from selenium import webdriver
import re
from bs4 import BeautifulSoup
```


 - 慢用
 - 晚安
