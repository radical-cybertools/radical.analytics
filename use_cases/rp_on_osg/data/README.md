`osg_analysis_sample_dataset.tar.bz2` contains the data used in `devel/examples/jupyter/osg_analysis.ipynb`. Before executing osg_analysis in your Jupyter environment, you should unbzip and untar this archive by executing the following within the `data` directory:

```
tar xvfj osg_analysis_sample_dataset.tar.bz2
```

Please note:
* **DO NOT COMMIT** the uncompressed archive to github. The file osg_analysis_sample_dataset.tar.bz2 is tracked and managed via the git large storage addon (https://git-lfs.github.com/). If you modify or add new data, create a new compressed archive and use git-lfs to managed it in this repository.
* These data have been copied from: https://github.com/radical-experiments/AIMES-Experience/tree/master/synapse_integration_testing/experiments/osg_runs_exp1/late_uniform
