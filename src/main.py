import sys,os
import baidu_translate as bt
from color_write import *

def programStratPrint():
    '打印程序开始语句'
    printRed('----------分割线----------\n\n')
    printBlue('  百度翻译爬虫 - By YYYCZ\n\n')
    printRed('----------分割线----------\n\n')

def programOverPrint():
    '打印程序结束语句'
    printRed('----------分割线----------\n\n')
    printBlue('***** 翻译程序已结束 *****\n\n')
    printRed('----------分割线----------\n\n')

def printResult(res_dict):
    '打印翻译结果'

    #打印语种
    printYellow('原文语种：' + res_dict['from'] + '\n')
    printYellow('目标语种：' + res_dict['to'] + '\n')
    print()

    #打印翻译结果
    printGreen('翻译结果：\n')
    print(res_dict['trans_result'])
    print()

    #打印字典解释
    if len(res_dict['dict_result']):
        for i in res_dict['dict_result']:
            print(i)
        print()

    printRed('----------分割线----------\n\n')

def selectLanguage(text, translator):
    '进行目标语种的选择'
    if len(text) <= 3:
        return (text,'')
    
    lan_sign = text.split('#')[-1]
    lan = translator.getLanguage(lan_sign)

    if lan == None:
        return (text,'')

    return (text[:-(len(lan_sign)+1)],lan[0])
    

if __name__ == '__main__':
    programStratPrint()
    printDarkRed('\r初始化中...')
    sys.stdout.flush()

    #加载百度翻译器
    translator = bt.BaiduTranslator()

    printDarkRed('\r初始化完毕！    \n\n')
    printRed('----------分割线----------\n\n')

    printSkyBlue('可选目标语种（在翻译内容结尾加上 "#" + "代号 或 名称" 进行选择）：\n')
    for i in translator.getLanguageList():
        print('%s - %s' % (i[0],i[1]))
    printRed('\n----------分割线----------\n\n')

    #已经翻译过了
    has_translated = False
    last_content = ''

    if len(sys.argv) > 1:
        s = ''
        for i in range(1,len(sys.argv)):
            s += sys.argv[i] + ' '

        #打印翻译内容以及结果
        s,lanTo = selectLanguage(s[:-1],translator)
        printSkyBlue('翻译内容：\n')
        print(s,end='\n\n')
        res = translator.translate(s,lanTo)
        printResult(res)

        has_translated = True
        last_content = s

    while True:
        #待翻译内容输入
        s = ''
        printSkyBlue('请输入要翻译的内容：\n（结尾加上 "#" + "代号 或 名称" 选择目标语种）\n（输入 #1 播放上次翻译的原文本音频）\n（输入 #2 播放上次翻译的翻译文本音频）\n（输入 #q 退出程序）\n')
        s = input()

        #根据 s 的内容控制流程
        if s == '#q':
            #退出程序
            programOverPrint()
            break
        elif s == '#1':
            #播放上次翻译原文本音频
            if not has_translated:
                printRed('\n还没有翻译的内容！\n')
            else:
                translator.getVocal(last_content,res['from'])
                if os.path.exists('vocal.mp3'):
                    os.system('vocal.mp3')
                else:
                    printRed('\n播放失败！\n')
                
            printRed('\n----------分割线----------\n\n')
            continue
        elif s == '#2':
            #播放上次翻译翻译文本音频
            if not has_translated:
                printRed('\n还没有翻译的内容！\n')
            else:
                translator.getVocal(res['trans_result'],res['to'])
                if os.path.exists('vocal.mp3'):
                    os.system('vocal.mp3')
                else:
                    printRed('\n播放失败！\n')
            
            printRed('\n----------分割线----------\n\n')
            continue
        
        #获取目标类型
        s,lanTo = selectLanguage(s,translator)
        
        #检测语种
        printDarkRed('\r检测语种中...')
        sys.stdout.flush()
        lanFrom = bt.BaiduTranslator.languageDetect(s)
        if lanFrom == '':
            programOverPrint()
            break

        #进行翻译
        printDarkRed('\r等待翻译中...')
        sys.stdout.flush()
        res = translator.translate(s,lanTo,lanFrom)

        sys.stdout.write('\r                    \n')
        sys.stdout.flush()

        #打印结果
        if bool(res):
            printResult(res)
        else:
            printRed('\n----------分割线----------\n\n')

        has_translated = True
        last_content = s