from argparse import ArgumentParser
import os.path
import re
import pprint

class Log():
    """Class to define the fields of a line in a log file."""
    def __init__(self, log_str):
        self._log_str = log_str
        self._timestamp, self._userid, self._tabid, self._url, self._status = self._log_str
        self._timestamp = int(self._timestamp)
        self._tabid = int(self._tabid)
        self._status = int(self._status)

    def __str__(self):
        return f"TIMESTAMP: {self._timestamp}\tUSERID: {self._userid}\tTABID: {self._tabid}\tURL: {self._url}\tSTATUS: {self._status}"

    def __repr__(self):
        return f"{self._timestamp} {self._userid} {self._tabid} {self._url} {self._status}"

    @property
    def timestamp(self):
        return self._timestamp
    @property
    def userid(self):
        return self._userid
    @property
    def tabid(self):
        return self._tabid
    @property
    def url(self):
        return self._url
    @property
    def status(self):
        return self._status

class Sessions():
    """Breaks log strings into intelligble and queryable user sessions associated with a unique userid."""

    def __init__(self, log_strs, pp):
        self._log_strs = log_strs
        self._pp = pp

        self._unique_userids = {}
        self._sorted_lst = []

        self.set_unique_userids()
        self.set_sorted_lst()

    @property
    def unique_userids(self):
        return self._unique_userids

    def set_unique_userids(self):
        """Populates the _unique_userids dictionary where a unique userid is the key
                    and each log_str object containing that userid are that key's values."""
        for log_str in self._log_strs:
            if log_str.userid not in self._unique_userids.keys():
                self._unique_userids[log_str.userid] = [log_str]
            else:
                self._unique_userids[log_str.userid].append(log_str)

    @property
    def sorted_lst(self):
        return self._sorted_lst

    def set_sorted_lst(self):
        """Creates a sorted list of sessions.
            
            Sessions are defined as dictionaries with a USERID as a key, and log_str objects as values.
            log_str opbjects must have matching URLs and TABIDs to be part of that dictionary.
            In this way, the status (started/finished) of each corresponding url:tabid session can be tracked per user.

        """
        for key1, value1 in self._unique_userids.items():
            sessions = {}
            sorted_sessions = {}
            for val in value1:
                identifiers = (val.url, val.tabid)
                if identifiers not in sessions.keys():
                    sessions[identifiers] = [val]
                else:
                    sessions[identifiers].append(val)
            for key2, value2 in sessions.items():
                sessions_sorted = {key1: sorted(value2,key=lambda val: (val.url, val.tabid, val.timestamp))}
                self._sorted_lst.append(sessions_sorted)




class Analyzer():
    """Performs analysis operations on sessions."""
    CLOSED, STARTED, FINISHED = 0, 1, 2

    def __init__(self, sessions, pp):
        self._sessions = sessions
        self._pp = pp
    
    @property
    def timeline(self):
        return self._sessions.sorted_lst

    def avg_url_dload_time(self):
        """Determines the average download time for each URL for each user.
            This information can indicate connectivity speed per user."""
        for dct in self._sessions.sorted_lst:
            for key, value in dct.items():
                if 2 > len(value):
                    continue
                else:
                    download_times = []
                    for index, log_str in enumerate(value):
                        try:
                            if self.STARTED == value[index].status and self.FINISHED == value[index + 1].status:
                                dload_time = value[index + 1].timestamp - value[index].timestamp
                                download_times.append(dload_time)
                        except:
                            continue
                    if download_times:
                        print(f"\nUSERID: {key}\nURL: {log_str.url}, TABID: {log_str.tabid}")
                        print(f"Average download time: {sum(download_times) / len(download_times)}ms")

    def avg_session_overlap(self):
        """Determines the average overlap time between browsing sessions for each user.
            This information can indicate how frequent a user is to open new tabs."""
        pass

    def avg_dload_time_before_overlap(self):
        """Determines the average time that a website starts downloading before an overlap happens."""
        pass

    def websites_in_overlap(self):
        """Determines how many websites there are in each user's overlaps."""
        pass


    def more(self):
        """what else?"""
        pass


def parse_logs(filename:str):
    """Returns a list of parsed log_str objects, where each log_str object is a list of five strings."""
    with open(filename, 'r') as fp:
        log_strs = [log_str.replace("/WebTracker/", '').replace(" HTTP", '').split(':') for log_str in re.findall("/WebTracker/.*HTTP", fp.read())]
        return [Log(log_str) for log_str in log_strs if 5 == len(log_str)]

def handle_args():
    """Ensures logfile is passed in as argument."""
    parser = ArgumentParser(description='Process Logs')
    parser.add_argument("-l", "--log", dest="filename", required=True,
                    help="input log file", metavar="FILE")
    return parser.parse_args()


def main() -> int:
    args = handle_args()
    log_strs = parse_logs(args.filename)
    pp = pprint.PrettyPrinter(indent=2)

    sessions = Sessions(log_strs, pp)
    analyzer = Analyzer(sessions, pp)
    analyzer.avg_url_dload_time()

    pp.pprint(analyzer.timeline) # Shows chronological sequence of browsing behavior for each user



    return 0

if __name__ == "__main__":
    main()
