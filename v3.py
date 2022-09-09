from argparse import ArgumentParser
import os.path
import re

class Log():
    def __init__(self, log_str):
        self._log_str = log_str
        self._timestamp, self._userid, self._tabid, self._url, self._status = self._log_str
        self._timestamp = int(self._timestamp)
        self._tabid = int(self._tabid)
        self._status = int(self._status)

    def check_status(self):
        if 0 == self.status:
            print("Tab was closed")
        elif 1 == self.status:
            print(f"Tab started Downloading at: {self.timestamp}")
        elif 2 == self.status:
            print(f"Tab finished downloading at {self.timestamp}")
        else:
            print(f"Unrecognized status: {self.status}")

    def __str__(self):
        return f"timestamp: {self._timestamp}\tuser_id: {self._userid}\ttab_id: {self._tabid}\turl: {self._url}\tstatus: {self._status}"

    def __repr__(self):
        return f"{self._timestamp} {self._tabid} {self._userid} {self._url} {self._status}"

    @property
    def user_id(self):
        return self._userid
    
    @property
    def timestamp(self):
        return self._timestamp
    @property
    def tabid(self):
        return self._tabid
    @property
    def url(self):
        return self._url
    @property
    def status(self):
        return self._status

class Analyzer():
    def __init__(self, logs):
        self._logs = logs
        self._unique_urls = {}
        self.get_unique_urls()

    def get_unique_urls(self):
        for log in self._logs:
            if log.url not in self._unique_urls.keys():
                self._unique_urls[log.url] = [log]
            else:
                if 0 == log.status:
                    continue
                else:
                    self._unique_urls[log.url].append(log)

    def print_unique_urls(self):
        for key, value in self._unique_urls.items():
            print(f"Address: {key}")
            for log in value:
                print(f"\t{log}")

    def avg_dload_time(self):
        for key, value in self._unique_urls.items():
            print(f"URL: {key}")
            sessions = {}
            download_times = []
            for val in value:
                session_identifiers = (val.user_id, val.tabid)
                if session_identifiers not in sessions.keys():
                    sessions[session_identifiers] = [val]
                else:
                    sessions[session_identifiers].append(val)
            
            for key, value in sessions.items():
                sessions_sorted = sorted(value,key=lambda val: val.status)
                dload_time = -1
                if 2 <= len(sessions_sorted):
                    if sessions_sorted[-1].status == 2 and sessions_sorted[0].status == 1:
                        dload_time = sessions_sorted[-1].timestamp - sessions_sorted[0].timestamp
                        download_times.append(dload_time)
                
                if dload_time != -1:
                    print(f"User: {key[0]}\tTab: {key[1]}\tDownload time:\t{dload_time} ms")

            if download_times:
                print(f"Average time to download from URL: {sum(download_times) / len(download_times)} ms")




def parse_logs(filename:str):
    with open(filename, 'r') as fp:
        log_strs = [log.replace("/WebTracker/", '').replace(" HTTP", '').split(':') for log in re.findall("/WebTracker/.*HTTP", fp.read())]
        return [Log(log) for log in log_strs if 5 == len(log)]

def handle_args():
    parser = ArgumentParser(description='Process Logs')
    parser.add_argument("-l", "--log", dest="filename", required=True,
                    help="input log file", metavar="FILE")
    return parser.parse_args()

def main() -> int:
    args = handle_args()
    logs = parse_logs(args.filename)

    analyzer = Analyzer(logs)
    analyzer.avg_dload_time()

    return 0




if __name__ == "__main__":
    main()
