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
        self._duration = None
        self._overlapping_url = self._overlapping_starts[1].url
        self._time_before_overlap_starts = None
        self._num_urls = 0

    def get_urls(self):
        self._urls = [log.url for log in self._overlapping_starts if log.url not in self._urls]

    def get_overlap_start(self):
        self._overlap_start = self._overlapping_starts[1].start

    def get_overlap_end(self):
        ends = sorted(self._overlapping_starts, key=lambda val: (val.end))
        endslist = [end.end for end in ends]
        self._overlap_end = self._end.end - endslist[-2]

    def get_duration(self):
        self._duration = self._overlap_end - self._overlap_start

    def get_time_before_overlap_starts(self):
        if 2 <= len(self._overlapping_starts):
            self._time_before_overlap_starts = self._overlap_start - self._start.start

    def get_num_urls(self):
        if 2 <= len(self._overlapping_starts):
            num_active = []
            num = 0
            for log in self._overlapping_starts:
                pass
            '''
            for ms in range(self._start.start, self._end.end + 1):
                changed = False
                for log in self._overlapping_starts:
                    if log.start == ms:
                        num += 1
                        num_active.append({num : ms})
                        changed = True
                    if log.end == ms:
                        num -= 1
                        num_active.append({num : ms})
                        changed = True
                if changed:
                    print(num_active)
            #self._num_urls.append(sum(num_active / len(urls)))
            '''

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
    def overlapping_url(self):
        return self._overlapping_url
    @property
    def urls(self):
        return self._urls
    @property
    def duration(self):
        return self._duration
    @property
    def time_before_overlap_starts(self):
        return self._time_before_overlap_starts
    @property
    def num_urls(self):
        return self._num_urls


