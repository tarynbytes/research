
from download import Download

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

