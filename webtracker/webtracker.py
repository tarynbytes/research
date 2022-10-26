from log import Log
from user import User
from session import Session
from graph import Graph
from argparse import ArgumentParser
import re
import collections
from tqdm import tqdm
from dash import Dash
import multiprocessing

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def generate_user_info(logs):
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
            overlap.get_overlap_start()
            overlap.get_overlap_end()
            overlap.get_duration()
            overlap.get_time_before_overlap_starts()
            overlap.get_num_urls()
        user.get_percent_overlaps()
        user.get_overlap_time()
        user.get_avg_overlap_time()
        user.get_urls_per_overlap()
        user.get_urls_per_overlaps()

        #user.get_num_urls_per_overlap()
        #user.get_avg_num_urls_per_overlaps()
            
        user.get_overlapping_url_per_overlap()
        user.get_most_common_overlapping_url_per_overlaps()
        user.get_avg_time_between_overlaps()
        user.get_time_before_overlap_starts_per_overlap()
        user.get_avg_time_before_overlap_starts()

        #print("   Getting visualized overlaps...")
        #user.get_visualized_overlaps()
        #print_overlaps(user)

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
    users = generate_user_info(logs)

    fields = ['user', 'num_logs', 'browsing_time', 'num_sessions', 'avg_session_time', 'avg_dload_time_per_session', 'num_dloads', 'percent_dloads',
        'urls_in_dloads', 'num_urls_visited', 'urls_visited', 'avg_dload_time_per_url', 'num_overlaps', 'percent_overlaps', 'overlap_time',
        'avg_overlap_time', 'urls_per_overlap', 'urls_per_overlaps', 'num_urls_per_overlap', 'avg_num_urls_per_overlaps', 'overlapping_url_per_overlap',
        'most_common_overlapping_url_per_overlaps', 'avg_time_between_overlaps', 'time_before_overlap_starts_per_overlap', 'avg_time_before_overlap_starts', 'visualized_overlaps']

    rows = []
    for user in tqdm(users, desc='Populating CSV'):
        dct = {

            # User info
            "user" : user.id, # ------------------------------------------------------------------------- # User ID
            "num_logs" : len(user.logs), # -------------------------------------------------------------- # How many logs per user
            "browsing_time" : user.browsing_time, # ----------------------------------------------------- # Duration of first timestamp to last timestamp of user logs

            # Session info
            "num_sessions" : len(user.sessions), # ------------------------------------------------------ # How many sessions per user (logs with same URL and TABID)
            "avg_session_time" : user.avg_session_time, # ------------------------------------------------# Average time a session lasts
            "avg_dload_time_per_session" : user.avg_dload_time_per_session, # --------------------------- # Average download time per session

            # Download info
            "num_dloads" : len(user.dloads), # ---------------------------------------------------------- # How many downloads per user (status 1 log with corresponding status 2 log)
            "percent_dloads" : user.percent_dloads, # --------------------------------------------------- # What percent of user logs are downloads
            "urls_in_dloads" : user._urls_in_dloads, # -------------------------------------------------- # The unique URLs involved in a download

            # URL info
            "num_urls_visited" : len(user.urls_visited), # ---------------------------------------------- # Number of unique websites visited per user
            "urls_visited" : user.urls_visited, # --------------------------------------------------------# The URL hashes of unique websites visited per user
            "avg_dload_time_per_url" : user.avg_dload_time_per_url, # ----------------------------------- # Average download time per unique url

            # Overlap info
            "num_overlaps" : len(user.overlaps), # ------------------------------------------------------ # Number of user overlaps
            "percent_overlaps" : user.percent_overlaps, # ----------------------------------------------- # What percent of user logs are involved in an overlap
            "overlap_time" : user.overlap_time, # ------------------------------------------------------- # Time an overlap lasts
            "avg_overlap_time" : user.avg_overlap_time, # ----------------------------------------------- # Average time an overlap lasts
            "urls_per_overlap" : user.urls_per_overlap, # ----------------------------------------------- # Unique websites involved per overlap
            "urls_per_overlaps" : user.urls_per_overlaps, # --------------------------------------------- # Unique websites in all overlaps combined
            "num_urls_per_overlap" : user.num_urls_per_overlap, # --------------------------------------- # Number of URLs per overlap in format such as (2 + 3 + 2)/3 = 2.33.
            "avg_num_urls_per_overlaps" : user.avg_num_urls_per_overlaps, # ----------------------------- # Gets average number of URLs per overlaps combined
            "overlapping_url_per_overlap" : user.overlapping_url_per_overlap,  # ------------------------ # The URL that first creates an overlap per overlap
            "most_common_overlapping_url_per_overlaps" : user.most_common_overlapping_url_per_overlaps,   # The average URL that creates overlap
            "avg_time_between_overlaps" : user.avg_time_between_overlaps, # ----------------------------- # Average time between end and start of a new overlap
            "time_before_overlap_starts_per_overlap" : user.time_before_overlap_starts_per_overlap, # --- # The time before overlap starts for each overlap
            "avg_time_before_overlap_starts" : user.avg_time_before_overlap_starts, # ------------------- # The average time before overlap starts for all overlaps combined
            "visualized_overlaps" : user.visualized_overlaps # ------------------------------------------ # Visualizable histogram of overlap intervals
        }
        rows.append(dct)

    # TODO:
    # overlap.num_urls
    # visualized_overlaps

    
    app = Dash(__name__, external_stylesheets=external_stylesheets)
    data = Graph(users, fields, rows, "bigdata.csv", app)
    data.create_csv()
    data.get_df()
    data.get_default_figures()
    data.get_graphs()
    data.init_app()

    app.run_server(dev_tools_hot_reload=False)
    #app.run_server(debug=True)
    
    return 0

if __name__ == "__main__":
    main()
