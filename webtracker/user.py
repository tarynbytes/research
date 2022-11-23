from overlap import Overlap
from statistics import multimode, mode
from numpy import mean
import collections
import copy

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
        self._avg_num_urls_per_overlaps = []
        self._avg_overlap_time = None
        self._avg_time_between_overlaps = None
        self._avg_time_before_overlap_starts = None
        self._visualized_overlaps = None


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
        self._percent_dloads = (len(self._dloads) *2 / len(self._logs) *100)

    def get_urls_in_dloads(self):
        self._urls_in_dloads = [dload.url for dload in self._dloads if dload.url not in self._urls_in_dloads]

    def get_avg_dload_time_per_session(self):
        for session in self._sessions:
            if session.avg_dload_time is not None:
                dct = {"Session H_ash" : session.hash, "Average dload time" : session.avg_dload_time}
                self._avg_dload_time_per_session.append(dct)

    def get_avg_session_time(self):
        if 0 < len(self._sessions):
            self._avg_session_time = (sum(session.duration for session in self._sessions) / len(self._sessions))

    def get_avg_dload_time_per_url(self):
        for url in self._urls_visited:
            avg_times = collections.defaultdict(list)
            for session in self._sessions:
                if url == session.url and session.avg_dload_time != None: # changed this conditional a little
                        avg_times[url].append(session.avg_dload_time)

            for url, times in avg_times.items():
                dct = {"URL" : url, "Average dload time" : mean(times)}
                self._avg_dload_time_per_url.append(dct)

    
    def get_overlaps(self):

        idx = 0
        prev_overlaps = {}
        total_overlaps = {}
 
        try:
            starting_dload = self._dloads[idx]
            ending_dload = self._dloads[idx]
            greatest_end = starting_dload.end

            while True:

                try:
                    curr_overlaps = {}

                    for dload in self._dloads[idx +1:]:
                        if starting_dload.start < dload.start <= ending_dload.end:
                            curr_overlaps[dload] = dload.end
                        
                    if 2 > len(prev_overlaps) and 2 > len(curr_overlaps): # No previous and no current
                        if idx == len(self._dloads) - 1:
                            break
                        else: # idx != len(self._dloads) - 1:
                            idx += 1
                            starting_dload = self._dloads[idx]
                            ending_dload = self._dloads[idx]

                    elif 2 > len(prev_overlaps) and 2 <= len(curr_overlaps): # No previous but current
                        greatest_end = max(curr_overlaps.values())
                        i = len(list(curr_overlaps.values())) - list(curr_overlaps.values())[::-1].index(greatest_end) - 1 # last occurence of max value
                        target_dload = list(curr_overlaps.keys())[i]

                        if idx == len(self._dloads) - 1:
                            self._overlaps.append(Overlap(self, starting_dload, list(total_overlaps.keys()), target_dload))  
                            break
                        else: # idx != len(self._dloads) - 1:
                            for dload in curr_overlaps:
                                if dload not in total_overlaps:
                                    total_overlaps[dload] = dload.end
                            idx += 1
                            ending_dload = self._dloads[idx]

                    elif 2 <= len(prev_overlaps) and 2 > len(curr_overlaps): # Previous but no current
                        greatest_end = max(total_overlaps.values())
                        i = len(list(total_overlaps.values())) - list(total_overlaps.values())[::-1].index(greatest_end) - 1
                        target_dload = list(total_overlaps.keys())[i]
                        self._overlaps.append(Overlap(self, starting_dload, list(total_overlaps.keys()), target_dload))

                        if idx == len(self._dloads) - 1:
                            break
                        else: # idx != len(self._dloads) - 1:
                            total_overlaps.clear()
                            idx += 1
                            starting_dload = self._dloads[idx]

                    elif 2 <= len(prev_overlaps) and 2 <= len(curr_overlaps): # Both previous and current:
                        greatest_end = max(total_overlaps.values())
                        i = len(list(total_overlaps.values())) - list(total_overlaps.values())[::-1].index(greatest_end) - 1 # last occurence of max value
                        target_dload = list(total_overlaps.keys())[i]
                        
                        if idx == len(self._dloads) - 1:                
                            self._overlaps.append(Overlap(self, starting_dload, list(total_overlaps.keys()), target_dload))
                            break
                        else: # idx != len(self._dloads) - 1:
                            for dload in curr_overlaps:
                                if dload not in total_overlaps:
                                    total_overlaps[dload] = dload.end
                            idx += 1
                            ending_dload = self._dloads[idx]

                    prev_overlaps = copy.deepcopy(curr_overlaps)

                except IndexError:
                    break
        except IndexError:
            pass
    
    
    def get_percent_overlaps(self):
        overlap_logs = 0
        for overlap in self._overlaps:
            overlap_logs += len(overlap.overlapping_starts) + 1
        self._percent_overlaps = (overlap_logs / len(self._logs) *100)

    def get_avg_num_urls_per_overlaps(self): 
        self._avg_num_urls_per_overlaps = (sum(overlap.num_urls for overlap in self._overlaps) / len(self._overlaps))

    def get_avg_overlap_time(self):
        self._avg_overlap_time = (sum(overlap.duration for overlap in self._overlaps) / len(self._overlaps))

    def get_avg_time_between_overlaps(self):
        times_between_overlaps = []
        idx = 0
        if 2 <= len(self._overlaps):
            while True:
                if idx == len(self._overlaps) - 1:
                    break
                times_between_overlaps.append(self._overlaps[idx+1].overlap_start - self._overlaps[idx].overlap_end)
                idx += 1
            self._avg_time_between_overlaps = (sum(times_between_overlaps) / len(times_between_overlaps))

    def get_avg_time_before_overlap_starts(self):
        self._avg_time_before_overlap_starts = (sum(overlap.time_before_overlap_starts for overlap in self._overlaps) / len(self._overlaps))
    
    def get_visualized_overlaps(self):
        pass

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
    def avg_num_urls_per_overlaps(self):
        return self._avg_num_urls_per_overlaps
    @property
    def avg_overlap_time(self):
        return self._avg_overlap_time
    @property
    def avg_time_between_overlaps(self):
        return self._avg_time_between_overlaps
    @property
    def avg_time_before_overlap_starts(self):
        return self._avg_time_before_overlap_starts
    @property
    def visualized_overlaps(self):
        return self._visualized_overlaps
