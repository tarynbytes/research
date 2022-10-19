from argparse import ArgumentParser
import re
import hashlib
import collections
import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tqdm import tqdm
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


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
        self._browsing_time = None
        self._starts = []
        self._urls_visited = []
        self._dloads = []
        self._urls_in_dloads = []
        self._percent_dloads = None
        self._avg_dload_time_per_session = []
        self._avg_session_time = None
        self._avg_dload_time_per_url = []
        self._overlaps = []
        self._percent_overlaps = None
        self._urls_in_overlaps = []
        self._urls_per_overlap = []
        self._avg_overlap_time = None
        self._avg_time_between_overlaps = None
        self._time_before_overlap_starts_per_overlap = []
        self._avg_time_before_overlap_starts = None


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

    def get_browsing_time(self):
        self._browsing_time = max(log.timestamp for log in self._logs) - min(log.timestamp for log in self._logs)

    def get_starts(self):
        for session in self._sessions:
            for log in session._session_logs:
                if 1 == log.status:
                    self._starts.append(log)

    def get_all_urls_visited(self):
        for session in self._sessions:
            if session.url not in self._urls_visited:
                self._urls_visited.append(session.url)

    def get_dloads(self):
        for session in self._sessions:
            for download in session.downloads:
                self._dloads.append(download)
        self._dloads = sorted(self._dloads, key=lambda val: (val.end, val.start))

    def get_percent_dloads(self):
        if 0 < len(self._dloads):
            self._percent_dloads = round((len(self._dloads) *2 / len(self._logs) *100), 2)

    def get_urls_in_dloads(self):
        self._urls_in_dloads = [dload.url for dload in self._dloads if dload.url not in self._urls_in_dloads]

    def get_avg_dload_time_per_session(self):
        for session in self._sessions:
            if session.avg_dload_time is not None:
                dct = {"Session Hash" : session.hash, "Average dload time" : round((session.avg_dload_time), 2)}
                self._avg_dload_time_per_session.append(dct)

    def get_avg_session_time(self):
        if 0 < len(self._sessions):
            self._avg_session_time = round((sum(session.duration for session in self._sessions) / len(self._sessions)), 2)

    def get_avg_dload_time_per_url(self):
        for url in self._urls_visited:
            avg_times = collections.defaultdict(list)
            for session in self._sessions:
                if session.avg_dload_time is not None:
                    if url == session.url:
                        avg_times[url].append(session.avg_dload_time)
            for url, times in avg_times.items():
                dct = {"URL" : url, "Average dload time" : round((sum(times) / len(times)), 2)}
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
                    self._overlaps.append(Overlap(self, start_dload, sorted(list(overlaps.keys()), key=lambda val: (val.start)), target_dload))

                    idx = self._dloads.index(target_dload)

                else:
                    idx += 1

                if greatest_end == last_end or idx == len(self._dloads) - 1:
                    break

            except IndexError:
                break


    def get_percent_overlaps(self):
        if 0 < len(self._overlaps):
            overlap_logs = 0
            for overlap in self._overlaps:
                overlap_logs += len(overlap.overlapping_starts)
            self._percent_overlaps = round((overlap_logs / len(self._logs) *100), 2)

    def get_urls_in_overlaps(self):
        for overlap in self._overlaps:
            self._urls_in_overlaps = [url for url in overlap.urls if url not in self._urls_in_overlaps]

    def get_urls_per_overlap(self):
        for i, overlap in enumerate(self._overlaps):
            if overlap.urls is not None:
                dct = {f"Overlap" : i+1, "URLs" : overlap.urls}
                self._urls_per_overlap.append(dct)
    
    def get_avg_overlap_time(self):
        if 0 < len(self._overlaps):
            self._avg_overlap_time = round((sum(overlap.duration for overlap in self._overlaps) / len(self._overlaps)), 2)

    def get_avg_time_between_overlaps(self):
        time_between_overlaps = []
        idx = 0
        if 2 <= len(self._overlaps):
            while True:
                if idx == len(self.overlaps) - 1:
                    break
                time_between_overlaps.append(self.overlaps[idx+1].start.start - self.overlaps[idx].end.end)
                idx += 1
            self._avg_time_between_overlaps = round((sum(time_between_overlaps) / len(time_between_overlaps)), 2)
    
    def get_time_before_overlap_starts_per_overlap(self):
        if 0 < len(self._overlaps):
            for i, overlap in enumerate(self._overlaps):
                dct = {f"Overlap" : i+1, "Time before overlap starts" : overlap.time_before_overlap_starts}
                self._time_before_overlap_starts_per_overlap.append(dct)

    def get_avg_time_before_overlap_starts(self):
        if 0 < len(self._overlaps):
            self._avg_time_before_overlap_starts = round((sum(overlap.time_before_overlap_starts for overlap in self._overlaps) / len(self._overlaps)), 2)


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
    def browsing_time(self):
        return self._browsing_time
    @property
    def starts(self):
        return self._starts
    @property
    def urls_visited(self):
        return self._urls_visited
    @property
    def dloads(self):
        return self._dloads
    @property
    def percent_dloads(self):
        return self._percent_dloads
    @property
    def urls_in_dloads(self):
        return self._urls_in_dloads
    @property
    def avg_dload_time_per_session(self):
        return self._avg_dload_time_per_session
    @property
    def avg_session_time(self):
        return self._avg_session_time
    @property
    def avg_dload_time_per_url(self):
        return self._avg_dload_time_per_url
    @property
    def overlaps(self):
        return self._overlaps
    @property
    def percent_overlaps(self):
        return self._percent_overlaps
    @property
    def urls_in_overlaps(self):
        return self._urls_in_overlaps
    @property
    def urls_per_overlap(self):
        return self._urls_per_overlap
    @property
    def avg_overlap_time(self):
        return self._avg_overlap_time
    @property
    def avg_time_between_overlaps(self):
        return self._avg_time_between_overlaps
    @property
    def time_before_overlap_starts_per_overlap(self):
        return self._time_before_overlap_starts_per_overlap
    @property
    def avg_time_before_overlap_starts(self):
        return self._avg_time_before_overlap_starts



