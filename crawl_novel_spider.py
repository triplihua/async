
#! /usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import re
import aiofiles
import time
# time是同步的，不要进入异步代码
LOOP = asyncio.get_event_loop()
#
HEADERS = {"Cookie": "__cdnuid=efaf90be3615c5e79e92852f271af777; jieqiVisitTime=jieqiArticlesearchTime%3D1534652382",
           "Referer": "http://www.biquge.com.tw/",
           "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Mobile Safari/537.36"}

BASE_URL = "http://www.biquge.com.tw"

async def get_html(session, url):
    try:
        # 6.31415926535 66.30009722709656秒  ----左边是时间没有控制好的错误例子，好像重复执行了500多次
        async with session.get(url=url, timeout=10.31415926535) as resp:
            # 这个timeout非常重要，笔趣阁的服务器是有点渣，他既不拒绝你又不答应你，时间自己好好考虑，尽可能的少重复请求
            if not resp.status // 100 == 2:
                print(resp.status)
                print("爬取", url, "出现错误")
            else:
                resp.encoding = 'gb18030'
                text = await resp.text()
                return text
    except Exception as e:
        print("出现错误", e)
        await get_html(session, url)


def parse_url(html):
    # 解析出来url
    pattern_url = re.compile('<dd><a href="(.*?\.html)">.*?</a></dd>')
    url_list = re.findall(pattern=pattern_url, string=html)
    return [BASE_URL + each for each in url_list]


def novel_content(html):
    # 返回两个列表
    pattern_title = re.compile('<h1>([\s\S]*?)</h1>')
    pattern_content = re.compile('(?<=&nbsp;&nbsp;&nbsp;&nbsp;)(.*?)(?=<br)')
    title_list = re.findall(pattern_title, html)
    content_list = re.findall(pattern_content, html)
    return title_list, content_list


async def download(title_list, content_list):
    # 下载  第二次测试下载只花了十三秒 643万字到手 13.034078598022461
    async with aiofiles.open(r'C:\Users\2191751138\Desktop\个人数据\小说\执魔\{}.txt'.format(title_list[0]), 'a',
                             encoding='utf-8') as f:
        # 列表直接写入,不拆了，浪费时间的事情不做
        await f.write('{}'.format(str(content_list)))
        # print(title, "下载完成")


async def get_content(session, chapter_url):
    # 错误处理很重要
    try:
        html = await get_html(session=session, url=chapter_url)
        title_list, content_list = novel_content(html)
    except Exception as e:
        print("出现错误,", e)
        await get_content(session, chapter_url)
    else:
        # 进行下载
        await download(title_list, content_list)
        print(title_list, url)


async def run(url):
         
    async with aiohttp.ClientSession() as session:
        session.headers = HEADERS
        html = await get_html(session, url)
        url_list = parse_url(html)
        tasks = []
        for each in url_list:
            tasks.append(asyncio.ensure_future(get_content(session, each)))
        await asyncio.gather(*tasks)



if __name__ == '__main__':
    func = lambda: time.time()
    start = func()
    # url = "http://www.biquge.com.tw/14_14055/"  # 三寸人间
    url = 'http://www.biquge.com.tw/0_948/'  # 执魔
    # 上面是我比较喜欢的作者的文章，不要尝试章节过多的，一方面写的也不怎么样，一方面这里有个缺点
    LOOP.run_until_complete(run(url))
    print(func() - start)


