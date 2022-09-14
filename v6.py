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

    CLOSED = 0

    def __init__(self, log_strs, pp):
        self._log_strs = log_strs
        self._pp = pp
        self._unique_userids = {}
        self._unique_sessions = {}
        self._sorted = {}
        self.remove_closed_tabs()
        self.set_unique_userids()
        self.set_unique_sessions()
        self.set_sorted()

    def remove_closed_tabs(self):
        """Removes closed tabs from the logfile because they are not significant to the analysis."""
        
        '''
        for index, log_str in enumerate(self._log_strs):
            print(index, log_str)
        print()
        '''
        for log_str in self._log_strs:
            if self.CLOSED == log_str.status:
                self._log_strs.remove(log_str)

        for log_str in self._log_strs:
            if self.CLOSED == log_str.status:
                self._log_strs.remove(log_str)

        for log_str in self._log_strs:
            if self.CLOSED == log_str.status:
                self._log_strs.remove(log_str)

        '''
        for index, log_str in enumerate(self._log_strs):
            print(index, log_str)
        '''

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
    def unique_sessions(self):
        return self._unique_sessions

    def set_unique_sessions(self):
        for key, value in self._unique_userids.items():
            for val in value:
                identifiers = (val.url, val.tabid)
                if identifiers not in self._unique_sessions.keys():
                    self._unique_sessions[identifiers] = [val]
                else:
                    self._unique_sessions[identifiers].append(val)
        #self._pp.pprint(self._unique_sessions)

    @property
    def sorted(self):
        return self._sorted

    def set_sorted(self):
        for key, value in self._unique_userids.items():
            sessions_sorted = sorted(value, key=lambda val: (val.url, val.tabid, val.status, val.timestamp))
            self._sorted[key] = sessions_sorted
        self._pp.pprint(self._sorted)


    

class Analyzer():
    """Performs analysis operations on sessions."""
    STARTED, FINISHED = 1, 2

    def __init__(self, sessions, pp):
        self._sessions = sessions
        self._pp = pp

    def avg_dload_time(self):
        """Determines the average download time for each URL.
            This information can indicate server response times for different websites."""
        pass

    def avg_dload_time_each_user(self):
        """Determines the average download time for each URL for each user.
            This information can indicate connectivity speed per user."""
        download_times = []
        for key, value in self._sessions.sorted.items():
            for val in value:
                pass
                #self._pp.pprint(val)

    def overlap(self):
        """Determines the overlap time for each URL; where one website is
                        still downloading while a second one starts downloading."""
        pass

    def avg_overlap_each_user(self):
        """Determines the average overlap time for each user.
            This information can indicate how frequent a user is to open new tabs."""
        pass

    def avg_overlap_time(self):
        """Determines the average overlap time for all sessions."""
        pass

    def avg_dload_time_before_overlap(self):
        """Determines the average time that a website starts downloading before an overlap happens."""
        pass

    def websites_in_overlap(self):
        """Determines how many websites there are in each overlap."""
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
    analyzer.avg_dload_time_each_user()

    return 0

if __name__ == "__main__":
    main()
