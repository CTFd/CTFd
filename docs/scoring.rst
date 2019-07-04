Scoring
=======

Scoring is central to any CTF. CTFd automatically generates a scoreboard that automatically resolves ties and supports score freezing. CTFd supports two models which can alter the score of a user or team.

Solves
------
Solves are what mark a challenge as solved. Solves do not carry a value and defer to the value of their respective Challenge.

Awards
------
Awards have a value defined by their creator (usually an admin). They can be used to give a user/team arbitrary (positive or negative) points.

Tie Breaks
----------
In CTFd, tie breaks are essentially resolved by time. If two teams have the same score, the team with the lower solve ID in the database will be considered on top. For example Team X and Team Y solve the same challenge five minutes apart and both now have 100 points.

Team X will have a Solve ID of 1 for their submission and Team Y will have a Solve ID of 2 for their submission.

Thus Team X will be considered the tie winner.

Formats
-------

MajorLeagueCyber
~~~~~~~~~~~~~~~~
MajorLeagueCyber (MLC) is a cyber security event tracker designed and maintained by the developers of CTFd. It provides polling of the CTFd API and can record and aggregate scores between competitions/events. It supports parsing and processing of CTFd's built in scoreboard API format.

To register your event with MLC:

 1. Register an account at https://www.majorleaguecyber.org/ if you don't already have one.
 2. Create a new event.
 3. Edit the event and add the API Scoreboard URL under the Integrations section. For CTFd you should enter ``https://[CTFd Instance URL]/api/v1/scoreboard``
 4. Access the JSON scoreboard API from MajorLeagueCyber by going to ``https://www.majorleaguecyber.org/events/[EVENT_ID]/[EVENT_NAME]/scoreboard.json``

CTFTime
~~~~~~~
In prior versions CTFd supported a CTFTime compatible scoreboard. This is no longer directly supported because the CTFTime scoreboard format is inherently limiting. However, MLC allows for the polling of any JSON scoreboard API and can translate to the CTFTime scoreboard format.

After registering your event on MLC you can access the legacy scoreboard format by going to ``https://www.majorleaguecyber.org/events/[EVENT_ID]/[EVENT_NAME]/scoreboard.json?format=legacy``.