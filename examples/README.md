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

* Perform a run with RADICAL-Pilot and take note of the name of the session of your run. For example:
  `rp.session.thinkie.merzky.017003.0023`.

* Execute the examples with `<example> <session_name>`. For example:

  ```
  ./00_session_describe_rp.py rp.session.thinkie.merzky.017003.0023
  ```

* Open the example file in your editor and read the comments to make sense of
  the output.

* NOTE: The following:

  ```
  sid   = sys.argv[1]
  descr = rp.utils.get_session_description(sid=sid)
  prof = rp.utils.get_session_profile(sid=sid)
  ```

  looks for the session description (in JSON format) and for the profiles created for each component of RADICAL-Pilot in the current or indicated directory. If they cannot be found, the two methods download the session description from the MongoDB used with RADICAL-Pilot and the profiles from the resources on which the pilots and CU have been submitted and executed.
