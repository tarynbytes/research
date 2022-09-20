from argparse import ArgumentParser
import os.path
import re
import hashlib
import collections

class Log():
    """Class to define the fields of a line in a log file."""
    def __init__(self, log_str):
        self._log_str = log_str
        self._timestamp, self._userid, self._tabid, self._url, self._status = self._log_str
        self._timestamp = int(self._timestamp)
        self._tabid = int(self._tabid)
        self._status = int(self._status)
        self._session_hash = self._hash()

    def _hash(self):
        str_to_hash = f"{self.userid}{self.url}{self.tabid}"
        hash_obj =  hashlib.md5(bytes(str_to_hash, "utf-8"))
        return hash_obj.hexdigest()
        
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
    @property
    def session_hash(self):
        return self._session_hash



class Session():
    """ Session objects are defined as a group of logs with the same userid, url, and tabid. """
    def __init__(self, session_id):
        self._session_id = session_id
        self._session_logs = []
        self.userid = None
        self.url = None
        self.tabid = None
        self._start = None
        self._downloads = []

    def sort_logs(self):
        self._session_logs = sorted(self._session_logs, key=lambda val: val.timestamp)
        self._start = self._session_logs[0].timestamp

    def add_log(self, log):
        if not self.userid:
            self.userid = log.userid
            self.url = log.url
            self.tabid = log.tabid
        self._session_logs.append(log)

    def get_downloads(self):
        if 2 <= len(self._session_logs):
            for index, log in enumerate(self._session_logs):
                try:
                    if 1 == self._session_logs[index].status and 2 == self._session_logs[index + 1].status:
                        self._downloads.append(Download(self, log.timestamp, self._session_logs[index + 1].timestamp))
                except:
                    continue

    def __str__(self):
        ret_str = f"SESSION HASH:\t{self._session_id}"
        for log in self._session_logs:
            ret_str += f"\n\t{log.__str__()}"

        return ret_str

    def __contains__(self, log):
        if isinstance(log, Log):
            return log.session_hash == self._session_id

    @property
    def downloads(self):
        return self._downloads
    @property
    def start(self):
        return self._start
    @property
    def logs(self):
        return self._session_logs
    
class Download():
    """Associates Downloads to each Session object. """
    def __init__(self, session, start, end):
        self._session = session
        self._start = start
        self._end = end

    def __contains__(self, download):
        if (isinstance(download, Downloads)):
            if (download.start <= self.start <= download.end) or (download.start <= self.end <= download.end):
                return True 
        return False

    def __str__(self):
        return f"Download:\n\tstart:\t{self.start}\n\tend:\t{self.end}"
        
    @property
    def session(self):
        return self.session
    @property
    def start(self):
        return self._start
    @property
    def end(self):
        return self._end


class Analyzer():
    """Performs analysis operations on sessions."""
    def __init__(self, sessions):
        self._sessions = sessions
    
    def timeline(self, sessions):
        sessions_sorted = collections.defaultdict(list)
        for session in sessions:
            sessions_sorted[session.userid].append(f"START: {session.start}, URL: {session.url}, TABID: {session.tabid}\n{session.logs}")
        for key, value in sessions_sorted.items():
            print(f"\nUSERID: {key}")
            for val in value:
                print(f"{val}")

    def avg_url_dload_time(self, sessions):
        """Determines the average download time for each session for each user.
            This information can indicate connectivity speed per user."""
        avg_times = collections.defaultdict(list)
        for session in sessions:
            download_times = []
            for download in session.downloads:
                download_times.append(download.end - download.start)
            if download_times:
                avg_times[session.userid].append(f"URL: {session.url}, TABID: {session.tabid}, Average download time: {sum(download_times) / len(download_times)}ms")
        
        for key, value in avg_times.items():
            print(f"\nUSERID: {key}")
            for val in value:
                print(f"{val}")
        

    def avg_session_overlap(self, sessions):
        """Determines the average overlap time among sessions per user.
            Overlap defined as where one website is still downloading while a second one starts downloading.
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



def generate_sessions(logs):
    sessions = {}
    for log in logs:
        try:
            sessions[log.session_hash].add_log(log)
        except Exception as e:
            sessions[log.session_hash] = Session(log.session_hash)
            sessions[log.session_hash].add_log(log)
    sessions = list(sessions.values())
    for session in sessions:
        session.sort_logs()
        session.get_downloads()

    return sorted(sessions, key=lambda session: (session.start, session.userid, session.url, session.tabid))

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
    logs = parse_logs(args.filename)
    sessions = generate_sessions(logs) # returns a list of Session objects
    analyzer = Analyzer(sessions)
    analyzer.timeline(sessions)
    #analyzer.avg_url_dload_time(sessions)

    return 0

if __name__ == "__main__":
    main()
