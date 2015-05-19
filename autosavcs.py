import subprocess
from collections import Counter
import re
import time
import watchdog
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

class FileSystemEventDetector(watchdog.events.FileSystemEventHandler):
    """docstring for FileSystemEventDetector"""
    def __init__(self):
        super(FileSystemEventDetector, self).__init__()

    def on_any_event(self, event):
        print("")
        print(commit_message_guess())

BLACKLIST = "if return def not for in while".split()

def git(command):
    return subprocess.check_output(["git"] + command.split()).decode("utf-8")

def commit_message_guess():
    diff = git("diff --word-diff=porcelain")
    add_text = filter_lines(is_add_line, diff)
    delete_text = filter_lines(is_delete_line, diff)
    
    add_counts = word_counts(add_text, BLACKLIST)
    delete_counts = word_counts(delete_text, BLACKLIST)
    change_counts = add_counts & delete_counts
    add_counts -= change_counts
    delete_counts -= change_counts
    
    count_strings = map(print_most_common, [add_counts, delete_counts, change_counts])
    
    return "+ {}\n- {}\n% {}".format(*count_strings)

def print_most_common(counts):
    most_common = counts.most_common(3)
    return " ".join(x[0] for x in most_common)

def word_counts(text, blacklist=[]):
    words = re.findall("[\w_]{3,}", text)
    words = [word for word in words if word not in blacklist]
    return Counter(words)

def filter_lines(predicate, text):
    lines = text.split("\n")
    return "\n".join(line for line in lines if predicate(line))

def is_diff_line(line):
    return is_add_line or is_delete_line

def is_add_line(line):
    return re.match("^[+](?![+]{2})", line)

def is_delete_line(line):
    return re.match("^[-](?![-]{2})", line)

print(commit_message_guess())

event_detector = FileSystemEventDetector()
observer = Observer()
observer.schedule(event_detector, ".", recursive=False)
observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()