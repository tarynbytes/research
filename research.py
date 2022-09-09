#!/usr/bin/python3

import time, numpy

'''
WebTracker data:

- - [14/Sep/2021:20:30:42 +0000] "POST /WebTracker/1631651439711:90e4a172c9eb701c:262:www.twitch.tv:1 HTTP/1.1" 404 5763 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"

This is an example of one line of the data. What we are interested in is the part after POST
Start with writing a program that read a file line by line. For each line, you have to "extract" the data after POST
The format is /WebTracker/TIMESTAMP:ID:TABID:URL:STATUS where STATUS is either 0, 1 or 2

in the example I gave

TIMESTAMP is 1631651439711
ID of the user is 90e4a172c9eb701c
tab id is 262
Status is 1
'''

class LogFile():
    def __init__(self, timestamp, userid, tabid, url, status) -> None:
        self._timestamp = timestamp
        self._userid = userid
        self._tabid = tabid
        self._url = url
        self._status = status
    
    def status(self, status):
        if status == 0:
            print("Tab was closed")
        elif status == 1:
            print(f"Tab started downloding at {self._timestamp}")
        elif status == 2:
            print(f"Tab finished downloading at {self._timestamp}")

    def get_userid(self):
        return self._userid


class Run():
    def __init__(self, matches) -> None:
        self._matches = matches

    def set_matches(self, urls, file_lines):
        #identifies all unique URL instances by indicies
        matches = []
        for n in range(len(urls)):
            s = urls[n]
            i = 0
            matched = []
            for i, line in enumerate(file_lines):
                if s == file_lines[i]._url:
                    matched.append(i)
                i += 1
            n +=1
            matches.append(matched)
        self._matches = matches

    def print_matches(self):
        print(f"{self._matches}\n")

    def avg_dload_time(self, file_lines):
        #what is the average download time for each website
        summ, start, stop, n = 0, 0, 0, 1
        for match in self._matches:
            for m in match:
                if int(file_lines[m]._status) == 0:
                    pass
                if int(file_lines[m]._status) == 1:
                    start = int(file_lines[m]._timestamp)
                    print(f"URL: {file_lines[m]._url}\tTab ID: {file_lines[m]._tabid}\tStarted: {file_lines[m]._timestamp}")
                if int(file_lines[m]._status) == 2:
                    stop = int(file_lines[m]._timestamp)
                    print(f"URL: {file_lines[m]._url}\tTab ID: {file_lines[m]._tabid}\tStopped: {file_lines[m]._timestamp}")
            print()
            summ = summ + (stop - start)
            average = summ / n
            n += 1
            #print(average)

    def overlap(self):
        #how many overlap are there (that is one website is still downloading, while a second one starts downloading)
        pass

    def avg_overlap_time(self):
        pass

    def avg_dload_time_before_overlap(self):
        #what is the average time that a website starts downloading before an overlap happens
        pass

    def websites_in_overlap(self):
        #how many websites are there in each overlap
        pass

    def more(self):
        #what else?
        pass


def main():
    #INPUTFILE = "./Data2/accessLog202206" #Change to args
    INPUTFILE = "./testLog202209"
    file_lines = list()
    for line in open(INPUTFILE):
        line = ''.join(line.split(' /WebTracker/', maxsplit=1)[1:]).split(' HTTP')[0].split(':')
        if len(line) == 5:
            timestamp, userid, tabid, url, status = line[0], line[1], line[2], line[3], line[4]
            file_lines.append(LogFile(timestamp, userid, tabid, url, status))
    
    timestamps, userids, tabids, urls, statuses = [], [], [], [], []
    run = Run(matches=[[]])

    for line in file_lines:
        urls.append(line._url)

    run.set_matches(numpy.unique(urls), file_lines)
    run.print_matches()
    run.avg_dload_time(file_lines)
    #run.overlap()
    #run.avg_dload_time_before_overlap()
    #run.websites_in_overlap()

if __name__ == "__main__":
    main()
