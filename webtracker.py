from argparse import ArgumentParser
import os.path
import re
import hashlib
import collections
import threading
import pandas as pd


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
        self._overlap_ones = []
        self._overlap_dloads = []
        self._dynamic_overlaps = []

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
        self._dloads = sorted(self._dloads, key=lambda val: (val.end, val.start))

    def get_static_overlaps(self):
        """Gets all static instances in which:
            1) a user log with status of 1 occurs between a Download.
            2) the starting log of a Download occurs between the start and end of another Download."""
        dloads = []
        for session in self._sessions:
            for download in session.downloads:
                dloads.append(download)        
        for session in self._sessions:
            for download in session.downloads:
                overlapping_starts = []
                overlapping_dloads = []
                for start in self._starts:
                    if download.start < start.timestamp < download.end:
                        if start.session_hash != session.hash:
                            overlapping_starts.append(start)
                for dload in self._dloads:
                    if download.start < dload.start < download.end:
                        if dload.session_id != session.hash:
                            overlapping_dloads.append(dload)

                overlapping_starts = sorted(overlapping_starts, key=lambda val: (val.timestamp))
                overlapping_dloads = sorted(overlapping_dloads, key=lambda val: (val.start))

                self._overlap_dloads.append(Overlap(self, download.start_log, overlapping_dloads, download.end_log))
                self._overlap_ones.append(Overlap(self, download.start_log, overlapping_starts, download.end_log))

          
    def get_dynamic_overlaps(self):

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
                    self._dynamic_overlaps.append(Overlap(self, start_dload, list(overlaps.keys()), target_dload))

                    idx = self._dloads.index(target_dload)

                else:
                    idx += 1

                if greatest_end == last_end or idx == len(self._dloads) - 1:
                    break

            except IndexError:
                break
        

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
    def overlap_ones(self):
        return self._overlap_ones
    @property
    def overlap_dloads(self):
        return self._overlap_dloads
    @property
    def dynamic_overlaps(self):
        return self._dynamic_overlaps




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
        self._avg_dload_times = None


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

    def get_avg_dload_times(self):
        download_times = []
        for download in self._downloads:
            download_times.append(download.end - download.start)
        if download_times:
            self._avg_dload_times = sum(download_times) / len(download_times)

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
    def avg_dload_times(self):
        return self._avg_dload_times


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



class TimelineAnalyzer():
    """Performs analysis operations on the sequence of events in a Log File."""

    def __init__(self, users):
        self._users = users
    
    def timeline(self, users):
        """ Prints whole log file in organization of sequential sessions per user.""" 
        print("################################### TIMELINE #######################################")
        for user in users:
            print(user)



class DownloadAnalyzer():
    """Performs analysis operations on Users' Downloads."""

    def __init__(self, users):
        self._users = users
    
    def avg_url_dload_time_per_user_sessions(self, users):
        """Determines the average download time for each session for each user (prints User 'avg_dload_times' property)"""
        print("\n####################### AVERAGE DOWNLOAD TIME PER USER ##############################")
        avg_times = collections.defaultdict(list)
        for user in users:
            for session in user.sessions:
                if session.avg_dload_times is not None:
                    avg_times[user.id].append(f"URL: {session.url}, TABID: {session.tabid}, Average download time: {session.avg_dload_times}ms")
        print_results(avg_times)

    def avg_url_dload_time_per_user(self, users):
        """Determines the average download time for each session for each user."""
        print("\n####################### AVERAGE URL DOWNLOAD TIME PER USER ###########################")
        avg_url_times = collections.defaultdict(list)
        for user in users:
            urls = []
            url_times = collections.defaultdict(list)
            for session in user.sessions:
                if session.avg_dload_times is not None:
                    if session.url not in urls:
                        urls.append(session.url)
            for url in urls:
                for session in user.sessions:
                    if session.avg_dload_times is not None:
                        if url == session.url:
                            url_times[url].append(session.avg_dload_times)
            for url, times in url_times.items():
                avg_url_times[user.id].append(f"URL: {url}, Average download time: {sum(times) / len(times)}ms")
        print_results(avg_url_times)


    def percent_downloads_per_user(self, users):
        """Out of all user logs, what percentage of logs are Downloads (a 1 status with an identified matching 2."""
        pass




class WebsiteAnalyzer():
    """Performs analysis operations on Users' websites."""

    def __init__(self, users):
        self._users = users

    def num_unique_websites_per_user(self, users):
        """Determines the total number of unique websites each user visited and displays what websites."""
        print("\n############################ WEBSITES VISITED PER USER ###################################")
        user_websites = collections.defaultdict(list)
        for user in users:
            websites = []
            for session in user.sessions:
                if session.url not in websites:
                    websites.append(session.url)
            if websites:
                ret_str = ''
                for site in websites:
                    ret_str += f"\t{site}\n"
                ret_str += f"Total websites: {len(websites)}"
                user_websites[user.id].append(f"Websites visited by user:\n{ret_str}")
        print_results(user_websites)


    
