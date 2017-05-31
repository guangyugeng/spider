#!/usr/bin/env python3
# Copyright © 2012-13 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version. It is provided for
# educational purposes and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import argparse
import multiprocessing
import os
import queue
import tempfile
import threading
import webbrowser
import Feed
import Qtrac
import Website



def main():
    limit, concurrency, url, deep = handle_commandline()
    Qtrac.report("starting...", True)
    Qtrac.report("url: {}, deep: {}".format(url, deep), True)
    # filename = os.path.join(os.path.dirname(__file__), "whatsnew.dat")
    jobs = queue.Queue()
    results = queue.Queue()
    create_threads(limit, jobs, results, concurrency, deep)
    # todo = add_jobs(filename, jobs)
    init_jobs(url, jobs)
    process(jobs, results, concurrency)


def handle_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--limit", type=int, default=0,
            help="the maximum items per feed [default: unlimited]")
    parser.add_argument("-c", "--concurrency", type=int,
            default=multiprocessing.cpu_count() * 4,
            help="specify the concurrency (for debugging and "
                "timing) [default: %(default)d]")
    parser.add_argument("-u", "--url", type=str, default='https://movie.douban.com/top250?start=1',
            help="指定爬虫开始地址 [default: %(default)s]")
    parser.add_argument("-d", "--deep", type=int, default=0,
            help="指定爬虫深度 [default: %(default)d]")
    args = parser.parse_args()
    return args.limit, args.concurrency, args.url, args.deep


def create_threads(limit, jobs, results, concurrency, deep):
    for _ in range(concurrency):
        thread = threading.Thread(target=worker, args=(jobs,
                results,deep))
        thread.daemon = True
        thread.start()


def worker(jobs, results, deep):
    while True:
        try:
            now_deep, url = jobs.get()
            ok, result = Website.read(url)
            # Qtrac.report('worker {} {}'.format(result, ok), True)
            # Qtrac.report('result {}'.format(result is not None), True)
            # results.put(websites)

            # ok, result = Feed.read(-, limit)
            if not ok:
                Qtrac.report(result, True)
            elif result is not None:
                # Qtrac.report("read {}".format(url), True)
                for w in result:
                    results.put(w.path)
                    if now_deep < deep:
                        jobs.put((now_deep+1, w.url))
        finally:
            jobs.task_done()


def init_jobs(url, jobs):
    jobs.put((0, url))
    Qtrac.report("jobs init success, first url:{}".format(url), True)


# def add_jobs(filename, jobs):
#     for todo, feed in enumerate(Feed.iter(filename), start=1):
#         jobs.put(feed)
#     return todo


def process(jobs, results, concurrency):
    canceled = False
    try:
        jobs.join() # Wait for all the work to be done
    except KeyboardInterrupt: # May not work on Windows
        Qtrac.report("canceling...")
        canceled = True
    # if canceled:
    #     done = results.qsize()
    # else:
    #     done, filename = output(results)
    Qtrac.report("read {} webpages using {} threads{}".format(results.qsize(),
            concurrency, " [canceled]" if canceled else ""))
    print()
    # if not canceled:
    #     webbrowser.open(filename)


def output(results):
    done = 0
    filename = os.path.join(tempfile.gettempdir(), "whatsnew.html") 
    with open(filename, "wt", encoding="utf-8") as file:
        file.write("<!doctype html>\n")
        file.write("<html><head><title>What's New</title></head>\n")
        file.write("<body><h1>What's New</h1>\n")
        while not results.empty(): # Safe because all jobs have finished
            result = results.get_nowait()
            done += 1
            for item in result:
                file.write(item)
        file.write("</body></html>\n")
    return done, filename


if __name__ == "__main__":
    main()
