# -*- coding: iso-8859-15 -*-
# 2011, José Manuel Fardello <jfardello@uoc.edu>
# Doctest for dardrive config

import os
import sys
sys.path.append(os.path.dirname(__file__))
import darsetts


class LastRun(object):
    '''
    >>> import os, sys
    >>> from datetime import datetime, timedelta
    >>> from sqlalchemy import func
    >>> from sqlalchemy import create_engine
    >>> from dardrive.db import *
    >>> from dardrive.db import Stat, save_stats
    >>> from sqlalchemy.orm import relationship, sessionmaker
    >>> days_back = lambda x:datetime.today() - timedelta(days=x)
    >>> create_all(darsetts.engine)
    >>> Sess = sessionmaker(bind=darsetts.engine)
    >>> s = Sess(bind=darsetts.engine)
    >>> r = Report("test", session=s)
    >>> job = s.query(Job).filter(Job.name == "test").one()
    >>> full = s.query(BackupType).get(1)
    >>> inc = s.query(BackupType).get(2)
    >>> s.query(Catalog).delete()
    10
    >>> s.query(Stat).delete()
    3
    >>> s.commit()
    >>> cat1 = Catalog(job=job, date=days_back(1), type=full)
    >>> cat2 = Catalog(job=job, date=days_back(2), type=inc)
    >>> cat3 = Catalog(job=job, date=days_back(5), type=inc)
    >>> cat1.ttook, cat2.ttook, cat3.ttook = (100, 50, 60)
    >>> cat1.status, cat2.status, cat3.status = (0, 0, 0)
    >>> s.add_all([cat1, cat2, cat3])
    >>> s.commit()
    >>> save_stats(cat1,s)
    >>> save_stats(cat2,s)
    >>> save_stats(cat3,s)
    >>> r.last_run()
    datetime.timedelta(0, 100)
    >>> r.last_run(backup_type=inc.name)
    datetime.timedelta(0, 50)
    >>>
    '''
    pass

if __name__ == "__main__":
    import doctest
    doctest.testmod()
