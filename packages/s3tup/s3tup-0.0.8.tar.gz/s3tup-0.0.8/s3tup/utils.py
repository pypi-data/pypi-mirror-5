from fnmatch import fnmatch
from base64 import b64encode
import hashlib
import os
import re

class Matcher(object):
    """Matches strings based on patterns

    Internally the matcher object has a list of unix style patterns to match
    and to ignore, and a list of regexes to match and to ignore. Each of
    these are tested against the string 's' in the matches method. Ignore
    has the highest precedence. If both patterns and regexes are empty, the
    object assumes that the match is True (though the ignore lists can still
    overpower this assumption).
    """
    
    def __init__(self, patterns=[], ignore_patterns=[], regexes=[],
                 ignore_regexes=[]):
        self.patterns = patterns
        self.ignore_patterns = ignore_patterns
        self.regexes = regexes
        self.ignore_regexes = ignore_regexes

    def matches(self, s):
        """Return whether this matcher matches string s"""
        # If neither patterns nor regexes is set, match everything
        matched = not self.patterns and not self.regexes

        if self.patterns:
            for pattern in self.patterns:
                if fnmatch(s, pattern):
                    matched = True
                    break

        if self.regexes and matched is not True:
            for regex in self.regexes:
                if re.search(regex, s):
                    matched = True
                    break

        if self.ignore_patterns and matched is True:
            for pattern in self.ignore_patterns:
                if fnmatch(s, pattern):
                    return False

        if self.ignore_regexes and matched is True:
            for regex in self.ignore_regexes:
                if re.search(regex, s):
                    return False

        return matched


def file_md5(f):
    """Return md5 hash of filelike object f"""
    m = hashlib.md5()
    while True:
        buf=f.read(8192)
        if not buf: break
        m.update(buf)
    return b64encode(m.digest()).strip()

def os_walk_iter(src):
    """Return list of all file paths in src relative to src"""
    for path, dirs, files in os.walk(src):
        for f in files:
            full_path = os.path.join(path, f)
            yield os.path.relpath(full_path, src)

def key_diff(before, after):
    """
    Return a dict representing the difference between two runs of
    Bucket.get_remote_keys().

    Useful to see changes in the keys within a bucket after some operation.
    Ex:
        before = list(bucket.get_remote_keys())
        do_something()
        diff = key_diff(before, bucket.get_remote_keys())

    Returned dict has fields 'new', 'removed', 'modified', and 'unmodified',
    and each field contains a list of str key names. Size and md5 are used to
    check for modification.

    Note: Be sure that 'before' is a list and *not* the generator returned
    by Bucket.get_remote_keys; because it's a generator, it won't actually
    fetch them from the server until they are iterated through.

    """
    before_set = {k['name'] for k in before}
    after_set = {k['name'] for k in after}

    before_keys = {k['name']: k for k in before if k['name'] in after_set}
    after_keys = {k['name']: k for k in after if k['name'] in before_set}

    removed = before_set - after_set
    new = after_set - before_set

    modified = set()
    unmodified = set()
    for k in (before_set & after_set):
        if before_keys[k]['md5'] == after_keys[k]['md5'] and \
           before_keys[k]['size'] == after_keys[k]['size']:
            unmodified.add(k)
        else:
            modified.add(k)
    return {'new': new, 'removed': removed, 'modified': modified,
            'unmodified': unmodified}
