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
    def __init__(self):
        pass
    
    def get_users(self, userids):
        print(numpy.unique(userids))        

    def avg_dload_time(self, urls, timestamps):
        #what is the average download time for each website
        for url in urls:
            print(url)
        for stamp in timestamps:
            pass

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
    INPUTFILE = "./Data2/accessLog202204" #Change to args
    file_lines = list()
    for line in open(INPUTFILE):
        line = ''.join(line.split(' /WebTracker/', maxsplit=1)[1:]).split(' HTTP')[0].split(':')
        if len(line) == 5:
            timestamp, userid, tabid, url, status = line[0], line[1], line[2], line[3], line[4]
            file_lines.append(LogFile(timestamp, userid, tabid, url, status))
    
    timestamps, userids, tabids, urls, statuses = [], [], [], [], []
    for line in file_lines:
        timestamps.append(line._timestamp)
        userids.append(line.get_userid())
        tabids.append(line._tabid)
        urls.append(line._url)
        statuses.append(line._status)

    run = Run()
    run.get_users(userids)
    
    #run.avg_dload_time(urls, timestamps)
    #run.overlap()
    #run.avg_dload_time_before_overlap()
    #run.websites_in_overlap()

if __name__ == "__main__":
    main()
