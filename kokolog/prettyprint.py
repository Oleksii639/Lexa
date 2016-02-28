#!/usr/bin/python
# coding=utf-8

"""
   traceback message or other files
"""
import sys
import os
import datetime
import logging
from raven.handlers.logging import SentryHandler
# from raven.conf import setup_logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from character import _cs, _cu

LOGDEBUG = True
LOGDIR = '/var/log/'
FILEDIR = '/var/file/'
TIMEOUT = 10

def _print(*args):
    """
        Print txt by coding GBK.

        *args
          list, list of printing contents
        
    """
    if not LOGDEBUG:
        return
    if not args:
        return
    encoding = 'gbk'
    args = [_cs(a, encoding) for a in args]
    f_back = None
    try:
        raise Exception
    except:
        f_back = sys.exc_traceback.tb_frame.f_back
    f_name = f_back.f_code.co_name
    filename = os.path.basename(f_back.f_code.co_filename)
    m_name = os.path.splitext(filename)[0]
    prefix = ('[%s.%s]'%(m_name, f_name)).ljust(20, ' ')
    if os.name == 'nt':
        for i in range(len(args)):
            v = args [i]
            if isinstance(v, str):
                args[i] = v #v.decode('utf8').encode('gbk')
            elif isinstance(v, unicode):
                args[i] = v.encode('gbk')
    print '[%s]'%str(datetime.datetime.now()), prefix, ' '.join(args)

def _print_err(*args):
    """
        Print errors.

        *args
          list, list of printing contents
        
    """
    if not LOGDEBUG:
        return
    if not args:
        return
    encoding = 'utf8' if os.name == 'posix' else 'gbk'
    args = [_cs(a, encoding) for a in args]
    f_back = None
    try:
        raise Exception
    except:
        f_back = sys.exc_traceback.tb_frame.f_back
    f_name = f_back.f_code.co_name
    filename = os.path.basename(f_back.f_code.co_filename)
    m_name = os.path.splitext(filename)[0]
    prefix = ('[%s.%s]'%(m_name, f_name)).ljust(20, ' ')
    print bcolors.FAIL+'[%s]'%str(datetime.datetime.now()), prefix, ' '.join(args) + bcolors.ENDC


