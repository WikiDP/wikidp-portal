import re
from os import listdir
from os.path import isfile, join, splitext
from datetime import datetime

ITEM_REGEX = "(Q|q)\d+"
PROPERTY_REGEX = "(P|p)\d+"

def remove_duplicates_from_list(lst):
    return list(dict.fromkeys(lst))

def get_pid_from_string(str):
    regex_search = re.search(PROPERTY_REGEX, str)
    return regex_search.group() if regex_search else False

def get_qid_from_string(str):
    regex_search = re.search(ITEM_REGEX, str)
    return regex_search.group() if regex_search else False

def get_directory_filenames_with_subdirectories(directory_path):
    output = []
    for item in listdir(directory_path):
        if isfile(join(directory_path, item)):
            output.append(item)
        else:
            output.append([item, get_directory_filenames_with_subdirectories(join(directory_path, item))])
    return output

def remove_extension_from_filename(filename_string):
    return splitext(filename_string)[0]

def list_sorting_by_length(elem):
    """Auxiliary sorting key function at the list level"""
    return len(elem[0])

def dict_sorting_by_length(elem):
    """Auxiliary sorting key function at the dictionary level"""
    return len(elem[0][0])


def time_formatter(time):
    """Converts wikidata's time json to a human readable string"""
    try:
        formatted_time = datetime.strptime(time, '+%Y-%m-%dT%H:%M:%SZ')
        return formatted_time.strftime("%A, %B %-d, %Y")
    except Exception:
        return time
