#!/usr/bin/env python

import os
import sys
import random

import radical.utils as ru
import radical.pilot as rp


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if not sys.argv[1]:
        sys.exit()
    pcfg = ru.Config(path=sys.argv[1])

    with rp.Session(download=True) as session:

        pmgr = rp.PilotManager(session=session)
        pd_init = {'resource': 'local.localhost',
                   'runtime' : pcfg.runtime,
                   'cores'   : pcfg.cores,
                   'gpus'    : pcfg.gpus}

        pdesc = rp.PilotDescription(pd_init)
        pilot = pmgr.submit_pilots(pdesc)
        tmgr  = rp.TaskManager(session=session)
        tmgr.add_pilots(pilot)

        n = pcfg.files
        tds = list()
        for i in range(0, n):

            td = rp.TaskDescription()
            td.executable     = '%s/radical-pilot-hello.sh' % os.getcwd()
            td.arguments      = [random.randint(1, 10)]
            td.ranks          =  random.randint(1, 8)
            td.cores_per_rank =  random.randint(1, 8)
            td.gpus_per_rank  =  random.randint(0, 2)
            tds.append(td)

        tmgr.submit_tasks(tds)
        tmgr.wait_tasks()