class Overlap():
    """An Overlap is defined as where one website is still downloading while a second one starts downloading."""

    def __init__(self, user, start, overlapping_starts, end):
        self._user = user
        self._start = start
        self._overlapping_starts = overlapping_starts
        self._end = end
        self._urls = []
        self._duration = self._end.end - self._start.start
        self._time_before_overlap_starts = None

    def get_urls(self):
        self._urls = [log.url for log in self._overlapping_starts if log.url not in self._urls]

    def get_time_before_overlap_starts(self):
        if 2 <= len(self._overlapping_starts):
            self._time_before_overlap_starts = self._overlapping_starts[1].start - self._overlapping_starts[0].start

    @property
    def start(self):
        return self._start
    @property
    def overlapping_starts(self):
        return self._overlapping_starts
    @property
    def end(self):
        return self._end
    @property
    def urls(self):
        return self._urls
    @property
    def duration(self):
        return self._duration
    @property
    def time_before_overlap_starts(self):
        return self._time_before_overlap_starts



class Session():
    """Session objects are defined as a group of logs with the same userid, url, and tabid."""

    def __init__(self, session_id):
        self._session_id = session_id
        self._session_logs = []
        self.userid = None
        self.url = None
        self.tabid = None
        self._start = None
        self._end = None
        self._downloads = []
        self._avg_dload_time = None
        self._duration = None


    def sort_logs(self):
        self._session_logs = sorted(self._session_logs, key=lambda val: (val.userid, val.url, val.tabid, val.timestamp))
        self._start = self._session_logs[0].timestamp
        self._end = self._session_logs[-1].timestamp


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

    def get_duration(self):
         self._duration = self._end - self._start
    

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
    def end(self):
        return self._end
    @property
    def logs(self):
        return self._session_logs
    @property
    def hash(self):
        return self._session_id
    @property
    def avg_dload_time(self):
        return self._avg_dload_time
    @property
    def duration(self):
        return self._duration


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
        if (isinstance(download, Download)):
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


        

class Graph():
    """Creates data visualizations."""

    def __init__(self, users, fields, rows, csvfile, app):
        self._users = users
        self._fields = fields
        self._rows = rows
        self._csvfile = csvfile
        self._app = app
        self._df = pd.read_csv(self._csvfile)
        self._figlst = []

    def create_csv(self):
        with open(self._csvfile, 'w') as f:
            writer = csv.DictWriter(f, fieldnames = self._fields) 
            writer.writeheader() 
            writer.writerows(self._rows)

    def create_json(self):
        pass

    def get_figs(self):
        for field in tqdm(self._fields[1:], desc='Getting figs'):
            self._figlst.append(px.line(self._df, x='user', y=f'{field}'))

    def init_app(self):
        children = []
        for idx, fig in tqdm(enumerate(self._figlst), desc='Generating graphs'):
            children.append(html.Div(dcc.Graph(id=f'graph{idx}', figure=fig)))
        self._app.layout = html.Div(children)



