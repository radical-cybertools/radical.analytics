.. _chapter_inspection:

Inspection
==========

RADICAL-Analytics enables deriving information about an RCT session. For example, session ID, number of tasks, number of pilots, final state of the tasks and pilots, duration of each task and pilot, etc.

RADICAL-Pilot Session
---------------------

Information commonly used when analyzing and plotting one or more sessions of RADICAL-Pilot

Single Session
^^^^^^^^^^^^^^

.. code-block:: python
   :linenos:

    # RCT session, pilot and task objects
    raw  = '../data/raw/incite2021/re.session.login1.lei.018775.0005'
    sobj = ra.Session(raw, 'radical.pilot')
    pobj = sobj.filter(etype='pilot', inplace=False)
    tobj = sobj.filter(etype='task', inplace=False)

    # Session info
    sinfo = {
        'sid'       : sobj.uid,
        'lm'        : sobj.get(etype='pilot')[0].cfg['agent_launch_method'],
        'hostid'    : sobj.get(etype='pilot')[0].cfg['hostid'],
        'cores_node': sobj.get(etype='pilot')[0].cfg['resource_details']['rm_info']['cores_per_node'],
        'gpus_node' : sobj.get(etype='pilot')[0].cfg['resource_details']['rm_info']['gpus_per_node'],
        'smt'       : sobj.get(etype='pilot')[0].cfg['resource_details']['rm_info']['smt']
    }

    # Pilot info (assumes 1 pilot)
    sinfo.update({
        'pid'       : pobj.list('uid'),
        'npilot'    : len(pobj.get()),
        'npact'     : len(pobj.timestamps(state='PMGR_ACTIVE')),
    })

    # Task info
    sinfo.update({
        'ntask'     : len(tobj.get()),
        'ntdone'    : len(tobj.timestamps(state='DONE')),
        'ntcanceled': len(tobj.timestamps(state='CANCELED')),
        'ntfailed'  : len(tobj.timestamps(state='FAILED')),
    })

    # Derive info (assume a single pilot)
    sinfo.update({
        'pres'      : pobj.get(uid=sinfo['pid'])[0].description['resource'],
        'ncores'    : pobj.get(uid=sinfo['pid'])[0].description['cores'],
        'ngpus'     : pobj.get(uid=sinfo['pid'])[0].description['gpus']
    })
    sinfo.update({
        'nnodes'    : int(sinfo['ncores']/sinfo['cores_node'])
    })

Multiple Sessions
^^^^^^^^^^^^^^^^^

.. code-block:: python
   :linenos:

    ss = {}
    for sid in suds:
        sp = sdir+sid
        ss[sid] = {'s': ra.Session(sp, 'radical.pilot')}
        ss[sid].update({'p': ss[sid]['s'].filter(etype='pilot', inplace=False),
                        't': ss[sid]['s'].filter(etype='task', inplace=False)})

    for sid in suds:
    ss[sid].update({'sid'       : ss[sid]['s'].uid,
                    'lm'        : ss[sid]['s'].get(etype='pilot')[0].cfg['agent_launch_method'],
                    'hostid'    : ss[sid]['s'].get(etype='pilot')[0].cfg['hostid'],
                    'cores_node': ss[sid]['s'].get(etype='pilot')[0].cfg['resource_details']['rm_info']['cores_per_node'],
                    'gpus_node' : ss[sid]['s'].get(etype='pilot')[0].cfg['resource_details']['rm_info']['gpus_per_node'],
                    'smt'       : ss[sid]['s'].get(etype='pilot')[0].cfg['resource_details']['rm_info']['smt']
    })

    ss[sid].update({
                    'pid'       : ss[sid]['p'].list('uid'),
                    'npilot'    : len(ss[sid]['p'].get()),
                    'npact'     : len(ss[sid]['p'].timestamps(state='PMGR_ACTIVE'))
    })

    ss[sid].update({
                    'ntask'     : len(ss[sid]['t'].get()),
                    'ntdone'    : len(ss[sid]['t'].timestamps(state='DONE')),
                    'ntfailed'  : len(ss[sid]['t'].timestamps(state='FAILED')),
                    'ntcanceled': len(ss[sid]['t'].timestamps(state='CANCLED'))
    })


    ss[sid].update({'pres'      : ss[sid]['p'].get(uid=ss[sid]['pid'])[0].description['resource'],
                    'ncores'    : ss[sid]['p'].get(uid=ss[sid]['pid'])[0].description['cores'],
                    'ngpus'     : ss[sid]['p'].get(uid=ss[sid]['pid'])[0].description['gpus']
    })

    ss[sid].update({'nnodes'    : int(ss[sid]['ncores']/ss[sid]['cores_node'])})