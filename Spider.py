import os
import requests
from pyquery import PyQuery as pq
import collections
import urllib.request
import socket
from uuid import uuid3, NAMESPACE_DNS
import Qtrac

Webpage = collections.namedtuple("webpage",["title", "url", "content"])


def read(url):
    # print('starting..')
    ok, path = _cached_url(url)
    # print('first finish..')
    if ok:
        with open(path, 'rb') as f:
            page = f.read()
            e = pq(page)
            websites = [_parse(a) for a in e('a').items()]
            return ok, websites
    else:
        return ok, path


def _cached_url(url):
    """
    缓存, 避免重复下载网页浪费时间
    """
    folder = 'cached'
    filename  = str(uuid3(NAMESPACE_DNS, url)).replace('-','')+'.html'
    Qtrac.report('cached', True)
    Qtrac.report(filename, True)
    path = os.path.join(folder, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
            return True, path
    else:
        # 建立 cached 文件夹
        if not os.path.exists(folder):
            os.makedirs(folder)
        # 发送网络请求, 把结果写入到文件夹中
        try:
            # with  as file:
            r = urllib.request.urlopen(url, None, 10)
            content = r.read()
            # body = _parse(data, limit)
            # if body:
            #     body = ["<h2>{}</h2>\n".format(escape(feed.title))] + body
            #     return True, body
            Qtrac.report(content, True)

            with open(path, 'wb') as f:
                f.write(content)
            return True, path
        except (ValueError, urllib.error.HTTPError, urllib.error.URLError,
                socket.timeout) as err:
            return False, "Error: {}: {}".format(url, err)
        # r = requests.get(url)
    # return r.content


def _parse(a):
    url = a.attr('href')
    title = a.val()
    _, path = _cached_url(url)
    w = Webpage(title, url, path)
    return w


def main():
    # for i in range(0, 250, 25):
    #     url = 'https://movie.douban.com/top250?start={}'.format(i)
    #     movies = movies_from_url(url)
    #     print('top250 movies', movies)
    read('https://movie.douban.com/top250?start=1')


if __name__ == '__main__':
    main()