# How to Run the Examples

* Install RADICAL-Analytics:  
  ```
  virtualenv --system-site-packages $HOME/ve
  source $HOME/ve/bin/activate
  pip install radical.analytics
  ```

* Install the chosen RADICAL-Cybertool in the same virtualenv.
  Currently, RADICAL-Analytics supports only the `analytics` branch of RP:
  ```  
  git clone git@github.com:radical-cybertools/radical.pilot.git
  cd radical.pilot
  git checkout analytics
  pip install --upgrade .
  ```

* Perform a run with RADICAL-Pilot and take note of the name of the session of your run. For example:  
  ```
  rp.session.thinkie.merzky.017003.0023
  ```  
  NOTE: RADICAL-Analytics requires the profile files for every RP component (e.g., pilot, umgr, or pmgr) and the an aggregated json file of the session as downloaded from the MongoDB server used to run the RP session (e.g., `rp.session.radical.mingtha.017035.0010.json`). These files need to be collected into a directory named with the name of the session. Files have to be organized with the following structure:  
  ```
  rp.session.radical.mingtha.017035.0010\
    pilot.0000/*.prof
    pilot.0001/*.prof
    pilot.000*/*.prof
    *.prof
    *.json
  ```  
  Currently, only a single file with extension `.json` is allowed in the directory.

* Execute the examples with `<example> <src_data_dir>`. For example:  
  ```
  ./00_session_describe_rp.py rp.session.thinkie.merzky.017003.0023
  ```

* Open the example file in your editor and read the comments to make sense of
  the output.

* In every example, the following:  
  ```
  src = sys.argv[1]
  json_file = json_files[0]
    json      = ru.read_json(json_file)
    sid       = os.path.basename(json_file)[:-5]

  session = ra.Session(sid, 'radical.pilot', src=src)
  ```  
  looks for the session description (in JSON format) and for the profiles created for each component of RADICAL-Pilot in the indicated `src` directory. If these files cannot be found, the `ra.Session()` constructor downloads the session description from the MongoDB used with RADICAL-Pilot and the profiles from the resources on which the pilots and CU have been submitted and executed.
