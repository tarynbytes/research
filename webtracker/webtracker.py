from log import Log
from user import User
from session import Session
from totals import Totals
from graph import Graph
from argparse import ArgumentParser
import re
import collections
from collections import defaultdict
from tqdm import tqdm
from dash import Dash
from multiprocessing import Process, cpu_count, Manager
import copy

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def get_sublists(original_list, number_of_sub_list_wanted):
    sublists = list()
    for sub_list_count in range(number_of_sub_list_wanted): 
        sublists.append(original_list[sub_list_count::number_of_sub_list_wanted])
    return copy.deepcopy(sublists)


def generate_user_logs(logs):
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

    num_proc = cpu_count()
    print(f"CPU Count: {num_proc}")
    users_manager = Manager()
    ret_users = users_manager.list()
    procs = []

    sub_users = get_sublists(users, num_proc)

    for sub_user in sub_users:
        proc = Process(target=generate_user_info, args=(sub_user, ret_users))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()

    print("Processes Joined")
        
    return ret_users


def generate_user_info(users, ret_users):
    for user in tqdm(users, desc='Populating user information'):
        user.get_logs()
        user.get_browsing_time()
        user.get_starts()
        user.get_all_urls_visited()
        user.get_dloads()
        user.get_avg_dload_time_per_session()
        user.get_avg_session_time()
        if 0 < len(user.dloads):
            user.get_percent_dloads()
            user.get_urls_in_dloads()
            user.get_overlaps()
            for dload in user.dloads:
                dload.get_duration()
        if 0 < len(user.overlaps):
            for overlap in user.overlaps:
                overlap.get_overlap_start()
                overlap.get_overlap_end()
                overlap.get_duration()
                overlap.get_time_before_overlap_starts()
                overlap.get_overlapping_url()
                overlap.get_overlapped_url()
                overlap.get_urls()
                overlap.get_num_urls()
            user.get_percent_overlaps()
            user.get_avg_overlap_time()
            user.get_avg_num_urls_per_overlaps()
            user.get_avg_time_between_overlaps()
            user.get_avg_time_before_overlap_starts()
            #print("   Getting visualized overlaps...")
            #user.get_visualized_overlaps()

        #print_overlaps(user)

    ret_users.extend(users)

def print_overlaps(user):
    overlaps = collections.defaultdict(list)
    if user.overlaps:
        print(f"\nUSER: {user.id}")
        for overlap in user.overlaps:
            if overlap.overlapping_starts:
                print(f"  OVERLAP START: {overlap.start.start} {overlap.start.end} {overlap.start.url}")
                for dload in overlap.overlapping_starts:
                    print(f"   Overlapping log: {dload.start} {dload.end} {dload.url}")
                print(f"  OVERLAP END:   {overlap.end.start} {overlap.end.end} {overlap.end.url}\n")

def get_user_axes(users):
    user_fields = ['user', 'num_logs', 'browsing_time (hrs)', 'num_sessions', 'avg_session_time (hrs)', 'num_dloads', 'percent_dloads',
        'num_urls_visited', 'num_overlaps', 'percent_overlaps', 'avg_overlap_duration (secs)', 'avg_time_between_overlaps (mins)', 'avg_num_urls_per_overlap']

    user_rows = []
    for user in tqdm(users, desc='Populating user data CSV'):
        user_dct = {

            "user" : user.id, # -------------------------------------------------------------------------- # User ID
            "num_logs" : len(user.logs), # --------------------------------------------------------------- # How many logs per user
            "browsing_time (hrs)" : ms_to_hours(user.browsing_time), # ----------------------------------- # Duration of first timestamp to last timestamp of user logs
            "num_sessions" : len(user.sessions), # ------------------------------------------------------- # How many sessions per user (logs with same URL and TABID)
            "avg_session_time (hrs)" : ms_to_hours(user.avg_session_time), # ------------------------------# Average time a session lasts
            "num_dloads" : len(user.dloads), # ----------------------------------------------------------- # How many downloads per user (status 1 log with corresponding status 2 log)
            "percent_dloads" : user.percent_dloads, # ---------------------------------------------------- # What percent of user logs are downloads
            "num_urls_visited" : len(user.urls_visited), # ----------------------------------------------- # Number of unique websites visited per user
            "num_overlaps" : len(user.overlaps), # ------------------------------------------------------- # Number of overlaps per user
            "percent_overlaps" : user.percent_overlaps, # ------------------------------------------------ # What percent of user logs involve an overlap
            "avg_overlap_duration (secs)" : ms_to_seconds(user.avg_overlap_time), # ---------------------- # Average time an overlap lasts
            "avg_time_between_overlaps (mins)" : ms_to_minutes(user.avg_time_between_overlaps), # -------- # Average time between overlaps
            "avg_num_urls_per_overlap" : user.avg_num_urls_per_overlaps, # ------------------------------- # Average number of URLs involved in overlap
        }   
        user_rows.append(user_dct)

    return user_fields, user_rows


def get_url_axes(totals):
    url_fields = ['url', 'num_times_dloaded', 'avg_dload_time (secs)', 'involved_in_an_overlap', 'begins_an_overlap']
    url_rows = defaultdict(list)
    for d in (totals.num_times_dloaded_per_url, totals.avg_dload_time_per_url, totals.url_is_involved_in_an_overlap, totals.url_begins_an_overlap):
        for key, value in d.items():
            if value:
                url_rows[key].append(value)

    return url_fields, url_rows