def generate_user_sessions(logs):
    """ Initializes Session objects and returns a list of User objects [corresponding to Sessions]."""
    sessions = {}
    users = []

    for log in tqdm(logs, desc='Assigning logs to users'):
        if log.userid not in users:
            users.append(log.userid)
        try:
            sessions[log.session_hash].add_log(log)
        except Exception as e:
            sessions[log.session_hash] = Session(log.session_hash)
            sessions[log.session_hash].add_log(log)

    sessions = list(sessions.values())
    for session in tqdm(sessions, desc='Populating user sessions'):
        session.sort_logs()
        session.get_downloads()
        session.get_avg_dload_time()
        session.get_duration()

    user_dct = {}
    for user in users:
        session_lst = []
        for session in sessions:
            if user == session.userid:
                session_lst.append(session)
        user_dct[user] = User(session_lst, user)
    users = list(user_dct.values())

    for user in tqdm(users, desc='Populating user information'):
        user.get_logs()
        user.get_browsing_time()
        user.get_starts()
        user.get_all_urls_visited()
        user.get_dloads()
        user.get_percent_dloads()
        user.get_urls_in_dloads()
        user.get_avg_dload_time_per_session()
        user.get_avg_session_time()
        user.get_avg_dload_time_per_url()
        user.get_overlaps()
        for overlap in user.overlaps:
            overlap.get_urls()
            overlap.get_time_before_overlap_starts()
        user.get_percent_overlaps()
        user.get_urls_in_overlaps()
        user.get_urls_per_overlap()
        user.get_avg_overlap_time()
        user.get_avg_time_between_overlaps()
        user.get_time_before_overlap_starts_per_overlap()
        user.get_avg_time_before_overlap_starts()

    return users

def print_overlaps(user):
    overlaps = collections.defaultdict(list)
    if user.overlaps:
        print(f"\nUSER: {user.id}")
        for overlap in user.overlaps:
            if overlap.overlapping_starts:
                print(f"  OVERLAP START: {overlap.start.start}")
                for dload in overlap.overlapping_starts:
                    print(f"   Overlapping log: {dload.start} {dload.end}")
                print(f"  OVERLAP END:   {overlap.end.end}\n")

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

    fields = ['user', 'num_logs', 'num_sessions', 'browsing_time', 'num_dloads', 'percent_dloads', 'num_urls_visited', 'urls_visited', 'urls_in_dloads',
        'avg_dload_time_per_url', 'avg_dload_time_per_session', 'avg_session_time', 'num_overlaps', 'percent_overlaps', 'urls_in_overlaps', 'urls_per_overlap',
        'avg_overlap_time', 'avg_time_between_overlaps', 'time_before_overlap_starts_per_overlap', 'avg_time_before_overlap_starts']

    rows = []
    for user in tqdm(users, desc='Populating CSV'):
        dct = {
            "user" : user.id, # --------------------------------------------------------------------- # User ID
            "num_logs" : len(user.logs), # ---------------------------------------------------------- # How many logs per user
            "num_sessions" : len(user.sessions), # -------------------------------------------------- # How many sessions per user (logs with same URL and TABID)
            "browsing_time" : user.browsing_time, # ------------------------------------------------- # Duration of first timestamp to last timestamp of user logs
            "num_dloads" : len(user.dloads), # ------------------------------------------------------ # How many downloads per user (status 1 log with corresponding status 2 log)
            "percent_dloads" : user.percent_dloads, # ----------------------------------------------- # What percent of user logs are downloads
            "num_urls_visited" : len(user.urls_visited), # ------------------------------------------ # Number of unique websites visited per user
            "urls_visited" : user.urls_visited, # ----------------------------------------------------# The URL hashes of unique websites visited per user
            "urls_in_dloads" : user._urls_in_dloads, # ---------------------------------------------- # The unique URLs involved in a download

            "avg_dload_time_per_url" : user.avg_dload_time_per_url, # ------------------------------- # Average download time per unique url
            "avg_dload_time_per_session" : user.avg_dload_time_per_session, # ----------------------- # Average download time per session
            "avg_session_time" : user.avg_session_time, # --------------------------------------------# Average time a session lasts
            "num_overlaps" : len(user.overlaps), # -------------------------------------------------- # Number of user overlaps
            "percent_overlaps" : user.percent_overlaps, # ------------------------------------------- # What percent of user logs are involved in an overlap
            "urls_in_overlaps" : user.urls_in_overlaps, # ------------------------------------------- # Unique websites in all overlaps combined
            "urls_per_overlap" : user.urls_per_overlap, # ------------------------------------------- # Unique websites involved per overlap

            "avg_overlap_time" : user.avg_overlap_time, # ------------------------------------------- # Average time an overlap lasts
            "avg_time_between_overlaps" : user.avg_time_between_overlaps, # ------------------------- # Average time between end and start of a new overlap
            "time_before_overlap_starts_per_overlap" : user.time_before_overlap_starts_per_overlap, #-# the time before overlap starts for each overlap
            "avg_time_before_overlap_starts" : user.avg_time_before_overlap_starts # --------------- # the average time before overlap starts for all overlaps combined  
        }
            # TODO:
            # num urls_per_overlap --- Define such as (2 + 3 + 2)/3 = 2.33.
            # Sequential intervals of overlaps --> create via graph
            # first overlap url per overlap
            # avg first overlap url per overlaps


        rows.append(dct)

    app = Dash(__name__, external_stylesheets=external_stylesheets)

    data = Graph(users, fields, rows, "bigdata.csv", app)
    data.create_csv()
    data.get_figs()
    data.init_app()

    app.run_server(dev_tools_hot_reload=False)
    
    return 0

if __name__ == "__main__":
    main()
