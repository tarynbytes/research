import collections
from numpy import mean
from statistics import mode


class Totals():
    """Pulls total data amongst users."""

    def __init__(self, users):
        self._users = users
        self._overlaps = []
        self._all_urls_in_overlaps = []
        self._overlapping_urls = []

        self._url_is_involved_in_an_overlap = {}
        self._url_begins_an_overlap = {}
        self._avg_dload_time_per_url = {}
        self._num_times_dloaded_per_url = {}

        self._avg_overlap_duration = 0
        self._avg_time_before_overlap_starts = 0
        self._avg_time_between_overlaps = 0
        self._avg_num_urls_per_overlaps = 0
        self._most_common_url_that_begins_an_overlap = None

    def get_overlaps(self):
        for user in self._users:
            if 0 < len(user.overlaps):
                for overlap in user.overlaps:
                    self._overlaps.append(overlap)

    def get_all_urls_in_overlaps(self):
        for overlap in self._overlaps:
            for url in overlap.unique_urls:
                if url not in self._all_urls_in_overlaps:
                    self._all_urls_in_overlaps.append(url)
    
    def get_overlapping_urls(self):
        for overlap in self._overlaps:
            self._overlapping_urls.append(overlap.overlapping_url)

    def get_avg_dload_time_per_url(self):
        for user in self._users:
            for url in user.urls_visited:
                avg_times = collections.defaultdict(list)
                for session in user.sessions:
                    if url == session.url and session.avg_dload_time != None:
                        avg_times[url].append(session.avg_dload_time / 1000 ) # convert ms to secs

                for url, times in avg_times.items():
                    dct = {url : round(mean(times), 2)}
                    self._avg_dload_time_per_url.update(dct)

    def get_num_times_dloaded_per_url(self):
        for user in self._users:
            num_times = collections.defaultdict(list)
            for session in user.sessions:
                num = len(session.downloads)
                num_times[session.url].append(num)

            for url, times in num_times.items():
                dct = {url : sum(times)}
                self._num_times_dloaded_per_url.update(dct)
    
    def get_url_begins_an_overlap(self):
        for user in self._users:
            for log in user.logs:
                if log.url in self._overlapping_urls:
                    dct = {log.url: "yes"}
                    if dct not in self._url_begins_an_overlap.items():
                        self._url_begins_an_overlap.update(dct)
    
    def get_url_is_involved_in_an_overlap(self):
        for user in self._users:
            for log in user.logs:
                if log.url in self._all_urls_in_overlaps:
                    dct = {log.url: "yes"}
                    if dct not in self._url_is_involved_in_an_overlap.items():
                        self._url_is_involved_in_an_overlap.update(dct)

    def get_most_common_url_that_begins_an_overlap(self):
        self._most_common_url_that_begins_an_overlap = mode(self._overlapping_urls)


    def get_avg_overlap_duration(self):
        durations = []
        for overlap in self._overlaps:
            durations.append(overlap.duration)
        self._avg_overlap_duration = round((sum(durations) / len(durations)), 2)

    def get_avg_time_before_overlap_starts(self):
        durations = []
        for overlap in self._overlaps:
            durations.append(overlap.time_before_overlap_starts)
        self._avg_time_before_overlap_starts = round((sum(durations) / len(durations)), 2)

    def get_avg_time_between_overlaps(self):
        durations = []
        for user in self._users:
            if 0 < len(user.overlaps):
                if user.avg_time_between_overlaps is not None:
                    durations.append(user.avg_time_between_overlaps)
        if 0 < len(durations):
            self._avg_time_between_overlaps = round((sum(durations) / len(durations)), 2)
    
    def get_avg_num_urls_per_overlaps(self):
        avg_nums = []
        for overlap in self._overlaps:
            avg_nums.append(overlap.num_urls)
        self._avg_num_urls_per_overlaps = round((sum(avg_nums) / len(avg_nums)), 2)


    @property
    def overlaps(self):
        return self._overlaps
    @property
    def all_urls_in_overlaps(self):
        return self._all_urls_in_overlaps
    @property
    def overlapping_urls(self):
        return self._overlapping_urls

    @property
    def avg_dload_time_per_url(self):
        return self._avg_dload_time_per_url
    @property
    def num_times_dloaded_per_url(self):
        return self._num_times_dloaded_per_url
    @property
    def url_is_involved_in_an_overlap(self):
        return self._url_is_involved_in_an_overlap
    @property
    def url_begins_an_overlap(self):
        return self._url_begins_an_overlap

    @property
    def avg_overlap_duration(self):
        return self._avg_overlap_duration
    @property
    def avg_time_before_overlap_starts(self):
        return self._avg_time_before_overlap_starts
    @property
    def avg_time_between_overlaps(self):
        return self._avg_time_between_overlaps
    @property
    def avg_num_urls_per_overlaps(self):
        return self._avg_num_urls_per_overlaps
    @property
    def most_common_url_that_begins_an_overlap(self):
        return self._most_common_url_that_begins_an_overlap


