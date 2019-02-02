
# coding: utf-8

# In[1]:


import os
import sys
from glob import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pprint import pprint
import json

import radical.utils     as ru
import radical.pilot     as rp
import radical.analytics as ra
import radical.entk as re


# In[13]:


# Input constants
trials = 2
stages = [16, 64, 256]
resource = 'bw'
src = '../raw-data/'
proc = '../proc-data/'


# In[3]:


def get_adap_time(loc, sid):
    
    # Get adap time
    duration = 0.0
    sess = ra.Session(stype='radical.entk', src=loc, sid=sid)
    stages = sorted(sess.filter(etype='stage', inplace=False).list('uid'))
#     print stages
    for stage in stages:
        duration += sess.duration(event=[{ru.EVENT: 'executing post-exec for stage %s'%stage},
                                         {ru.EVENT: 'post-exec executed for stage %s'%stage}])
    return duration


# In[4]:


def get_entk_overheads(loc, sid):
    
    sess = ra.Session(stype='radical.entk', src=loc, sid=sid)
    init_time = sess.duration(event=[{ru.EVENT: 'create amgr obj'},
                                     {ru.EVENT: 'init rreq submission'}])
    res_sub_time = sess.duration(event=[{ru.EVENT: 'creating rreq'},
                                     {ru.EVENT: 'rreq submitted'}])
    total_teardown_time = sess.duration(event=[{ru.EVENT: 'start termination'},
                                               {ru.EVENT: 'termination done'}])
    rts_teardown_time = sess.duration(event=[{ru.EVENT: 'canceling resource allocation'},
                                             {ru.EVENT: 'resource allocation cancelled'}])
    
    return {'init_time': init_time,
           'res_sub_time': res_sub_time,
           'total_teardown_time': total_teardown_time,
           'rts_teardown_time': rts_teardown_time}


# In[5]:


def get_entk_exec_time(loc, sid):
    sess = ra.Session(stype='radical.entk', src=loc, sid=sid)
    tasks = sess.filter(etype='task', inplace=False)
    return tasks.duration(state=['SCHEDULING','DONE'])


# In[6]:


def process_entk_profiles(src):
    
    sid = os.path.basename(src)
    loc = os.path.dirname(src)
    tag = '/'.join(loc.split('/')[2:])
    proc_data = os.path.join(proc,tag) + '/entk_data.json'
    data = {'adap_time': 0, 'overheads': 0, 'exec_time': 0}
        
    data['adap_time'] = get_adap_time(loc, sid)
    data['overheads'] = get_entk_overheads(loc, sid)
    data['exec_time'] = get_entk_exec_time(loc, sid)
    
    write_data(data, proc_data)
    return proc_data


# In[52]:


def write_data(data, proc_path):

    if 'rp.session' in proc_path:
        proc_path = os.path.dirname(os.path.dirname(proc_path)) + '/' + os.path.basename(proc_path)
    if not os.path.isdir(os.path.dirname(proc_path)):
        os.makedirs(os.path.dirname(proc_path))
    ru.write_json(data,proc_path)
    
    return proc_path


# In[51]:


print 'EnTK analysis'
for s in stages:
    for t in range(1,trials+1):
        path = os.path.join(src,resource,'trial-%s'%t,'stages-%s'%s)
        for sess in glob(path + '/' + 're.session.*'):  
            print 'Processing: ', sess
            out_path = process_entk_profiles(sess)
            print 'Output written to ', out_path


# In[55]:


def process_rp_profiles(src):
    
    sid = os.path.basename(src)
    loc = os.path.dirname(src)
    tag = '/'.join(loc.split('/')[2:])
    proc_data = os.path.join(proc,tag) + '/rp_data.json'
    data = {'task_mgmt': 0, 'exec_time': 0}
    
    sess = ra.Session(stype='radical.pilot', src=loc, sid=sid)
    units = sess.filter(etype='unit', inplace=False)
        
    data['task_mgmt'] = units.duration(state=['NEW','DONE'])
    data['exec_time'] = units.duration(event=[{ru.EVENT:'exec_start'},{ru.EVENT:'exec_stop'}])
    
    proc_path = write_data(data, proc_data)
    return proc_path


# In[56]:


print 'RP analysis'
for s in stages:
    for t in range(1,trials+1):
        path = os.path.join(src,resource,'trial-%s'%t,'stages-%s'%s)
        for sess in glob(path + '/' + 'rp.session.*/'):  
            print 'Processing: ', sess
            out_path = process_rp_profiles(sess)
            print 'Output written to ', out_path

