from argparse import ArgumentParser
import re
import hashlib
import collections
import csv


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
        self._logs = []
        self._starts = []
        self._dloads = []
        self._percent_dloads = None
        self._overlaps = []
        self._percent_overlaps = None
        self._urls_visited = []
        self._avg_dload_time_per_session = []
        self._avg_dload_time_per_url = []


    def __str__(self):
        ret_str = f"USERID: {self._userid}"
        for session in self._sessions:
            ret_str += f"\n{session}"
        return ret_str

    def get_logs(self):
        for session in self._sessions:
            for log in session.logs:
                self._logs.append(log)
        self._logs = sorted(self._logs, key=lambda val: (val.timestamp))

    def get_starts(self):
        """Pulls out all logs with status of 1 for that user."""
        for session in self._sessions:
            for log in session._session_logs:
                if 1 == log.status:
                    self._starts.append(log)
            
    def get_dloads(self):
        for session in self._sessions:
            for download in session.downloads:
                self._dloads.append(download)

            if session.avg_dload_time is not None:
                dct = {"Session Hash" : session.hash, "Average dload time" : session.avg_dload_time}
                self._avg_dload_time_per_session.append(dct)

        self._dloads = sorted(self._dloads, key=lambda val: (val.end, val.start))
        
        if 0 < len(self._dloads):
            self._percent_dloads = len(self._dloads) *2 / len(self._logs) *100

        for url in self._urls_visited:
            avg_times = collections.defaultdict(list)
            for session in self._sessions:
                if session.avg_dload_time is not None:
                    if url == session.url:
                        avg_times[url].append(session.avg_dload_time)

            for url, times in avg_times.items():
                dct = {"URL" : url, "Average dload time" : (sum(times) / len(times))}
                self._avg_dload_time_per_url.append(dct)


    def get_overlaps(self):

        last_end  = 0
        for dload in self._dloads:
            if dload.end > last_end:
                last_end = dload.end

        idx = 0
        while True:
            try:
                start_dload = self._dloads[idx]
                end_dload = self._dloads[idx]
                greatest_end = 0
                overlaps = {}

                for dload in self._dloads[idx:]:
                    if dload.start < end_dload.end:
                        overlaps[dload] = dload.end

                if 2 <= len(overlaps):
                    greatest_end = max(overlaps.values())
                    target_dload = list(overlaps.keys())[list(overlaps.values()).index(greatest_end)]
                    self._overlaps.append(Overlap(self, start_dload, list(overlaps.keys()), target_dload))

                    idx = self._dloads.index(target_dload)

                else:
                    idx += 1

                if greatest_end == last_end or idx == len(self._dloads) - 1:
                    break

            except IndexError:
                break
        
        if 0 < len(self._overlaps):
            overlap_logs = 0
            for overlap in self._overlaps:
                overlap_logs += len(overlap.overlapping_starts)
            self._percent_overlaps = overlap_logs / len(self._logs) *100

    def get_urls_visited(self):
        for session in self._sessions:
            if session.url not in self._urls_visited:
                self._urls_visited.append(session.url)

    @property
    def sessions(self):
        return self._sessions
    @property
    def id(self):
        return self._userid
    @property
    def logs(self):
        return self._logs
    @property
    def starts(self):
        return self._starts
    @property
    def dloads(self):
        return self._dloads
    @property
    def percent_dloads(self):
        return self._percent_dloads
    @property
    def overlaps(self):
        return self._overlaps
    @property
    def percent_overlaps(self):
        return self._percent_overlaps
    @property
    def urls_visited(self):
        return self._urls_visited
    @property
    def avg_dload_time_per_session(self):
        return self._avg_dload_time_per_session
    @property
    def avg_dload_time_per_url(self):
        return self._avg_dload_time_per_url

class Overlap():
    """An Overlap is defined as where one website is still downloading while a second one starts downloading."""

    def __init__(self, user, start, overlapping_starts, end):
        self._user = user
        self._start = start
        self._overlapping_starts = overlapping_starts
        self._end = end

    @property
    def start(self):
        return self._start
    @property
    def overlapping_starts(self):
        return self._overlapping_starts
    @property
    def end(self):
        return self._end


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
        self._avg_dload_time = None


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
                        self._downloads.append(Download(self, self.url, self._session_id, log, self._session_logs[index + 1]))
                except:
                    continue

    def get_avg_dload_time(self):
        download_times = []
        for download in self._downloads:
            download_times.append(download.end - download.start)
        if download_times:
            self._avg_dload_time = sum(download_times) / len(download_times)

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
    @property
    def avg_dload_time(self):
        return self._avg_dload_time



class Download():
    """Associates Downloads to each Session object."""

    def __init__(self, session, url, session_id, start_log, end_log):
        self._session = session
        self._url = url
        self._session_id = session_id
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
    def url(self):
        return self._url  
    @property
    def session_id(self):
        return self._session_id  
    @property
    def start_log(self):
        return self._start_log
    @property
    def end_log(self):
        return self._end_log
    @property
    def start(self):
        return self._start
    @property
    def end(self):
        return self._end



