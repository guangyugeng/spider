import os
import requests
from pyquery import PyQuery as pq
import collections


Website = collections.namedtuple("website",["title", "url", "content"])


def read(url):
    page = _cached_url(url)
    e = pq(page)
    websites = [_parse(a) for a in e('a').items()]
    return websites


def _cached_url(url):
    """
    缓存, 避免重复下载网页浪费时间
    """
    folder = 'cached'
    filename = url.split('=', 1)[-1] + '.html'
    path = os.path.join(folder, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
            return s
    else:
        # 建立 cached 文件夹
        if not os.path.exists(folder):
            os.makedirs(folder)
        # 发送网络请求, 把结果写入到文件夹中
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)
    return r.content



def _parse(a):
    url = a.attr('href')
    title = a.val()
    content = _cached_url(url)
    w = Website(title, url, content)
    return w




def main():
    # for i in range(0, 250, 25):
    #     url = 'https://movie.douban.com/top250?start={}'.format(i)
    #     movies = movies_from_url(url)
    #     print('top250 movies', movies)
    read('https://movie.douban.com/top250?start=1')


if __name__ == '__main__':
    main()