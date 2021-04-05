# Project: Data Lake with Spark
completed by Ken Jung, as part of the Udacity Data Engineering Nanodegree Program


### Introduction
A music streaming startup, Sparkify, has grown their user base and song database even more and want to move their data warehouse to a data lake. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

As their data engineer, you are tasked with building an ETL pipeline that extracts their data from S3, processes them using Spark, and loads the data back into S3 as a set of dimensional tables. This will allow their analytics team to continue finding insights in what songs their users are listening to.


### Instruction
- Populate the Fact Table & Dimension Table
- Create AWS credentials to execute etl.py file

*Fact Table*
- songplays (records in log data associated with song plays): songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent

*Dimension Tables*
- users (users in the app): user_id, first_name, last_name, gender, level
- songs (songs in music database): song_id, title, artist_id, year, duration
- artists (artists in music database): artist_id, name, location, lattitude, longitude
- time (timestamps of records in songplays broken down into specific units): start_time, hour, day, week, month, year, weekday


### Project Workspace and Files
- dl.cfg: Configuration file with AWS credential information
- etl.py: ETL script