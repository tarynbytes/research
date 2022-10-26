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

