'''
百度翻译爬虫 - By YYYCZ
----------
param:

from - 通常为 zh 或 en

to - 同理

query - 翻译的语句

sign - 加密值，在copy中有实现(e函数，以翻译字符串作为参数)

simple_means_flag - 填数字3

token - html中获取

domain - 填common

----------
注1：要获取 gtk 传给 sign 函数 且 gtk 必须是字符串

注2：必须获取 cookie，否则无法获取 token
'''

import subprocess
from functools import partial

# 修改 subprocess 的默认编码
subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")

import http
import urllib
import execjs
import requests
from lxml import etree

class BaiduTranslator:
    #生成headers - 通用
    __headers__ = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.50'}

    #js文件的路径
    __js_file_path__ = 'sign.js'

    #百度翻译母网站 - 通用
    __url__ = 'https://fanyi.baidu.com/'
    #检测语种的网站 - 通用
    __url_detect__ = 'https://fanyi.baidu.com/langdetect'
    #真正翻译的网站 - 通用
    __url_trans__ = 'https://fanyi.baidu.com/v2transapi'
    #获取语音的网站
    __url_vocal__ = 'https://fanyi.baidu.com/gettts'

    #js编译代码
    __javascript__ = ''

    __gtk__ = ''
    __token__ = ''
    __langList__ = {}
    __langList_rev_ = {}

    #参数列表
    __params__ = {
        'from':'zh',
        'to':'en',
        'query':'',
        'sign':0.0,
        'simple_means_flag':3,
        'token':'',
        'domain':'common'
    }

    #翻译结果
    __res__ = {}

    def __init__(self):
        if not 'Cookie' in BaiduTranslator.__headers__ or BaiduTranslator.__headers__['Cookie'] == '':
            BaiduTranslator.updateCookie()
        
        #爬取 html 以获取 token 和 gtk
        html = requests.get(url=BaiduTranslator.__url__,headers=BaiduTranslator.__headers__).text
        element = etree.HTML(html)

        #获取 window.common
        wcommon = execjs.eval(element.xpath('/html/body/script[1]/text()')[0].split(';')[0].replace('window[\'common\'] =',''))

        #获取 langList
        #self.__langList__ = wcommon['langList']
        #self.__langList_rev_ = {value: key for key, value in self.__langList__.items()}

        #获取 token
        self.__token__ = wcommon['token']

        #获取 gtk
        self.__gtk__ = element.xpath('/html/body/script[3]/text()')[0].split(';')[1]
        idx = self.__gtk__.find('window.gtk')
        self.__gtk__ = self.__gtk__[idx:].strip('window.gtk = ').strip('\'')

        #编译 js 代码
        with open(BaiduTranslator.__js_file_path__,'r',encoding='utf-8') as f:
            self.__javascript__ = execjs.compile(f.read())

            temp_dict = self.__javascript__.call('lanList')
            self.__langList__ = {key: value['zhName'] for key, value in temp_dict.items()}
            self.__langList_rev_ = {value: key for key, value in self.__langList__.items()}

    def getCookie():
        '获取cookie'
        return BaiduTranslator.__headers__['Cookie'] if 'Cookie' in BaiduTranslator.__headers__ else ''

    def updateCookie():
        '更新cookie（在线）'
        #构建一个CookieJar对象实例来保存cookie
        cookiejar = http.cookiejar.CookieJar()
        #使用HTTPCookieProcessor()来创建cookie处理器对象，参数为CookieJar()对象
        handler = urllib.request.HTTPCookieProcessor(cookiejar)
        #通过build_opener()来构建opener
        opener = urllib.request.build_opener(handler)
        
        try:
            #以get方法访问页面，访问之后会自动保存cookie到cookiejar中
            opener.open(BaiduTranslator.__url__)
            #可以按照标准格式将保存的Cookie打印出来
            cookieStr = ""
            for item in cookiejar:
                cookieStr = cookieStr + item.name + "=" +item.value + ";"
            #舍去最后一位的分号cls
            BaiduTranslator.__headers__['Cookie'] = cookieStr[:-1]
        except:
            print('BaiduTranslator - Cookie更新失败！')

    def clearCookie():
        '清除Cookie'
        if 'Cookie' in BaiduTranslator.__headers__:
            BaiduTranslator.__headers__['Cookie'] = ''

    def getLanguage(self, key_or_v : str):
        '''
        通过语言代号获取语音 或 通过语言名称获取代号
        ----------
        没有找到返回 None

        注意：获取的是 (key, value)
        '''

        if key_or_v in self.__langList__:
            return (key_or_v,self.__langList__[key_or_v])
        elif key_or_v in self.__langList_rev_:
            return (self.__langList_rev_[key_or_v],key_or_v)
        return None

    def getLanguageList(self):
        '获取所有可用语种的代号以及名称'
        return zip(self.__langList__.keys(),self.__langList__.values())

    def languageDetect(text):
        '''
        检测语种（在线）
        -----

        返回语种代号

        失败返回空字符串
        '''
        try:
            return requests.post(url=BaiduTranslator.__url_detect__,params={'query':text},headers=BaiduTranslator.__headers__).json()['lan']
        except:
            print('BaiduTranslator - 在线检测语种失败！')
        return ''

    def translate_raw(self, text, lanTo = '', lanFrom = ''):
        '''
        翻译且不获取结果（在线）
        
        参数
        -----
        1.text - 待翻译的文本

        2.lanTo - 目标语种 的 代号 ，为空时自动选择 中文 或 英文

        3.lanFrom - 原文语种 的 代号 ，为空时将自动检测

        -----
        成功翻译得到未经处理的字典

        此时再调用 translate_result 函数获取翻译结果字典
        '''

        #设置基本参数
        self.__params__ = {
            'from':'zh',
            'to':'en',
            'query':'',
            'sign':0.0,
            'simple_means_flag':3,
            'token':'',
            'domain':'common'
        }

        #检测语种
        if lanFrom == '':
            lan = BaiduTranslator.languageDetect(text)
            if lan == None:
                return
            lanFrom = lan

        self.__params__['from'] = lanFrom
        self.__params__['to'] = lanTo if lanTo != '' else 'en' if lanFrom == 'zh' else 'zh'

        #将待翻译内容传去翻译
        self.__params__['query'] = text
        self.__params__['token'] = self.__token__
        self.__params__['sign'] = self.__javascript__.call('sign', text, self.__gtk__)
        try:
            self.__res__ = requests.post(url=BaiduTranslator.__url_trans__,params=self.__params__,headers=BaiduTranslator.__headers__).json()
        except:
            print('BaiduTranslator - 在线翻译失败！')

    def translate_result(self):
        '''
        获取翻译得到的结果
        -----
        -----
        返回的是一个字典

        包括：

        1.翻译结果 - trans_result

        2.字典解释 - dict_result

        3.原语种名称 - from

        4.目标语种名称 - to

        -----
        获取失败返回空字典
        '''

        if bool(self.__res__):
            res = {'trans_result':'','dict_result':[],'from':self.__params__['from'],'to':self.__params__['to']}
            res['from'] = self.getLanguage(res['from'])[1]
            res['to'] = self.getLanguage(res['to'])[1]

            #将翻译结果输出
            res['trans_result'] = self.__res__['trans_result']['data'][0]['dst']

            #输出词典（如果有的话）
            if 'dict_result' in self.__res__ and 'simple_means' in self.__res__['dict_result'] and 'symbols' in self.__res__['dict_result']['simple_means']:
                for i in self.__res__['dict_result']['simple_means']['symbols'][0]['parts']:
                    #不一定会有part
                    part_str = 'part' if 'part' in i else 'part_name' if 'part_name' in i else ''
                    
                    #为空，说明内容与翻译内容一致，不显示
                    if len(i[part_str]) == 0:
                        break
                    
                    #打印词典内容
                    #中外文情况不同
                    if self.__params__['from'] == 'zh':
                        for j in i['means']:
                            if isinstance(j,dict):
                                p_str = 'part' if 'part' in j else 'part_name' if 'part_name' in j else ''
                                str_p = '[{}]'.format(j['part']) + ' ' if len(p_str) else ''
                                str_p += j['text'] + ' - '
                                idx = 0
                                if 'means' in j:
                                    for k in j['means']:
                                        idx += 1
                                        str_p += ' %d.%s; ' % (idx, k)
                                res['dict_result'].append(str_p[:-2])
                            else:
                                res['dict_result'].append(str(j))
                    else:
                        temp_str = i[part_str] + ' '
                        str_p = ''
                        for j in i['means']:
                            str_p += str(j) + '; '
                        res['dict_result'].append(temp_str + str_p[:-2])

            return res
        
        return {}

    def translate(self, text, lanTo = '', lanFrom = ''):
        '''
        翻译并获取结果（在线）
        
        参数
        -----
        1.text - 待翻译的文本

        2.lanTo - 目标语种 的 代号 ，为空时自动选择 中文 或 英文

        3.lanFrom - 原文语种 的 代号 ，为空时将自动检测

        -----
        成功翻译返回结果字典

        相当于 translate_raw 和 translate_result 的组合
        '''

        self.translate_raw(text,lanTo,lanFrom)
        return self.translate_result()

    def translate_result_raw(self):
        '获取原始翻译结果'
        return self.__res__

    def getVocal( self, text = '', lan = '', path = 'vocal.mp3', speed = 3):
        '''
        获取语音数据
        -----
        参数
        -----
        1.text - 为空默认用翻译结果作为翻译文本，此时 lan 无效
        
        2.lan - 文本的语种，为空自动检测

        3.path - 保存的路径，默认为 vocal.mp3

        4.speed - 语速，只能取 1、3、5，且默认为3
        '''

        #文本检测
        if text == '':
            if not 'trans_result' in self.__res__:
                return
            
            text = self.__res__['trans_result']
            lan = self.getLanguage(self.__res__['to'])[0]

        #语种检测
        if lan in self.__langList_rev_:
            lan = self.__langList_rev_[lan]
        elif lan == '' or not lan in self.__langList__:
            lan = self.languageDetect(text)

        #speed规范化
        if not speed in [1,3,5]:
            speed = 3

        #设置好参数列表
        params = {
            'lan' : lan,
            'text' : text,
            'spd' : speed,
            'source' : 'wed'
        }

        #下载音频
        try:
            mp3_file = requests.get(BaiduTranslator.__url_vocal__,params=params,headers=BaiduTranslator.__headers__)
        except:
            print('BaiduTranslator - 语音下载失败！')
            return

        #保存文件
        with open(path,'wb') as f:
            f.write(mp3_file.content)