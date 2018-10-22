import re
from os import listdir
from os.path import isfile, join, splitext

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
