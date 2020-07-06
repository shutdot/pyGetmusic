#!/usr/local/bin/python3
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import logging
from logging import handlers
import subprocess
import youtube_dl
import os
from os import rename
def clear():os.system('clear')
clear()

class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }#日志级别关系映射

    def __init__(self,filename,level='info',when='D',backCount=3,fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        fmt = '%(asctime)s:%(message)s'
        format_str = logging.Formatter(fmt)#设置日志格式
        self.logger.setLevel(self.level_relations.get(level))#设置日志级别
        sh = logging.StreamHandler()#往屏幕上输出
        sh.setFormatter(format_str) #设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=backCount,encoding='utf-8')#往文件里写入#指定间隔时间自动生成文件的处理器
        #实例化TimedRotatingFileHandler
        #interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(format_str)#设置文件里写入的格式
        self.logger.addHandler(sh) #把对象加到logger里
        self.logger.addHandler(th)
"""log用例 
    log = Logger('info.log',level='info')
    log.debug('调试')
    log.info('信息')
    log.warning('警告')
    log.error('报错')
    log.critical('严重')
    Logger('error.log', level='error').logger.error('error')
"""  

#youtube-dl -F --skip-download 'https://www.youtube.com/watch?v=r7UDi_JKsMg'
class downloadObj(object):
    strFileName = ''
    def rename_hook(self,d):
        # 重命名下载的视频名称的钩子
        if d['status'] == 'finished':
            file_name = '{}.m4a'.format(self.strFileName)
            rename(d['filename'], file_name)
            log.info('下载完成:%s'%(file_name))
        elif d['status'] == 'downloading':
            #info = 'downloaded_bytes: ' + str(d['downloaded_bytes']) + ', elapsed: ' + str(d['elapsed']) + ', speed: ' + str(d['speed']) + ', filename: ' + self.strFileName
            info = self.strFileName + '耗时: ' + str(float('%.2f' % d['elapsed']))
            print(info)
        else:
            log.info('下载%s,出错！'%self.strFileName)

    def download(self,filename,youtube_url):
        # 定义某些下载参数
        """
        best：选择具有视频和音频的单个文件所代表的最佳质量格式。
        worst：选择具有视频和音频的单个文件所代表的最差质量格式。
        bestvideo：选择最佳质量的仅视频格式（例如DASH视频）。可能无法使用。
        worstvideo：选择质量最差的纯视频格式。可能无法使用。
        bestaudio：选择质量最佳的音频格式。可能无法使用。
        worstaudio：选择质量最差的音频格式。可能无法使用。
        """
        self.strFileName = filename
        print('下载%s'%(self.strFileName))
        ydl_opts = {
            # 我指定了要下载 “1” 这个格式，也可以填写 best/worst/worstaudio 等等
            'format' : 'bestaudio',
            'progress_hooks' : [self.rename_hook],
            # 格式化下载后的文件名，避免默认文件名太长无法保存
            'outtmpl': '%(id)s%(ext)s',
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # 下载给定的URL列表
            result = ydl.download([youtube_url])

if __name__ == '__main__':
    log = Logger('info.log',level='info').logger
    #strfilename = input("输入歌单地址：")
    strfilename = '/Users/jacklee/PythonProjects/pyGetmusic/list.txt'
    #print ("歌单地址: ", strfilename)
    #逐行读取歌曲下载列表

    dictAll = {}
    f = open(strfilename, "r")
    for line in f:
        #跳过#开头对行
        if(line[0]== '#'):
            continue
        line = line.rstrip('\n')
        if len(line) > 0:
            #以空格分割字符串存储在数据容器中
            listNameAndArtist = line.split(' ')
            dictAll[listNameAndArtist[0]] = listNameAndArtist
    f.close()

    #遍历数据容器，以歌曲名请求youtube搜索页面
    #https://www.youtube.com/results?search_query=%E9%86%89%E9%B2%9C%E7%BE%8E
    urlBase = 'https://www.youtube.com/results?search_query='
    headers = {
        'Content-Type': 'text/html;charset=utf-8',
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    chrome_opt = Options()      # 创建参数设置对象.
    chrome_opt.add_argument('--headless')   # 无界面化.
    chrome_opt.add_argument('--disable-gpu')    # 配合上面的无界面化.
    chrome_opt.add_argument('--window-size=1920,1080')   # 设置窗口大小, 窗口大小会有影响.
    prefs = {
        'profile.default_content_setting_values' : {
            'images' : 2
        }
    }
    chrome_opt.add_experimental_option('prefs',prefs)

    driver = webdriver.Chrome(chrome_options=chrome_opt)

    #解析请求结果，匹配歌曲名和歌手在结果中对位置，获得下载地址存储数据容器
    for(k,v)in dictAll.items(): 
        url = urlBase + k
        driver.get(url)
        WebDriverWait(driver,30,0.5).until(lambda x:x.find_elements_by_id('contents'))
        
        #xpath = "//ytd-video-renderer[@class='style-scope ytd-item-section-renderer']//a[@id='video-title']/title"
        xpath = "//div[@id='contents']"
        #strTitle = r.xpath("/div[contains(@class ,‘style-scope ytd-item-section-renderer']").extract()
        elementContents = driver.find_element_by_xpath(xpath)
        elementItems = elementContents.find_elements_by_tag_name('ytd-video-renderer')
        if len(elementItems) > 0:
            for element in elementItems:
                elementA = element.find_element_by_id('video-title')
                strHref = elementA.get_attribute('href')
                strText = elementA.text
                #print('分析Title:%s'%(strText))
                if(strText.find(v[0]) > -1 and strText.find(v[1]) > -1):
                    #print('找到%s，加入%s，ok下一个！'%(strText,strHref))
                    log.info('找到%s，加入%s，ok下一个！'%(strText,strHref))
                    v.append(strHref)
                    break
        else:
            log.info('糟糕！解析%s失败'%(k))

        #如果没有匹配的，就用第一个结果吧，有时候歌名歌手只出现一个关键字匹配    
        if len(v) < 3:
            log.info('找不到%s，加入第一个结果%s！'%(k,elementItems[0].find_element_by_id('video-title').get_attribute('href')))
            v.append(elementItems[0].find_element_by_id('video-title').get_attribute('href'))

    driver.quit()
    #print(dictAll)
    #遍历数据容器调用youtube-dl下载，这部分可以改造成多线程任务队列
    for key in dictAll:
        musicItem = dictAll[key]
        #判断是否有下载地址
        if len(musicItem) > 2 and len(musicItem[2]) > 0 and musicItem[2].find('https') > -1:
            url = musicItem[2]
            downObj = downloadObj()
            downObj.download(key,url)
