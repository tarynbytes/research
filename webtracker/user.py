from overlap import Overlap
from statistics import multimode, mode
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
        self._urls_per_overlap = []
        self._urls_per_overlaps = []
        self._num_urls_per_overlap = []
        self._avg_num_urls_per_overlaps = []
        self._overlapping_url_per_overlap = []
        self._most_common_overlapping_url_per_overlaps = None
        self._overlap_time = []
        self._avg_overlap_time = None
        self._avg_time_between_overlaps = None
        self._time_before_overlap_starts_per_overlap = []
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
        idx = 0
        odict = {}
        prev_overlaps = {}
        try:
            start_dload = self._dloads[idx]
            while True:
                try:
                    
                    end_dload = self._dloads[idx]
                    curr_overlaps = {}
                    greatest_end = 0
                    if start_dload not in odict:
                        d = {start_dload : start_dload.end}
                        odict.update(d)

                    for dload in self._dloads[idx:]:
                        if start_dload.start < dload.start <= end_dload.end:
                            curr_overlaps[dload] = dload.end
                        
                    if 2 > len(prev_overlaps) and 2 > len(curr_overlaps): # No previous and no current
                        if idx == len(self._dloads) -1:
                            break
                        if idx != len(self._dloads) -1:
                            prev_overlaps = copy.deepcopy(curr_overlaps)
                            idx += 1

                    elif 2 > len(prev_overlaps) and 2 <= len(curr_overlaps): # No previous but current
                        if idx != len(self._dloads) -1:
                            for item in curr_overlaps:
                                if item not in odict:
                                    odict.update(curr_overlaps)
                            prev_overlaps = copy.deepcopy(curr_overlaps)
                            greatest_end = max(curr_overlaps.values())
                            target_dload = list(curr_overlaps.keys())[list(curr_overlaps.values()).index(greatest_end)]
                            if greatest_end == start_dload.end:
                                idx = self._dloads.index(target_dload) + 1
                            if greatest_end != start_dload.end:
                                idx = self._dloads.index(target_dload)
                        if idx == len(self._dloads) -1:
                            self._overlaps.append(Overlap(self, start_dload, list(odict.keys()), target_dload))
                            odict = {}

                    elif 2 <= len(prev_overlaps) and 2 > len(curr_overlaps): # Previous but no current
                        if idx == len(self._dloads) -1:
                            self._overlaps.append(Overlap(self, start_dload, list(odict.keys()), target_dload))
                            break
                        if idx != len(self._dloads) -1:
                            self._overlaps.append(Overlap(self, start_dload, list(odict.keys()), target_dload))
                            odict = {}
                            prev_overlaps = copy.deepcopy(curr_overlaps)
                            idx += 1
                            start_dload = self._dloads[idx]

                    else: # 2 <= len(prev_overlaps) and 2 <= len(curr_overlaps): # Both previous and current
                        if idx == len(self._dloads) -1:
                            self._overlaps.append(Overlap(self, start_dload, list(odict.keys()), target_dload))
                            break
                        if idx != len(self._dloads) -1:
                            for item in curr_overlaps:
                                if item not in odict:
                                    odict.update(curr_overlaps)
                            prev_overlaps = copy.deepcopy(curr_overlaps)
                            greatest_end = max(curr_overlaps.values())
                            target_dload = list(curr_overlaps.keys())[list(curr_overlaps.values()).index(greatest_end)]
                            if greatest_end == start_dload.end:
                                idx = self._dloads.index(target_dload) + 1
                            if greatest_end != start_dload.end:
                                idx = self._dloads.index(target_dload)
                except IndexError:
                    break
        except IndexError:
            pass

    def get_percent_overlaps(self):
        if 0 < len(self._overlaps):
            overlap_logs = 0
            for overlap in self._overlaps:
                overlap_logs += len(overlap.overlapping_starts)
            self._percent_overlaps = round((overlap_logs / len(self._logs) *100), 2)

    def get_num_urls_per_overlap(self):
        if 0 < len(self._overlaps):
            for i, overlap in enumerate(self._overlaps):
                dct = {f"Overlap" : i+1, "Number URLs" : overlap.num_urls}
                self._num_urls_per_overlap.append(dct)
        
    def get_avg_num_urls_per_overlaps(self):
        if 0 < len(self._overlaps):
            self._avg_num_urls_per_overlaps = round((sum(overlap.num_urls for overlap in self._overlaps) / len(self._overlaps)), 2)

    def get_overlapping_url_per_overlap(self):
        if 0 < len(self._overlaps):
            for i, overlap in enumerate(self._overlaps):
                dct = {f"Overlap" : i+1, "Overlapping URL" : overlap.overlapping_url}
                self._overlapping_url_per_overlap.append(dct)

    def get_most_common_overlapping_url_per_overlaps(self):
        if 0 < len(self._overlaps):
            self._most_common_overlapping_url_per_overlaps = mode([lst[1] for lst in [list(dct.values()) for dct in self._overlapping_url_per_overlap]])

    def get_urls_per_overlap(self):
        for i, overlap in enumerate(self._overlaps):
            if overlap.urls is not None:
                dct = {f"Overlap" : i+1, "URLs" : overlap.urls}
                self._urls_per_overlap.append(dct)

    def get_urls_per_overlaps(self):
        for overlap in self._overlaps:
            self._urls_per_overlaps = [url for url in overlap.urls if url not in self._urls_per_overlaps]

    def get_overlap_time(self):
        if 0 < len(self._overlaps):
            for i, overlap in enumerate(self._overlaps):
                dct = {f"Overlap" : i+1, "Duration" : overlap.duration}
                self._overlap_time.append(dct)

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
                time_between_overlaps.append(self.overlaps[idx+1].overlap_start - self.overlaps[idx].overlap_end)
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
    def num_urls_per_overlap(self):
        return self._num_urls_per_overlap
    @property
    def avg_num_urls_per_overlaps(self):
        return self._avg_num_urls_per_overlaps
    @property
    def overlapping_url_per_overlap(self):
        return self._overlapping_url_per_overlap
    @property
    def most_common_overlapping_url_per_overlaps(self):
        return self._most_common_overlapping_url_per_overlaps
    @property
    def urls_per_overlap(self):
        return self._urls_per_overlap
    @property
    def urls_per_overlaps(self):
        return self._urls_per_overlaps
    @property
    def overlap_time(self):
        return self._overlap_time
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
    @property
    def visualized_overlaps(self):
        return self._visualized_overlaps
