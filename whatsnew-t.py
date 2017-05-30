
import sys
if sys.version_info < (3, 2):
    print("requires Python 3.2+ for concurrent.futures")
    sys.exit(1)
import argparse
import concurrent.futures
import multiprocessing
import os
import tempfile
import webbrowser
import Feed
import Qtrac
import Spider


def main():
    limit, concurrency, url, deep = handle_commandline()
    Qtrac.report("starting...")
    filename = os.path.join(os.path.dirname(__file__), "whatsnew.dat")
    Qtrac.report("starting {}".format(filename) ,True)
    futures = set()
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=concurrency) as executor:
        for feed in Feed.iter(filename):
            future = executor.submit(Feed.read, feed, limit)
            futures.add(future)
        Qtrac.report("futures {}".format(len(futures)) ,True)
        done, filename, canceled = process(futures)
        # print('canceled',canceled)
        if canceled:
            executor.shutdown()
    Qtrac.report("read {}/{} feeds using {} threads{} {}".format(done,
            len(futures), concurrency, " [canceled]" if canceled else "", filename))
    print()
    if not canceled:
        Qtrac.report("finished...", error=True)
        webbrowser.open(filename)


def handle_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--limit", type=int, default=0,
            help="the maximum items per feed [default: unlimited]")
    parser.add_argument("-c", "--concurrency", type=int,
            default=multiprocessing.cpu_count() * 4,
            help="specify the concurrency (for debugging and "
                "timing) [default: %(default)d]")
    parser.add_argument("-u", "--url", type=str, default='http://www.sina.com.cn/',
            help="指定爬虫开始地址 [default: %(default)s]")
    parser.add_argument("-d", "--deep", type=int, default=1,
            help="指定爬虫深度 [default: %(default)d]")
    args = parser.parse_args()
    return args.limit, args.concurrency, args.url, args.deep


def process(futures):
    canceled = False
    done = 0
    filename = "whatsnew.html"
    with open(filename, "w", encoding="utf-8") as file:
        file.write("<!doctype html>\n")
        file.write("<html><head><title>What's New</title></head>\n")
        file.write("<body><h1>What's New</h1>\n")
        canceled, results = wait_for(futures)
        if not canceled:
            for result in (result for ok, result in results if ok and
                    result is not None):
                done += 1
                for item in result:
                    file.write(item)
        else:
            done = sum(1 for ok, result in results if ok and result is not
                       None)
        file.write("</body></html>\n")
    Qtrac.report("read in {}".format(filename), True)
    return done, filename, canceled


# Could have yielded each result but that doesn't play nicely with
# KeyboardInterrupt.
def wait_for(futures):
    canceled = False
    results = []
    try:
        for future in concurrent.futures.as_completed(futures):
            err = future.exception()
            if err is None:
                ok, result = future.result()
                if not ok:
                    Qtrac.report(result, True)
                elif result is not None:
                    Qtrac.report("read {}".format(result[0][4:-6]), error=True)
                results.append((ok, result))
            else:
                raise err # Unanticipated
    except KeyboardInterrupt:
        Qtrac.report("canceling...")
        canceled = True
        for future in futures:
            future.cancel()
    return canceled, results


if __name__ == "__main__":
    # print("hello")
    main()
