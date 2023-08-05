#!/usr/bin/env python
import atexit

from contextlib import contextmanager
from os.path import basename
from threading import Thread
import argparse
import cProfile
import collections

import os
import pstats
import select
import signal
import sys
import threading
import time
import traceback
import cStringIO

parser = argparse.ArgumentParser()
flags = argparse.Namespace()

def log(msg, *args, **kw):
  caller = sys._getframe(1)
  filename = caller.f_code.co_filename
  lineno = caller.f_lineno
  now = time.time()
  if 'exc_info' in kw:
    exc = ''.join(traceback.format_exc())
  else:
    exc = None
  print >> sys.stderr, '%s:%s:%d: %s' % (now, os.path.basename(filename), lineno, msg % args)
  if exc:
    print >> sys.stderr, exc


class Watchdog(threading.Thread):
  def __init__(self, max_delay=10):
    threading.Thread.__init__(self, name='WatchdogThread')
    self.max_delay = max_delay
    self._last_tick = time.time()
    self.setDaemon(True)

  def ping(self):
    self._last_tick = time.time()

  def run(self):
    while 1:
      if time.time() - self._last_tick > self.max_delay:
        sys.exit(0)
        os._exit(1)


class FileWatchdog(threading.Thread):
  """Watchdog for a file (typically `sys.stdin`).

  When the file closes, terminate the process.
  (This occurs when an ssh connection is terminated, for example.)
  """
  def __init__(self, file_handle):
    threading.Thread.__init__(self, name='WatchdogThread')
    self.setDaemon(True)
    self.file_handle = file_handle
    # self.log = open('/tmp/watchdog.%d' % os.getpid(), 'w')

  def run(self):
    f = [self.file_handle]
    while 1:
      r, w, x = select.select(f, f, f, 1.0)
      # print >>self.log, 'Watchdog running: %s %s %s' % (r,w,x)
      # self.log.flush()
      if r:
        # print >>self.log, 'Watchdog: file closed.  Shutting down.'
        # self.log.flush()
        os._exit(1)
      time.sleep(1)

def flatten(lst, depth=1):
  if depth == 0:
    return lst

  out = []
  for item in lst:
    if isinstance(item, (list, set)): out.extend(flatten(item, depth=depth - 1))
    else: out.append(item)
  return out

def parse_args(argv):
  global flags
  flags, rest = parser.parse_known_args(argv)
  return flags, rest

def add_flag(name, default, *args, **kw):
  if name in flags:
    # util.log('Duplicate flag definition (%s) ignored.', name)
    return

  setattr(flags, name, default)
  parser.add_argument('--' + name, default=default, *args, **kw)

def timeit(f, name=None):
  st = time.time()
  res = f()
  ed = time.time()
  if name is None:
    name = f
  log('Operation %s completed in %.3f seconds', name, ed - st)
  return res


@contextmanager
def timer_ctx(name='Operation'):
  '''Context based timer:

  Usage::

    with timer_ctx('LoopOp'):
      for i in range(10):
        my_op()

  '''
  st = time.time()
  yield
  ed = time.time()
  print('%3.5f:: %s' % (ed - st, name))

class Timer(object):
  '''Lazy timer.

  Prints elapsed time when destroyed.
  '''
  def __init__(self, name):
    self.name = name
    self.st = time.time()

  def __del__(self):
    print('%3.5f:: %s' % (time.time() - self.st, self.name))

def dump_stacks(out):
  id_to_name = dict([(th.ident, th.name) for th in threading.enumerate()])
  thread_stacks = collections.defaultdict(list)

  for thread_id, stack in sys._current_frames().items():
    code = []
    for filename, lineno, name, line in traceback.extract_stack(stack):
      if line is None: line = ''
      code.append('%s:%d (%s): %s' % (basename(filename), lineno, name, line.strip()))
    thread_stacks['\n'.join(code)].append(thread_id)

  for stack, thread_ids in thread_stacks.iteritems():
    print >> out, 'Thread %d(%s)' % (thread_ids[0], id_to_name.get(thread_ids[0], ''))
    if len(thread_ids) > 1:
      print >> out, '... and %d more' % (len(thread_ids) - 1)
    print >> out, stack
    print >> out

def stack_signal():
  out = cStringIO.StringIO()
  dump_stacks(out)
  print >> sys.stderr, out.getvalue()
  with open('/tmp/%d.stacks' % os.getpid(), 'w') as f:
    print >> f, out.getvalue()

QUIT_HANDLERS = {}
def _quit_handler(signal, frame):
  for h in QUIT_HANDLERS.keys():
    h()

signal.signal(signal.SIGQUIT, _quit_handler)

def register_quit_handler(f):
  QUIT_HANDLERS[f] = 1

def enable_stacktrace():
  register_quit_handler(stack_signal)

def disable_stacktrace():
  signal.signal(signal.SIGQUIT, signal.SIG_DFL)

_thread_run = Thread.run
_stat_lock = threading.Lock()
def _run_with_profile(self):
  self._prof = cProfile.Profile()
  self._prof.enable()
  _thread_run(self)
  self._prof.disable()

  with _stat_lock:
    if Thread.stats is None:
      Thread.stats = pstats.Stats(self._prof)
    else:
      Thread.stats.add(self._prof)

def dump_profile():
  import yappi
  yappi.stop()
  yappi.get_func_stats().save('/tmp/prof.out.%d' % os.getpid(), type='callgrind')

  from sparrow.rpc import zeromq
  zeromq.shutdown()
  stats = get_profile()
  if stats is None:
    return
  # stats.sort_stats('cumulative').print_stats(25)
  stats.dump_stats('/tmp/prof.out.%d' % os.getpid())
  try:
    os.unlink('/tmp/prof.out')
  except: pass

  try:
    os.symlink('/tmp/prof.out.%d' % os.getpid(), '/tmp/prof.out')
  except:
    pass

PROFILER = None
def enable_profiling():
  import yappi
  yappi.start()
  return

  Thread.stats = None
  Thread.run = _run_with_profile
  global PROFILER
  PROFILER = cProfile.Profile()
  PROFILER.enable()
  atexit.register(dump_profile)

def get_profile():
  if PROFILER is None:
    return None

  stats = pstats.Stats(PROFILER)
  if threading.Thread.stats is not None:
    stats.add(threading.Thread.stats)
  return stats
