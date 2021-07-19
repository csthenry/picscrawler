import re
import os
import requests
from lxml import etree
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
page = 0
bingcnt = 1


def getHtml(url: str) -> str:  # 获取网页
    fakeHeaders = {'User-Agent':
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                   AppleWebKit/537.36 (KHTML, like Gecko) \
                   Chrome/91.0.4472.124 Safari/537.36',
                   'Accept': 'text/html,application/xhtml+xml, */*'}  # 请求头
    try:
        r = requests.get(url, headers=fakeHeaders)
        r.encoding = r.apparent_encoding  # 网页编码
        return r.text  # 返回整个网页内容
    except Exception as e:
        errorCallBack(str(e))  # 输出错误信息
        return "Error"


def getBaiduPic(keyWord: str, n: int):
    url = "https://image.baidu.com/search/index?tn=baiduimage" \
          "&ipn=r&ct=201326592&cl=2&fm=detail&lm=&hd=&latest=" \
          "&copyright=&st=-1&sf=2&fmq=1626515893369_D&fm=detail&pv=&ic=0&nc" \
          "=1&z=0&se=&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word="
    url += keyWord
    html = getHtml(url)
    if html == "Error":  # 判断是否成功get网页
        return "Error"
    pt = '\"thumbURL\":.*?\"(.*?)\"'  # 正则表达式
    cnt = 1  # 已抓取图片
    for x in re.findall(pt, html):
        x = x.replace("%3a", ":")
        x = x.replace("%2f", "/")
        if not (x.lower().endswith(".jpg") or x.lower().endswith(".jpeg") or x.lower().endswith(".png")):
            continue
        try:
            infList.insert("end", x)
            win.update()  # 更新
            r = requests.get(x, timeout=3, stream=True)  # 获取对应网络资源
        except:
            continue  # 该图片地址无法访问，进入下一个地址
        try:
            pos = x.rfind(".")  # 处理后缀名
            f = open((os.getcwd().replace('\\', '/') + '/{0}{1}{2}').format(keyWord, cnt, x[pos:]), "wb")  # wb为二进制写方式
            f.write(r.content)  # 写入图片
            cnt += 1
            f.close()
        except IOError as e:
            if str(e).find('HTTP') != -1:  # 过滤掉不知道为什么的HTTP错误
                continue
            return e
        if cnt > n:
            break
    return True


def getBingPic(keyword: str, n: int):
    global bingcnt  # 已抓取图片
    global page  # 当前抓取的网页页面
    url = 'https://cn.bing.com/images/async?q=' + keyword + '&first=' + str(page) + '&count=35&relp=35&scenario=' \
                                                            'ImageBasicHover&datsrc=N_I&layout=RowBased&mmasync=1'
    html = etree.HTML(getHtml(url))
    if html == "Error":  # 判断是否成功get网页
        return "Error"
    conda_list = html.xpath('//a[@class="iusc"]/@m')
    for i in conda_list:
        img_url = re.search('"murl":"(.*?)"', i).group(1)
        try:
            infList.insert("end", img_url)
            win.update()  # 更新
            r = requests.get(img_url, timeout=3, stream=True)  # 获取对应网络资源
            delpos = img_url.rfind('?')
            if delpos != -1:
                img_url = img_url[0:delpos]
            if not (img_url.lower().endswith(".jpg") or img_url.lower().endswith(".jpeg") or img_url.lower().endswith(".png")):
                continue
            pos = img_url.rfind(".")
            print(img_url)
        except Exception as e:
            print("服务器Error:" + str(e))
            continue  # 该图片地址无法访问，进入下一个地址
        try:
            if bingcnt > n:
                bingcnt = 1
                return True
            f = open((os.getcwd().replace('\\', '/') + '/{0}{1}{2}').format(keyword, bingcnt, img_url[pos:]), "wb")  # wb为二进制写方式
            f.write(r.content)  # 写入图片
            bingcnt += 1
            f.close()
        except IOError as e:
            if str(e).find('HTTP') != -1:  # 过滤掉不知道为什么的HTTP错误
                continue
            return e

    if bingcnt <= n:
        page += 1
        print("触发翻页:[" + str(page) + "]，当前已抓取：" + str(bingcnt))
        return getBingPic(keyword, n)


