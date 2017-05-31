import os
import requests
from pyquery import PyQuery as pq
import collections
import urllib.request
import socket
from uuid import uuid3, NAMESPACE_DNS
import Qtrac
import re


Webpage = collections.namedtuple("webpage",["title", "url", "path"])


def read(url, key):
    ok, path = _cached_url(url, key)
    if ok:
        with open(path, 'rb') as f:
            page = f.read()
            # Qtrac.report('page {}'.format(page), True)
            e = pq(page)
            websites = [_parse(a, key) for a in e('a').items()]
            websites = [w for w in websites if w is not None]
            # Qtrac.report('websites {}'.format(websites), True)

            return ok, websites
    else:
        return ok, path


def _cached_url(url, key):
    """
    缓存, 避免重复下载网页浪费时间
    """
    folder = 'cached'
    try:
        filename  = str(uuid3(NAMESPACE_DNS, url)).replace('-','')+'.html'
    except (TypeError) as err:
        return False, "Error: {}: {}".format(url, err)
    Qtrac.report('cached {}'.format(filename))
    path = os.path.join(folder, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
            Qtrac.report('exists {}'.format(type(s)), True)
        return True, path
    else:
        # 建立 cached 文件夹
        if not os.path.exists(folder):
            os.makedirs(folder)
        # 发送网络请求, 把结果写入到文件夹中
        try:
            # Qtrac.report('mkr {}'.format(path), True)
            # with  as file:
            r = urllib.request.urlopen(url, None, 10)
            # Qtrac.report('r {}'.format(r), True)
            content = r.read()
            Qtrac.report('content {}'.format(type(content)), True)

            with open(path, 'wb') as f:
                f.write(content)
            return True, path
        except (ValueError, urllib.error.HTTPError, urllib.error.URLError,
                socket.timeout) as err:
            return False, "Error: {}: {}".format(url, err)


def _parse(a, key):
    url = a.attr('href')
    title = a.val()
    ok, path = _cached_url(url, key)
    Qtrac.report('parse {} {} {}'.format(url, title, path))
    if ok:
        w = Webpage(title, url, path)
        return w
    else:
        return None


# def main():
#     read('https://movie.douban.com/top250?start=1')
#
#
# if __name__ == '__main__':
#     main()