class OverlapAnalyzer():
    """Performs analysis operations on Users' Overlaps."""

    def __init__(self, users):
        self._users = users
    
    def number_dynamic_overlaps(self, users):
        """Determines the number of overlaps per user."""
        print("\n############################ NUMBER OVERLAPS PER USER ###################################")
        num_dynamic_overlaps = collections.defaultdict(list)
        for user in users:
            if 0 < len(user.dynamic_overlaps):
                num_dynamic_overlaps[user.id].append(f"  Number of overlaps: {len(user.dynamic_overlaps)}")
        print_results(self, num_dynamic_overlaps)

    # Fix
    def websites_in_dynamic_overlaps(self, users):
        """Determines how many websites there are in each users' overlaps."""
        print("\n############################# WEBSITES IN USER OVERLAPS ###################################")
        overlap_urls = collections.defaultdict(list)
        for user in users:
            for overlap in user.dynamic_overlaps:
                urls = []
                for dload in overlap.overlapping_starts:
                    if dload.url not in urls:
                        urls.append(dload.url)
                if urls:
                    overlap_urls[user.id].append(f"  Overlap URL: {dload.url}")
        print_results(self, overlap_urls)
    
    # Fix
    def avg_overlap_time(self, users):
        """Determines the average overlap time per user."""
        print("\n############################ AVERAGE OVERLAP PER USER ####################################")
        avg_overlap_times = collections.defaultdict(list)
        for user in users:
            overlap_times = []
            for overlap in user.overlaps:
                overlap_times.append(overlap.overlap_log.timestamp - overlap.start.timestamp)
            if overlap_times:
                avg_overlap_times[user.id].append(f"  Average overlap time: {sum(overlap_times) / len(overlap_times)}ms")
        print_results(self, avg_overlap_times)


class OverlapPrinter():
    """Prints User Overlaps."""

    def __init__(self, users):
        self._users = users
    
    def print_overlaps_for_starts(self, users):
        """Nicely prints all users' downloads that overlap with logs in other sessions that have status of 1."""
        print("\n#################### USER DOWNLOADS OVERLAPPING WITH STARTS ##########################")
        overlaps = collections.defaultdict(list)
        for user in users:
            if user.overlap_ones:
                print(f"\nUSER: {user.id}")
                for overlap in user.overlap_ones:
                    if overlap.overlapping_starts:
                        print(f"  START: {overlap.start}")
                        for log in overlap.overlapping_starts:
                            print(f"   Overlap: {log}")
                        print(f"  END:   {overlap.end}\n")
    
    def print_overlaps_for_dloads(self, users):
        """Nicely prints all users' downloads that overlap with download start logs in other sessions."""
        print("\n##################### USER DOWNLOADS OVERLAPPING WITH OTHER DOWNLOADS ########################")
        overlaps = collections.defaultdict(list)
        for user in users:
            if user.overlap_dloads:
                print(f"\nUSER: {user.id}")
                for overlap in user.overlap_dloads:
                    if overlap.overlapping_starts:
                        print(f"  START: {overlap.start}")
                        for dload in overlap.overlapping_starts:
                            print(f"   Overlap: {dload.start_log}")
                        print(f"  END:   {overlap.end}\n")

    def print_dynamic_overlaps(self, users):
        """Nicely prints overlap starting and ending among the sequence of a users' logs."""
        print("\n############################# USER OVERLAP STARTS AND ENDS ##################################")
        overlaps = collections.defaultdict(list)
        for user in users:
            if user.dynamic_overlaps:
                print(f"\nUSER: {user.id}")
                for overlap in user.dynamic_overlaps:
                    if overlap.overlapping_starts:
                        print(f"  OVERLAP START: {overlap.start.start}")
                        for dload in overlap.overlapping_starts:
                            print(f"   Overlapping log: {dload.start} {dload.end}")
                        print(f"  OVERLAP END:   {overlap.end.end}\n")



def print_results(self, dct):
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
        session.get_avg_dload_times()

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
        user.get_starts()
        user.get_dloads()
        #user.get_static_overlaps() # Need to add threading
        user.get_dynamic_overlaps()

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

    t = TimelineAnalyzer(users)
    d = DownloadAnalyzer(users)
    w = WebsiteAnalyzer(users)
    o = OverlapAnalyzer(users)
    p = OverlapPrinter(users)

    # To-Do: change function calls to args

    #t.timeline(users) 
    #d.avg_url_dload_time_per_user_sessions(users)
    #d.avg_url_dload_time_per_user(users)

    #w.num_unique_websites_per_user(users)

    o.number_dynamic_overlaps(users)
    o.websites_in_dynamic_overlaps(users)
    #o.avg_overlap_time(users)

    #p.print_overlaps_for_starts(users)
    #p.print_overlaps_for_dloads(users)
    p.print_dynamic_overlaps(users)


    return 0

if __name__ == "__main__":
    main()
