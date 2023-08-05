import dpath.exceptions
import re
import fnmatch
import shlex
import sys

def validate(path, separator="/", regex=None):
    validated = []
    for key in path:
        strkey = str(key)
        if (separator and (separator in strkey)):
            raise dpath.exceptions.InvalidKeyName("{} at {} contains the separator {}"
                                                  "".format(strkey,
                                                            separator.join(validated),
                                                            separator))
        elif (regex and (not regex.findall(strkey))):
            raise dpath.exceptions.InvalidKeyName("{} at {} does not match the expression {}"
                                                  "".format(strkey,
                                                            separator.join(validated),
                                                            regex.pattern))
        validated.append(strkey)

def paths(obj, dirs=True, leaves=True, path=[], skip=False, separator="/"):
    """Yield all paths of the object.

    Arguments:

    obj -- An object to get paths from.

    Keyword Arguments:

    dirs -- Yield intermediate paths.
    leaves -- Yield the paths with leaf objects.
    path -- A list of keys representing the path.
    skip -- Skip special keys beginning with '+'.

    """
    if isinstance(obj, dict):
        for (i, v) in enumerate(obj):
            if skip and v[0] == '+':
                continue
            newpath = path + [v]
            validate(newpath, separator=separator)
            if dirs:
                yield newpath
            for child in paths(obj[v], dirs, leaves, newpath, skip):
                yield child
    elif isinstance(obj, (list, tuple)):
        for (i, v) in enumerate(obj):
            newpath = path + [i]
            if dirs:
                yield newpath
            for child in paths(obj[i], dirs, leaves, newpath, skip):
                yield child
    elif leaves:
        yield path + [obj]
    elif not dirs:
        yield path

def match(path, glob):
    """Match the path with the glob.

    Arguments:

    path -- A list of keys representing the path.
    glob -- A list of globs to match against the path.

    """
    path_len = len(path)
    glob_len = len(glob)

    ss = -1
    ss_glob = glob
    if '**' in glob:
        ss = glob.index('**')
        if '**' in glob[ss + 1:]:
            raise dpath.exceptions.InvalidGlob("Invalid glob. Only one '**' is permitted per glob.")

        if path_len >= glob_len:
            # Just right or more stars.
            more_stars = ['*'] * (path_len - glob_len + 1)
            ss_glob = glob[:ss] + more_stars + glob[ss + 1:]
        elif path_len == glob_len - 1:
            # Need one less star.
            ss_glob = glob[:ss] + glob[ss + 1:]

    if path_len == len(ss_glob):
        return all(map(fnmatch.fnmatch, map(str, path), map(str, ss_glob)))

    return False

def search(obj, glob, dirs=True, leaves=False):
    """Search the object paths that match the glob."""
    for path in paths(obj, dirs, leaves, skip=True):
        if match(path, glob):
            yield path

def is_glob(string):
    return any([c in string for c in '*?[]!'])

def set(obj, path, value, create_missing=True, separator="/", filter=None):
    """Set the value of the given path in the object. Path
    must be a list of specific path elements, not a glob.
    You can use dpath.util.set for globs, but the paths must
    slready exist.

    If create_missing is True (the default behavior), then any
    missing path components in the dictionary are made silently.
    Otherwise, if False, an exception is thrown if path
    components are missing.
    """
    cur = obj
    traversed = []

    def _presence_test_dict(obj, elem):
        return (elem in obj)

    def _create_missing_dict(obj, elem):
        obj[elem] = {}

    def _presence_test_list(obj, idx):
        return (idx < len(obj))

    def _create_missing_list(obj, idx):
        idx = int(str(elem))
        while (len(obj)-1) < idx:
            obj.append(None)

    def _accessor_dict(obj, elem):
        return obj[elem]

    def _accessor_list(obj, elem):
        return obj[int(str(elem))]

    def _assigner_dict(obj, elem, value):
        obj[elem] = value

    def _assigner_list(obj, elem, value):
        obj[int(str(elem))] = value

    elem = None
    for elem in path:
        tester = None
        creator = None
        accessor = None
        assigner = None
        if issubclass(obj.__class__, (dict)):
            tester = _presence_test_dict
            creator = _create_missing_dict
            accessor = _accessor_dict
            assigner = _assigner_dict
        elif issubclass(obj.__class__, (list, tuple)):
            if not str(elem).isdigit():
                raise TypeError("Can only create integer indexes in lists, "
                                "not {}, in {}".format(type(obj),
                                                       separator.join(traversed)
                                                       )
                                )
            tester = _presence_test_list
            creator = _create_missing_list
            accessor = _accessor_list
            assigner = _assigner_list
        else:
            raise TypeError("Unable to path into elements of type {} "
                            "at {}".format(type(elem), separator.join(traversed)))
        if (not tester(obj, elem)) and (create_missing):
            creator(obj, elem)
        elif (not tester(obj, elem)):
            raise dpath.exceptions.PathNotFound(
                "{} does not exist in {}".format(
                    elem,
                    separator.join(traversed)
                    )
                )
        traversed.append(elem)
        if len(traversed) < len(path):
            obj = accessor(obj, elem)

    if elem is None:
        return
    if (filter and filter(accessor(obj, elem))) or (not filter):
        assigner(obj, elem, value)

def get(obj, path, view=False):
    """Get the value of the given path.

    Arguments:

    obj -- Object to look in.
    path -- A list of keys representing the path.

    Keyword Arguments:

    view -- Return a view of the object.

    """
    target = obj
    head = type(target)()
    tail = head
    up = None
    for key in path:
        target = target[key]
        if view:
            if isinstance(tail, dict):
                if target == None:
                    tail[key] = None
                else:
                    tail[key] = type(target)()
            elif isinstance(tail, list):
                if key >= len(tail):
                    tail += [None] * (key - len(tail) + 1)
                if target == None:
                    tail[key] = None
                else:
                    tail[key] = type(target)()
            up = tail
            tail = tail[key]
    if view:
        up[path[-1]] = target
        return head
    else:
        return target
