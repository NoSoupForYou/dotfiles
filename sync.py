#!/bin/env python3


from argparse import ArgumentParser
from difflib import unified_diff
from functools import lru_cache
import logging
from os import listdir
from os.path import abspath
from os.path import basename
from os.path import dirname
from os.path import expanduser
from os.path import getmtime
from os.path import join
from pprint import pformat
from shutil import copy2 as copy
import sys


class Resolutions(object):
    OVERWRITE = 0
    LATEST = 1


def _get_resolution(overwrite, latest):
    """Return the enum"""
    if overwrite:
        resolution = Resolutions.OVERWRITE
        logging.info("Chose to resolve conflicts by overwriting target scripts")
    elif latest:
        resolution = Resolutions.LATEST
        logging.info("Chose to resolve conflicts by keeping the latest modified scripts")
    else:
        resolution = None
        logging.info("No conflict resolution method chosen")
    return resolution


_memoize = lru_cache(maxsize=None)


_source = _memoize(join)
"""Source filename for a given script"""


_target = _memoize(lambda targetdir, target: join(targetdir, ".{}".format(target)))
"""Target filename for a given script"""


def _get_conflicts(sources, targets, srcdir, targetdir):
    """Yield scripts modified after deployment"""

    check = [src for src in sources if any(t.endswith(src) for t in targets)]
    logging.debug("Checking %d scripts: %s", len(check), check)

    for script in check:
        source_mtime = getmtime(_source(srcdir, script))
        target_mtime = getmtime(_target(targetdir, script))
        if target_mtime > source_mtime:
            logging.warning(
                "Target %s was modified after deployment: source mtime is %d, target mtime is %d",
                script, source_mtime, target_mtime)
            yield script


def _get_diff(conflict, srcdir, targetdir):
    """Diff the two files and print to the console"""
    with open(_source(srcdir, conflict)) as src:
        source = src.readlines()
        source_name = src.name
    try:
        with open(_target(targetdir, conflict)) as dest:
            target = dest.readlines()
            dest_name = dest.name
    except FileNotFoundError:
        target = []
        dest_name = ""
    return unified_diff(source, target, fromfile=source_name, tofile=dest_name)


def _diff_scripts(sources, targets, srcdir, targetdir, resolution):
    """
    Get conflicts by comparing timestamps and determine scripts that diff

    Then, determine what files need to be moved given the resolution type chosen
    """

    diffs = {}
    conflicts = set(_get_conflicts(sources, targets, srcdir, targetdir))
    for conflict in conflicts:
        diff = "".join(_get_diff(conflict, srcdir, targetdir))
        if resolution is not None:
            diffs[conflict] = diff

    if len(conflicts) > 0 and resolution is None:
        logging.warning(
            "Conflicts above will not be in sync. Use --overwrite or --latest to resolve")

    # Now grab the diffs of non-conflicting files
    for script in set(sources) - conflicts:
        diff = "".join(_get_diff(script, srcdir, targetdir))
        if len(diff) > 0:
            diffs[script] = diff

    # Using the given resolution, determine which files need to move where
    moves = []
    for diff in diffs:
        if diff in conflicts and resolution == Resolutions.LATEST:
            moves.append((_target(targetdir, diff), _source(srcdir, diff)))
        else:
            moves.append((_source(srcdir, diff), _target(targetdir, diff)))

    return diffs, moves


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    dotfiles = abspath(dirname(__file__))
    homedir = abspath(expanduser("~"))

    parser = ArgumentParser(description="Commit rc files to source control")
    parser.add_argument("-s", "--srcdir", help="Source directory", default=dotfiles)
    parser.add_argument(
        "-t", "--targetdir", help="Target directory, defaults to ~", default=homedir)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument(
        "--overwrite", action="store_true", help="Resolve conflicts by overwriting the target")
    parser.add_argument(
        "--latest", action="store_true", help="Resolve conflicts by picking the latest modified")
    parser.add_argument("-d", "--dryrun", action="store_true", help="Don't actually move any files")
    _args = parser.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if _args.verbose else logging.INFO)
    logging.debug("Source directory is %s", _args.srcdir)
    logging.debug("Target directory is %s", _args.targetdir)

    sources = list(filter(lambda x: x != basename(__file__), listdir(_args.srcdir)))
    logging.debug("%d sources: %s", len(sources), ", ".join(sources))

    targets = list(filter(
        lambda filename: any((filename.endswith(src) for src in sources)),
        listdir(_args.targetdir)
    ))
    logging.debug("%d existing targets: %s", len(targets), ", ".join(targets))

    resolution = _get_resolution(_args.overwrite, _args.latest)


    diffs, moves = _diff_scripts(
        sources, targets, _args.srcdir, _args.targetdir, _args.overwrite or _args.latest)

    if _args.verbose:
        for diff, text in diffs.items():
            logging.info("Diff for %s is", diff)
            print(text, end="")

    for source, target in moves:
        if _args.dryrun:
            logging.info("Will move %s to %s", source, target)
        else:
            copy(source, target)
            logging.info("Moved %s to %s", source, target)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
