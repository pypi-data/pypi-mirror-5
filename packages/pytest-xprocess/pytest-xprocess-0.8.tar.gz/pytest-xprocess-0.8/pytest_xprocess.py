
# content of conftest.py

import pytest
import subprocess
import textwrap
import py
import sys
import os


from xprocess import XProcess, do_killxshow
print_ = py.builtin.print_
std = py.std

def pytest_addoption(parser):
    group = parser.getgroup("xprocess",
        "managing external processes across test-runs [xprocess]")
    group.addoption('--xkill', action="store_true",
        help="kill all external processes")
    group.addoption('--xshow', action="store_true",
        help="show status of external process")

def getrootdir(config):
    from pytest_cache import getrootdir
    return getrootdir(config, ".xprocess").ensure(dir=1)

def pytest_cmdline_main(config):
    xkill = config.option.xkill
    xshow = config.option.xshow
    if xkill or xshow:
        config.pluginmanager.do_configure(config)
        tw = py.io.TerminalWriter()
        rootdir = getrootdir(config)
        xprocess = XProcess(config, rootdir)
        return do_killxshow(xprocess, tw, xkill)

@pytest.fixture(scope="session")
def xprocess(request):
    """ Return session-scoped XProcess helper to manage long-running
    processes required for testing.
    """
    rootdir = getrootdir(request.config)
    return XProcess(request.config, rootdir)

def pytest_runtest_makereport(__multicall__, item, call):
    logfiles = getattr(item.config, "_extlogfiles", None)
    if logfiles is None:
        return
    report = __multicall__.execute()
    for name in sorted(logfiles):
        content = logfiles[name].read()
        if content:
            longrepr = getattr(report, "longrepr", None)
            if hasattr(longrepr, "addsection"):
                longrepr.addsection("%s log" %name, content)
    return report

