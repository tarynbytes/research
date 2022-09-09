#!/usr/bin/python3

import time, numpy

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
    def __init__(self, matches, organized) -> None:
        self._matches = matches
        self._organized = organized

    def set_matches(self, urls, file_lines):
        #identifies all unique URL instances by indicies
        matches = []
        for n in range(len(urls)):
            s = urls[n]
            matched = []
            for i, line in enumerate(file_lines):
                if s == file_lines[i]._url:
                    matched.append(i)
            matches.append(matched)
        self._matches = matches

    def print_matches(self):
        print(f"{self._matches}\n")

    def organize_parsed_data(self, file_lines):
        summ, start, stop, n, urls, organized = 0, 0, 0, 1, [] ,[]
        for match in self._matches:
            for m in match:
                if int(file_lines[m]._status) != 0 and file_lines[m]._url not in urls:
                    urls.append(file_lines[m]._url)

        for url in urls:
            for match in self._matches:
                for m in match:
                    if int(file_lines[m]._status) != 0 and file_lines[m]._url == url:
                        organized.append(file_lines[m])
        self._organized = organized
    
    def print_organized(self):
        print(f"{self._organized}\n")

    def avg_dload_time(self):
        #what is the average download time for each website
        for i, line in enumerate(self._organized):
            #if True:
            try:
                if line._url == self._organized[i+1]._url and line._tabid == self._organized[i+1]._tabid:
                    if int(line._status) == 1:
                        started = int(line._timestamp)
                    elif int(line._status) == 2:
                        stopped = int(line._timestamp)
                try:
                    if started and stopped:
                        summ = 0
                        diff = stopped - started
                        summ = summ + diff
                        print(f"\nDownload time for URL {line._url}, tabid {line._tabid} (index {i}):\nStarted: {started}\nStopped: {stopped}\nDownload Time: {summ}ms")
                        #average = summ / n
                        #n += 1
                        #print(average)
                        started, stopped = 0, 0
                except:
                    print(f"Both values not populated by index {i}.")
            except:
                print("\nEnd of range")
                break

        
    def overlap(self):
        #how much overlap is there (that is one website is still downloading, while a second one starts downloading)
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
    run = Run(matches=[[]], organized=[])

    for line in file_lines:
        urls.append(line._url)


    run.set_matches(numpy.unique(urls), file_lines)
    run.organize_parsed_data(file_lines)
    run.avg_dload_time()
    #run.overlap()
    #run.avg_dload_time_before_overlap()
    #run.websites_in_overlap()

if __name__ == "__main__":
    main()
