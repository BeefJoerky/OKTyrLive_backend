Author: Gustav Jörg
Date: 2025

To set up the server:
1. Make sure dependencies are installed. These are found in requirements.txt
2. Set up a database by running mopDB_setup.sql
3. Configure a user. By default the program uses "mop" and "mop" as username and password. The host can also be configured in the program.
4. Run mop_server.py

A server is now listening on localhost:5000/data. This can be configured in MeOS as the place to send data to.
