class Overlap():
    """An Overlap is defined as where one website is still downloading while a second one starts downloading."""

    def __init__(self, user, start, overlapping_starts, end):
        self._user = user
        self._start = start
        self._overlapping_starts = overlapping_starts
        self._end = end
        self._overlap_start = None
        self._overlap_end = None
        self._urls = []
        self._unique_urls = []
        self._duration = None
        self._time_before_overlap_starts = None
        self._num_urls = 0
        self._overlapped_url = None
        self._overlapping_url = None


    def get_overlap_start(self):
        self._overlap_start = self._overlapping_starts[0].start

    def get_overlap_end(self):
        ends = sorted(self._overlapping_starts, key=lambda val: (val.end))
        endslist = [end.end for end in ends]
        self._overlap_end = endslist[-2]

    def get_duration(self):
        self._duration = self._overlap_end - self._overlap_start

    def get_time_before_overlap_starts(self):
        if 2 <= len(self._overlapping_starts):
            self._time_before_overlap_starts = self._overlap_start - self._start.start

    def get_overlapped_url(self):
        self._overlapped_url = self.start.url

    def get_overlapping_url(self):
        self._overlapping_url = self._overlapping_starts[0].url

    def get_urls(self):
        self._urls.append(self._start.url)
        for dload in self._overlapping_starts:
            self._urls.append(dload.url)
        self._urls.append(self._end.url)
        self._unique_urls = list(dict.fromkeys(self._urls))

    def get_num_urls(self):
        percentages = []
        first_dload_percent = (self._start.end - self._overlap_start) / self._duration
        percentages.append(first_dload_percent)
        
        overlapping_log_percents = []
        for dload in self._overlapping_starts:
            if dload.end <= self._overlap_end:
                percent = (dload.end - dload.start) / self._duration
            elif dload.end > self._overlap_end:
                percent = (self._overlap_end - dload.start) / self._duration
            else:
                continue
            overlapping_log_percents.append(percent)
        percentages.extend(overlapping_log_percents)

        self._num_urls = round((sum(percentages) / len(percentages)) * 100, 2)

    @property
    def start(self):
        return self._start
    @property
    def overlap_start(self):
        return self._overlap_start
    @property
    def overlapping_starts(self):
        return self._overlapping_starts
    @property
    def end(self):
        return self._end
    @property
    def overlap_end(self):
        return self._overlap_end
    @property
    def urls(self):
        return self._urls
    @property
    def unique_urls(self):
        return self._unique_urls
    @property
    def duration(self):
        return self._duration
    @property
    def time_before_overlap_starts(self):
        return self._time_before_overlap_starts
    @property
    def num_urls(self):
        return self._num_urls
    @property
    def overlapping_url(self):
        return self._overlapping_url
    @property
    def overlapped_url(self):
        return self._overlapped_url

