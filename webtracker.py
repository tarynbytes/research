from argparse import ArgumentParser
import os.path
import re
import hashlib
import collections
import threading

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
        return f"\t\tTIMESTAMP: {self._timestamp}\tUSERID: {self._userid}\tTABID: {self._tabid}\tURL: {self._url}\tSTATUS: {self._status}"

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



class User():
    """User objects are groups of sessions associated with a particular userid."""
    def __init__(self, sessions, userid):
        self._sessions = sessions
        self._userid = userid
        self._starts = []
        self._overlaps = []

    def __str__(self):
        ret_str = f"USERID: {self._userid}"
        for session in self._sessions:
            ret_str += f"\n{session}"
        return ret_str

    def get_starts(self):
        for session in self._sessions:
            for log in session._session_logs:
                if 1 == log.status:
                    self._starts.append(log)
            
    def get_overlaps(self):
        for session in self._sessions:
            for download in session.downloads:
                for start in self._starts:
                    if download.start < start.timestamp < download.end and start.url != session.url:
                        self._overlaps.append(Overlap(self, download.start_log, start, download.end_log))

    @property
    def sessions(self):
        return self._sessions
    @property
    def id(self):
        return self._userid
    @property
    def starts(self):
        return self._starts
    @property
    def overlaps(self):
        return self._overlaps



class Session():
    """Session objects are defined as a group of logs with the same userid, url, and tabid."""
    def __init__(self, session_id):
        self._session_id = session_id
        self._session_logs = []
        self.userid = None
        self.url = None
        self.tabid = None
        self._start = None
        self._downloads = []

    def sort_logs(self):
        self._session_logs = sorted(self._session_logs, key=lambda val: (val.userid, val.url, val.tabid, val.timestamp))
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
                        self._downloads.append(Download(self, log, self._session_logs[index + 1]))
                except:
                    continue

    def __str__(self):
        ret_str = f"\tSESSION HASH:{self._session_id}"
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
    @property
    def hash(self):
        return self._session_id



class Download():
    """Associates Downloads to each Session object."""
    def __init__(self, session, start_log, end_log):
        self._session = session
        self._start_log = start_log
        self._end_log = end_log
        self._start = start_log.timestamp
        self._end = end_log.timestamp

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
    def start_log(self):
        return self._start_log
    @property
    def end(self):
        return self._end
    @property
    def end_log(self):
        return self._end_log


class Overlap():
    """An Overlap is defined as where one website is still downloading while a second one starts downloading."""

    def __init__(self, user, start, overlap, end):
        self._user = user
        self._start = start
        self._overlap = overlap
        self._end = end

    @property
    def start(self):
        return self._start
    @property
    def overlap_log(self):
        return self._overlap
    @property
    def end(self):
        return self._end


class Analyzer():
    """Performs analysis operations on [sessions corresponding to] Users."""
    def __init__(self, users):
        self._users = users
    
    def timeline(self, users):
        """ Prints a chronological, intelligible sequence of events of the whole log file for reference."""
        print("################################### TIMELINE #######################################")
        for user in users:
            print(user)
       
    def avg_url_dload_time(self, users):
        """Determines the average download time for each session for each user."""
        print("\n####################### AVERAGE DOWNLOAD TIME PER USER ##############################")
        avg_times = collections.defaultdict(list)
        for user in users:
            for session in user.sessions:
                download_times = []
                for download in session.downloads:
                    download_times.append(download.end - download.start)
                if download_times:
                    avg_times[user.id].append(f"URL: {session.url}, TABID: {session.tabid}, Average download time: {sum(download_times) / len(download_times)}ms")
        self._print_results(avg_times)

    def print_overlaps(self, users):
        """Nicely prints all users' overlaps."""
        print("\n################################## USER OVERLAPS #######################################")
        overlaps = collections.defaultdict(list)
        for user in users:
            for overlap in user.overlaps:
                overlaps[user.id].append(f"  [!] Overlap\n      START: {overlap.start}\n      OVERLAP: {overlap.overlap_log}\n      END:     {overlap.end}")
        self._print_results(overlaps)

    def overlaps(self, users):
        """Determines the number of overlaps per user."""
        print("\n########################## NUMBER OVERLAPS PER USER #################################")
        num_overlaps = collections.defaultdict(list)
        for user in users:
            if 0 < len(user.overlaps):
                num_overlaps[user.id].append(f"  Number of overlaps: {len(user.overlaps)}")
        self._print_results(num_overlaps)

    def avg_overlap_time(self, users):
        """Determines the average overlap time per user."""
        print("\n########################## AVERAGE OVERLAP PER USER #################################")
        avg_overlap_times = collections.defaultdict(list)
        for user in users:
            overlap_times = []
            for overlap in user.overlaps:
                overlap_times.append(overlap.overlap_log.timestamp - overlap.start.timestamp)
            if overlap_times:
                avg_overlap_times[user.id].append(f"  Average overlap time: {sum(overlap_times) / len(overlap_times)}ms")
        self._print_results(avg_overlap_times)
 
    '''
    def websites_in_overlap(self, users):
        """Determines how many websites there are in each users' overlaps."""
        print("\n########################## WEBSITES IN USER OVERLAPS ################################")
        for user in users:
            urls = []
            for overlap in user.overlaps:
                if overlap.overlap_log.url not in urls:
                    urls.append(overlap.overlap_log.url)
                    print(overlap.overlap_log.url)
    '''

    def more(self):
        """what else?"""
        pass
    
    
    def _print_results(self, dct):
        """Prints analyses via dictionary, {userid: "result_string"}"""
        for key, value in dct.items():
            print(f"\nUSERID: {key}")
            for val in value:
                print(f"{val}")




def generate_user_sessions(logs):
    """ Initializes Session objects and returns a list of User objects [corresponding to Sessions]."""
    sessions = {}
    users = []

    for log in logs:
        if log.userid not in users:
            users.append(log.userid)
        try:
            sessions[log.session_hash].add_log(log)
        except Exception as e:
            sessions[log.session_hash] = Session(log.session_hash)
            sessions[log.session_hash].add_log(log)

    sessions = list(sessions.values())
    for session in sessions:
        session.sort_logs()
        session.get_downloads()

    user_dct = {}
    for user in users:
        session_lst = []
        for session in sessions:
            if user == session.userid:
                session_lst.append(session)
        user_dct[user] = User(session_lst, user)
    users = list(user_dct.values())



    for user in users:
        user.get_starts()
        user.get_overlaps()

    return users

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
    users = generate_user_sessions(logs)

    analyzer = Analyzer(users)

    """
    num_threads = 12
    threads = []

    chunk_size = len(analyzer.users)/num_threads
    for thread_idx in range(num_threads):
        thread = threading.Thread(target=analyzer.timeline, args=(users[chunk_size * thread_idx : chunk_size * thread_idx + 1],))
        threads.append(thread)
    
    for thread in threads:
        thread.start()
    
    print("Threads started")

    for thread in threads:
        thread.join()

    print("Threads joined")
    """
    #analyzer.timeline(users)
    #analyzer.avg_url_dload_time(users)
    #analyzer.print_overlaps(users)
    #analyzer.overlaps(users)
    #analyzer.avg_overlap_time(users)
    #analyzer.websites_in_overlap(users)

    return 0

if __name__ == "__main__":
    main()
