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
    limit, concurrency, url, deep, key = handle_commandline()
    Qtrac.report("starting...", True)
    Qtrac.report("url: {}, deep: {}".format(url, deep), True)
    jobs = queue.Queue()
    results = queue.Queue()
    create_threads(jobs, results, concurrency, deep ,key)
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
    parser.add_argument("-k", "--key", type=str, default="all",
            help="指定关键词 [default: %(default)d]")
    args = parser.parse_args()
    return args.limit, args.concurrency, args.url, args.deep, args.key


def create_threads(jobs, results, concurrency, deep, key):
    for _ in range(concurrency):
        thread = threading.Thread(target=worker, args=(jobs,
                results,deep,key))
        thread.daemon = True
        thread.start()


def worker(jobs, results, deep, key):
    while True:
        try:
            now_deep, url = jobs.get()
            ok, result = Website.read(url, key)
            # Qtrac.report('worker {} {}'.format(result, ok), True)
            # Qtrac.report('result {}'.format(result is not None), True)
            # results.put(websites)

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
            concurrency, " [canceled]" if canceled else ""), True)
    Qtrac.report("results {}".format(results.__str__()))


if __name__ == "__main__":
    main()
