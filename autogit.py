from pygit2 import Repository
from collections import Counter
import re

BLACKLIST = "if return def not for in".split()

def commit_message_guess():
    diff = repo.diff()
    if not diff.patch:
        return ""
    diff_text = filter_lines(is_diff_line, diff.patch)
    counts = word_counts(diff_text, BLACKLIST)
    most_common = counts.most_common(3)
    keyword_string = " ".join(x[0] for x in most_common)
    return "keywords: " + keyword_string

def word_counts(text, blacklist=[]):
    words = re.findall("[\w_]+", text)
    words = [word for word in words if word not in blacklist]
    return Counter(words)

def filter_lines(predicate, text):
    lines = text.split("\n")
    return "\n".join(line for line in lines if predicate(line))

def is_diff_line(line):
    return re.match("^[+-](?![+]{2}|[-]{2})", line)


repo = Repository(".git")
diff = repo.diff()
print(diff.patch)
print(commit_message_guess())