def btGetDown():
    if (not getsum.get().isdigit()) or keyword.get() == "" or (not int(getsum.get())):
        errorCallBack("inputError")
        processText.set("状态：参数错误")
        lable_3["foreground"] = "red"
    else:
        if cbxCategory.current() == 0:
            if int(getsum.get()) > 30:
                tkinter.messagebox.showinfo("Tips", "百度图片最多抓取30张图片，请选择其他接口。")
                return
            else:
                gettingCallBack()
                callBack = getBaiduPic(keyword.get(), int(getsum.get()))
        else:
            gettingCallBack()
            callBack = getBingPic(keyword.get(), int(getsum.get()))
        if callBack == True:
            processText.set("状态：抓取完成")
        elif callBack != "Error":
            errorCallBack('1' + str(callBack))


def errorCallBack(_inf: str):
    if _inf == "inputError":
        tkinter.messagebox.showinfo("Error", "参数错误：未输入参数或输入参数不合法。\n错误参数：" + _inf)
    elif _inf[0] == '1':
        tkinter.messagebox.showinfo("Error", "写入错误：请检查写入权限或当前目录是否合法。\n错误信息：" + _inf[1:])
        processText.set("状态：写入错误")
    else:
        tkinter.messagebox.showinfo("Error", "网络错误：请检查网络连接并关闭代理。\n注：该错误不排除抓取的图片服务器故障。\n错误信息：" + _inf)
        processText.set("状态：网络或服务器错误")
    lable_3["foreground"] = "red"


def gettingCallBack():
    lable_3["foreground"] = "black"
    processText.set("状态：正在抓取...")
    win.update()  # 更新lable


getApi = ("百度图片", "Bing必应")
win = tk.Tk()  # 生成窗口
win.title("pics爬虫（Henry）")
win.resizable(width=False, height=False)  # 窗口禁止拉伸
keyword, getsum, processText = tk.StringVar(), tk.StringVar(), tk.StringVar()
processText.set("状态：待操作...")
lable_1 = ttk.Label(win, text="图片关键词：")
lable_2 = ttk.Label(win, text="抓取数量：")
lable_3 = ttk.Label(win, textvariable=processText)
lable_api = ttk.Label(win, text="API：")
cbxCategory = ttk.Combobox(win, width=10)
infList = tk.Listbox(win)
infList.insert("end", "pics爬虫（Author:Henry） 抓取信息：")
etKeyword = ttk.Entry(win, textvariable=keyword)
etSum = ttk.Entry(win, textvariable=getsum)
lable_1.grid(row=0, column=0, padx=15, pady=10, sticky='e')
lable_2.grid(row=1, column=0, padx=15, pady=10, sticky='e')
lable_3.grid(row=3, column=1, padx=15, pady=15, sticky='es')
lable_api.grid(row=2, column=1, padx=15, pady=0, sticky='wn')
cbxCategory.grid(row=2, column=1, padx=15, pady=0, sticky='en')
cbxCategory["values"], cbxCategory["state"] = getApi, "readonly"
cbxCategory.current(0)  # 选中第0项
infList.grid(row=4, column=0, columnspan=2, padx=0, pady=0, sticky='ewsn')
etKeyword.grid(row=0, column=1, padx=15, pady=10, sticky='w')
etSum.grid(row=1, column=1, padx=15, pady=10, sticky='w')
# key, num = input("请输入需要爬取的图片关键词和数量，用空格隔开：").split()
btGet = ttk.Button(win, text="Get!", command=btGetDown)
btGet.grid(row=3, column=0, columnspan=2, padx=15, pady=15, sticky='ws')  # columnspan代表占几列
# btGet.bind("<ButtonPress-1>")
# getBaiduPic(key, int(num))
win.mainloop()