def logprint(logname, category, level='INFO', to_stdout=True, backupCount=15, sentrykey=''):
    """
        Print logs by datetime.

        logname
          string, file name
        category
          string, category path of logs file in log directory
        level
          string, restrict whether logs to be printed or not
        to_stdout
          bool, restrict whether logs to be print in the console or not
        backupCount
          int, how many backups can be reserved
        sentrykey
          string, a key for raven to sentry
        
    """
    path = os.path.join(LOGDIR, category, logname + '.log')
    print "log path:", path
    if not os.path.exists(path[:path.rindex('/')]):
        os.makedirs(path[:path.rindex('/')])
    # Initialize logger
    logger = logging.getLogger(logname)
    frt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    hdr = None
    if path:
        hdr = TimedRotatingFileHandler(path, 'D', 1, backupCount)
        hdr.suffix = "%Y%m%d"
        # hdr = RotatingFileHandler(path, 'a', maxBytes, backupCount, 'utf-8')
        hdr.setFormatter(frt)
        hdr._name = logname + '_p'
        already_in = False
        for _hdr in logger.handlers:
            if _hdr._name == logname + '_p':
                already_in = True
                break
        if not already_in:
            logger.addHandler(hdr)
    if to_stdout:
        hdr = logging.StreamHandler(sys.stdout)
        hdr.setFormatter(frt)
        hdr._name = logname + '_s'
        already_in = False
        for _hdr in logger.handlers:
            if _hdr._name == logname + '_s':
                already_in = True
        if not already_in:
            logger.addHandler(hdr)
    if level == 'NOTEST':
        level == logging.NOTSET
    elif level == 'DEBUG':
        level == logging.DEBUG
    elif level == 'WARNING':
        level == logging.WARNING
    elif level == 'ERROR':
        level == logging.ERROR
    elif level == 'CRITICAL':
        level == logging.CRITICAL
    else:
        level == logging.INFO
    logger.setLevel(level)

    sentrykey = sentrykey.strip()
    print 'see sentry: ', sentrykey # hdr = SentryHandler('http://1d1db94883984afb8401b1c616b63922:c7cf1b896ed1465d8f047d36b0fdd268@111.innapp.cn:9090/3')
    if not sentrykey == '':
        if not '?' in sentrykey:
            sentrykey = sentrykey + '?timeout=' + str(TIMEOUT)
        elif not 'timeout=' in sentrykey.split('?')[-1]:
            sentrykey = sentrykey + '&timeout=' + str(TIMEOUT)
    hdr = SentryHandler(sentrykey)

    def _wraper(*args, **kwargs):
        if not LOGDEBUG:
            return
        if not args:
            return
        encoding = 'utf8' if os.name == 'posix' else 'gbk'
        args = [_cu(a, encoding) for a in args]
        f_back = None
        try:
            raise Exception
        except:
            f_back = sys.exc_traceback.tb_frame.f_back
        f_name = f_back.f_code.co_name
        filename = os.path.basename(f_back.f_code.co_filename)
        m_name = os.path.splitext(filename)[0]
        prefix = (u'[%s.%s]' % (m_name, f_name)).ljust(20, ' ')
        s = kwargs.get('to_sentry', False)
        if s and not sentrykey == '':
            logger.addHandler(hdr)
        else:
            logger.removeHandler(hdr)
        l = kwargs.get('printlevel', 'info').upper()
        if l == 'DEBUG':
            try:
                logger.debug(u' '.join([prefix,
                     ' '.join(args)]))
            except:
                t, v, b = sys.exc_info()
                err_messages = traceback.format_exception(t, v, b)
                print 'Error: %s' % ','.join(err_messages)
        elif l == 'WARNING':
            try:
                logger.warning(u' '.join([prefix,
                     ' '.join(args)]))
            except:
                t, v, b = sys.exc_info()
                err_messages = traceback.format_exception(t, v, b)
                print 'Error: %s' % ','.join(err_messages)
        elif l == 'ERROR':
            try:
                logger.error(u' '.join([prefix,
                         ' '.join(args)]))
            except:
                t, v, b = sys.exc_info()
                err_messages = traceback.format_exception(t, v, b)
                print 'Error: %s' % ','.join(err_messages)
        elif l == 'CRITICAL':
            try:
                logger.critical(u' '.join([prefix,
                     ' '.join(args)]))
            except:
                t, v, b = sys.exc_info()
                err_messages = traceback.format_exception(t, v, b)
                print 'Error: %s' % ','.join(err_messages)
        else:
            try:
                logger.info(u' '.join([prefix,
                     ' '.join(args)]))
            except:
                t, v, b = sys.exc_info()
                err_messages = traceback.format_exception(t, v, b)
                print 'Error: %s' % ','.join(err_messages)
    return _wraper, logger

def fileprint(filename, category, level=logging.DEBUG, maxBytes=1024*10124*100,
             backupCount=0, to_stdout=True):
    """
        Print files by file size.

        filename
          string, file name
        category
          string, category path of logs file in log directory
        level
          enumerated type of logging module, restrict whether logs to be printed or not
        maxBytes
          int, max limit of file size
        backupCount
          int, allowed numbers of file copys
        to_stdout
          bool, restrict whether logs to be print in the console or not
        
    """
    path = os.path.join(FILEDIR, category, filename)

    # Initialize filer
    filer = logging.getLogger(filename)
    frt = logging.Formatter('%(message)s')
    hdr = None
    if path:
        hdr = RotatingFileHandler(path, 'a', maxBytes, backupCount, 'utf-8')
        hdr.setFormatter(frt)
        hdr._name = filename + '_p'
        already_in = False
        for _hdr in filer.handlers:
            if _hdr._name == filename + '_p':
                already_in = True
                break
        if not already_in:
            filer.addHandler(hdr)
    if to_stdout:
        hdr = logging.StreamHandler(sys.stdout)
        hdr.setFormatter(frt)
        hdr._name = filename + '_s'
        already_in = False
        for _hdr in filer.handlers:
            if _hdr._name == filename + '_s':
                already_in = True
        if not already_in:
            filer.addHandler(hdr)
    filer.setLevel(level)
    def _wraper(*args):
        if not LOGDEBUG:
            return
        if not args:
            return
        encoding = 'utf8' if os.name == 'posix' else 'gbk'
        args = [_cu(a, encoding) for a in args]
        filer.info(' '.join(args))
    return _wraper, filer

class bcolors:
    """
        定义常用颜色
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

if __name__ == '__main__':
    pass