def get_dload_axes(users):
    dload_fields = ['url', 'user_who_downloaded', 'dload_duration (secs)']
    dload_rows = []
    for user in tqdm(users, desc='Populating download data CSV'):
        for dload in user.dloads:
            dload_dct = {
                "url" : dload.url, # -------------------------------------------- # Downloaded URL
                "user_who_downloaded" : user.id, # ------------------------------ # User who did the download
                "dload_duration (secs)" : ms_to_seconds(dload.duration), # ------ # Overlap duration
            }   
            dload_rows.append(dload_dct)

    return dload_fields, dload_rows
    

def get_total_overlap_axes(totals):
    overlap_fields = ['avg_time_between_overlaps (mins)', 'avg_overlap_duration (secs)', 'avg_time_before_overlap_starts (secs)',
    'avg_num_urls_per_overlaps', 'most_common_url_that_begins_an_overlap']

    overlap_rows = [ms_to_minutes(totals.avg_time_between_overlaps), ms_to_seconds(totals.avg_overlap_duration),
    ms_to_seconds(totals.avg_time_before_overlap_starts), totals.avg_num_urls_per_overlaps, totals.most_common_url_that_begins_an_overlap]

    return overlap_fields, overlap_rows


def get_overlap_axes(users):
    overlap_fields = ['user_for_this_overlap', 'overlap_duration (secs)', 'time_before_overlap_starts (secs)', 'url_that_begins_the_overlap','num_urls_per_overlap']
    overlap_rows = []
    for user in tqdm(users, desc='Populating overlap data CSV'):
        for overlap in user.overlaps:
            overlap_dct = {
                "user_for_this_overlap" : user.id, # ---------------------------------------------------------- # User ID
                "overlap_duration (secs)" : ms_to_seconds(overlap.duration), # -------------------------------- # Overlap duration
                "time_before_overlap_starts (secs)" : ms_to_seconds(overlap.time_before_overlap_starts), # ---- # Time before overlap starts
                "url_that_begins_the_overlap" : overlap.overlapping_url, # ------------------------------------ # URL that begins the overlap
                "num_urls_per_overlap" : overlap.num_urls # --------------------------------------------------- # Number of URLs per overlap #TODO
            }   
            overlap_rows.append(overlap_dct)

    return overlap_fields, overlap_rows


def ms_to_hours(ms):
    if ms:
        return round(ms / 3600000, 2)

def ms_to_minutes(ms):
    if ms:
        return round(ms / 60000, 2)

def ms_to_seconds(ms):
    if ms:
        return round(ms / 1000, 2)

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
    users = generate_user_logs(logs)
    
    totals = Totals(users)
    totals.get_overlaps()
    totals.get_all_urls_in_overlaps()
    totals.get_overlapping_urls()

    totals.get_avg_dload_time_per_url()
    totals.get_num_times_dloaded_per_url()
    totals.get_url_is_involved_in_an_overlap()
    totals.get_url_begins_an_overlap()

    totals.get_most_common_url_that_begins_an_overlap()
    totals.get_avg_overlap_duration()
    totals.get_avg_time_before_overlap_starts()
    totals.get_avg_time_between_overlaps()
    totals.get_avg_num_urls_per_overlaps()
    
    # user data
    user_fields, user_rows = get_user_axes(users)
    user_app = Dash(__name__, external_stylesheets=external_stylesheets)
    user_data = Graph(users, user_fields, user_rows, "user_data.csv", user_app)
    user_data.create_format1_csv()
    user_data.get_df()
    user_data.get_user_graphs()
    user_data.init_app()

    # unique_url data
    url_fields, url_rows = get_url_axes(totals)
    url_app = Dash(__name__, external_stylesheets=external_stylesheets)
    url_data = Graph(totals, url_fields, url_rows, "unique_url_data.csv", url_app)
    url_data.create_format2_csv()
    url_data.get_df()
    url_data.get_url_graphs()
    url_data.init_app()

    # download data
    dload_fields, dload_rows = get_dload_axes(users)
    dload_app = Dash(__name__, external_stylesheets=external_stylesheets)
    dload_data = Graph(users, dload_fields, dload_rows, "download_data.csv", dload_app)
    dload_data.create_format1_csv()
    dload_data.get_df()
    dload_data.get_dload_graphs()
    dload_data.init_app()

    # overlap data
    overlap_fields, overlap_rows = get_overlap_axes(users)
    overlap_app = Dash(__name__, external_stylesheets=external_stylesheets)
    overlap_data = Graph(users, overlap_fields, overlap_rows, "overlap_data.csv", overlap_app)
    overlap_data.create_format1_csv()
    overlap_data.get_df()
    overlap_data.get_overlap_graphs()
    overlap_data.init_app()

    # total overlap data
    total_overlap_fields, total_overlap_rows = get_total_overlap_axes(totals)
    total_overlap_app = Dash(__name__, external_stylesheets=external_stylesheets)
    total_overlap_data = Graph(totals, total_overlap_fields, total_overlap_rows, "total_overlap_data.csv", total_overlap_app)
    total_overlap_data.create_format3_csv()

    # visualized overlaps
    

    user_app.run_server(dev_tools_hot_reload=False)
    url_app.run_server(dev_tools_hot_reload=False)
    overlap_app.run_server(dev_tools_hot_reload=False)
    dload_app.run_server(dev_tools_hot_reload=False)


    return 0

if __name__ == "__main__":
    main()