class OverlapAnalyzer():
    """Performs analysis operations on Users' Overlaps."""

    def __init__(self, users):
        self._users = users
    
    def print_overlaps(self, users):
        """Nicely prints overlap starting and ending among the sequence of a users' logs."""
        print("\n############################# USER OVERLAP STARTS AND ENDS ##################################")
        overlaps = collections.defaultdict(list)
        for user in users:
            if user.overlaps:
                print(f"\nUSER: {user.id}")
                for overlap in user.overlaps:
                    if overlap.overlapping_starts:
                        print(f"  OVERLAP START: {overlap.start.start}")
                        for dload in overlap.overlapping_starts:
                            print(f"   Overlapping log: {dload.start} {dload.end}")
                        print(f"  OVERLAP END:   {overlap.end.end}\n")


    def unique_websites_per_overlap(self, users):
        """Determines the unique URLs in each users' overlaps."""
        print("\n############################# WEBSITES IN USER OVERLAPS ###################################")
        urls_per_overlap = collections.defaultdict(list)
        for user in users:
            for i, overlap in enumerate(user.overlaps):
                urls = []
                ret_str = ''
                for dload in overlap.overlapping_starts:
                    if dload.url not in urls:
                        urls.append(dload.url)
                if urls:
                    for url in urls:
                        ret_str += f"\n\tURL: {url}"
                urls_per_overlap[user.id].append(f"  Overlap {i+1}: {ret_str}")
        print_results(urls_per_overlap)
    
    def unique_websites_out_of_all_overlaps(self, users):
        """Determines the unique URLs in each users' overlaps."""
        print("\n############################# WEBSITES IN USER OVERLAPS ###################################")
        overlap_urls = collections.defaultdict(list)
        for user in users:
            if 0 < len(user.overlaps):
                urls = []
                ret_str = ''
                for overlap in user.overlaps:
                    for dload in overlap.overlapping_starts:
                        if dload.url not in urls:
                            urls.append(dload.url)
                if urls:
                    for url in urls:
                        ret_str += f"\tURL: {url}\n"
                overlap_urls[user.id].append(f"{ret_str}")
        print_results(overlap_urls)

    def avg_overlap_time_per_user(self, users):
        """Determines the average overlap time per user."""
        print("\n############################ AVERAGE OVERLAP PER USER ####################################")
        avg_overlap_times = collections.defaultdict(list)
        for user in users:
            overlap_times = []
            for overlap in user.overlaps:
                overlap_times.append(overlap.end.end - overlap.start.start)
            if overlap_times:
                avg_overlap_times[user.id].append(f"  Average overlap time: {sum(overlap_times) / len(overlap_times)}ms")
        print_results(avg_overlap_times)

    # TO-DO
    def avg_overlapping_times_per_overlap_per_user(self, users):
        """Determines the average time before an overlapping log starts per each overlap per user."""
        print("\n############################ AVERAGE OVERLAP PER USER ####################################")
        avg_overlap_times = collections.defaultdict(list)

        print_results(avg_overlap_times)

        

class Graph():
    """Creates data visualizations."""

    def __init__(self, users, fields, rows, csvfile):
        self._users = users
        self._fields = fields
        self._rows = rows
        self._csvfile = csvfile


    def create_csv(self):
        with open(self._csvfile, 'w') as f:
            writer = csv.DictWriter(f, fieldnames = self._fields) 
            writer.writeheader() 
            writer.writerows(self._rows)

    def create_json(self):
        pass




def print_results(dct):
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
        session.get_avg_dload_time()

    user_dct = {}
    for user in users:
        session_lst = []
        for session in sessions:
            if user == session.userid:
                session_lst.append(session)
        user_dct[user] = User(session_lst, user)
    users = list(user_dct.values())

    for user in users:
        user.get_logs()
        user.get_urls_visited()
        user.get_starts()
        user.get_dloads()
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

    o = OverlapAnalyzer(users)

    fields = ['user', 'num_logs', 'num_sessions', 'num_dloads', 'percent_dloads', 'num_urls_visited', 'urls_visited',
        'avg_dload_time_per_url', 'avg_dload_time_per_session', 'num_overlaps', 'percent_overlaps']

    rows = []
    for user in users:
        dct = {
            "user" : user.id,
            "num_logs" : len(user.logs),
            "num_sessions" : len(user.sessions),
            "num_dloads" : len(user.dloads),
            "percent_dloads" : user.percent_dloads,
            "num_urls_visited" : len(user.urls_visited),
            "urls_visited" : user.urls_visited,
            "avg_dload_time_per_url" : user.avg_dload_time_per_url,
            "avg_dload_time_per_session" : user.avg_dload_time_per_session,
            "num_overlaps" : len(user.overlaps),
            "percent_overlaps" : user.percent_overlaps,
        }
        rows.append(dct)

    generic_data = Graph(users, fields, rows, "generic_data.csv")
    generic_data.create_csv()

    ''' Graphs '''

    ''' Each user's average time an overlap lasts            : user, avgoverlaptime '''
        #o.avg_overlap_time_per_user(users)
    ''' Each user's average time between overlapping logs    : user, avgtime peroverlap '''
        #o.avg_overlapping_times_per_overlap_per_user(users) # TO DO
    ''' Websites involved in overlap for each user            : user, overlaps... '''
        #o.unique_websites_per_overlap(users)
    ''' Unique websites in all overlaps combined per user    : user, websites '''
        #o.unique_websites_out_of_all_overlaps(users)
    ''' Each user's sequential intervals of overlaps         : user, overlaps '''
        #

    return 0

if __name__ == "__main__":
    main()
