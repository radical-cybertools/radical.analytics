# How to Run the Examples

* Install RADICAL-Analytics:  
  ```
  virtualenv --system-site-packages $HOME/ve
  source $HOME/ve/bin/activate
  pip install radical.analytics
  ```

* Install the chosen RADICAL-Cybertool in the same virtualenv.
  Currently, RADICAL-Analytics supports only:  
  ```
  pip install radical.pilot
  ```  
  **NOTE: At the moment, only the `analytics` branch of RP works with RADICAL-Analytics**:
  ```  
  git clone git@github.com:radical-cybertools/radical.pilot.git
  git checkout analytics
  pip install --upgrade .
  ```

* Perform a run with RADICAL-Pilot and take note of the name of the session of your run. For example:  
  ```
  rp.session.thinkie.merzky.017003.0023
  ```  
  NOTE: RADICAL-Analytics requires the profile files for every RP component (e.g., pilot, umgr, or pmgr) and the an aggregated json file of the session as downloaded from the MongoDB server used to run the RP session (e.g., `rp.session.radical.mingtha.017035.0010.json`). These files need to be collected into a directory named with the name of the session, with the following structure:  
  ```
  rp.session.radical.mingtha.017035.0010\
    pilot.0000/
    pilot.0001/
    pilot.000*/
    *.prof
    *.json
  ```  
  Only a single json file is allowed in the directory. An error should be thrown by the script utilizing RADICAL-Analytics when more than one json file is present (to be implemented in RADICAL-Analytics soon).

* Execute the examples with `<example> <session_name>`. For example:  
  ```
  ./00_session_describe_rp.py rp.session.thinkie.merzky.017003.0023
  ```

* Open the example file in your editor and read the comments to make sense of
  the output.

* In every example, the following:  
  ```
  sid = sys.argv[1]
  descr = rp.utils.get_session_description(sid=sid)
  prof = rp.utils.get_session_profile(sid=sid)
  ```  
  looks for the session description (in JSON format) and for the profiles created for each component of RADICAL-Pilot in the current or indicated directory. If they cannot be found, the two methods download the session description from the MongoDB used with RADICAL-Pilot and the profiles from the resources on which the pilots and CU have been submitted and executed.
