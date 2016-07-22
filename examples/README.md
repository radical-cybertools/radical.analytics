# How to Run the Examples

* Perform a run with a RADICAL-Cybertool that supports RADICAL-Analytics.
  Currently, the support has been implemented only for RADICAL-Pilot.
* Take note of the name of the session of your run. For example:
  `rp.session.thinkie.merzky.017003.0023`.
* Install RADICAL-Analytics:

    ```
    virtualenv --system-site-packages $HOME/ve
    source $HOME/ve/bin/activate
    pip install radical.analytics
    ```

* Install the chosen RADICAL-Cybertool in the same virtualenv. Assuming you
  are installing RADICAL-Pilot:

    ```
    pip install radical.pilot
    ```

* Execute the examples with `<example> <session_name>`. For example:

    ```
    ./00_session_describe_rp.py rp.session.thinkie.merzky.017003.0023
    ```

* Open the example file in your editor and read the comments to make sense of
  the output.
