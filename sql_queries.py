import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE IF NOT EXISTS staging_events ( 
    artist varchar, 
    auth varchar, 
    firstName varchar, 
    gender varchar(1), 
    itemInSession int, 
    lastName varchar, 
    length float, 
    level varchar, 
    location varchar, 
    method varchar, 
    page varchar, 
    registration float, 
    sessionId int, 
    song varchar, 
    status int, 
    ts bigint, 
    userAgent varchar, 
    userId int);
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs ( 
    num_songs int, 
    artist_id varchar, 
    artist_latitude float, 
    artist_longitude float, 
    artist_location varchar, 
    artist_name varchar, 
    song_id varchar, 
    title varchar, 
    duration float, 
    year int);
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplays ( 
    songplay_id int IDENTITY(0,1) PRIMARY KEY, 
    start_time bigint NOT NULL, 
    user_id int NOT NULL, 
    level varchar NOT NULL, 
    song_id varchar, 
    artist_id varchar, 
    session_id int NOT NULL, 
    location varchar NOT NULL, 
    user_agent varchar NOT NULL);
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS users ( 
    user_id int PRIMARY KEY, 
    first_name varchar NOT NULL, 
    last_name varchar NOT NULL, 
    gender varchar(1), 
    level varchar);
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS songs ( 
    song_id varchar PRIMARY KEY, 
    title varchar NOT NULL,
    artist_id varchar NOT NULL, 
    year int, 
    duration float NOT NULL);
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS artists (
    artist_id varchar PRIMARY KEY, 
    name varchar NOT NULL, 
    location varchar, 
    latitude float, 
    longitude float);
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time ( 
    start_time varchar PRIMARY KEY, 
    hour int NOT NULL, 
    day int NOT NULL, 
    week int NOT NULL, 
    month int NOT NULL, 
    year int NOT NULL, 
    weekday int NOT NULL);
""")

# STAGING TABLES

staging_events_copy = ("""
    copy staging_events from 's3://udacity-dend/log_data'
    credentials 'aws_iam_role={}'
    region 'us-west-2' 
    format as json 's3://udacity-dend/log_json_path.json';
""").format(config['IAM_ROLE']['ARN'])

staging_songs_copy = ("""
    copy staging_songs from 's3://udacity-dend/song_data'
    credentials 'aws_iam_role={}'
    region 'us-west-2'
    json 'auto';
""").format(config['IAM_ROLE']['ARN'])

# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO songplays (
    start_time,
    user_id, 
    level, 
    song_id, 
    artist_id, 
    session_id, 
    location, 
    user_agent) 
SELECT e.ts as start_time,
    e.userId as user_id,
    e.level as level,
    s.song_id as song_id,
    s.artist_id as artist_id,
    e.sessionId as session_id,
    e.location as location,
    e.userAgent as user_agent
FROM staging_events e
JOIN staging_songs s ON (e.song = s.title AND e.artist = s.artist_name) 
""")

user_table_insert = ("""
INSERT INTO users (
    user_id, 
    first_name, 
    last_name, 
    gender, 
    level) 
SELECT DISTINCT e.userId as user_id,
    e.firstName as first_name,
    e.lastName as last_name,
    e.gender as gender,
    e.level as level
FROM staging_events e
WHERE user_id IS NOT NULL
""")

song_table_insert = ("""
INSERT INTO songs (
    song_id, 
    title, 
    artist_id, 
    year, 
    duration) 
SELECT DISTINCT s.song_id as song_id,
    s.title as title,
    s.artist_id as artist_id,
    s.year as year,
    s.duration as duration
FROM staging_songs s
""")

artist_table_insert = ("""
INSERT INTO artists (
    artist_id, 
    name, 
    location, 
    latitude, 
    longitude) 
SELECT DISTINCT s.artist_id as artist_id,
    s.artist_name as name,
    s.artist_location as location,
    s.artist_latitude as latitude,
    s.artist_longitude as longitude
FROM staging_songs s
""")

time_table_insert = ("""
INSERT INTO time (
    start_time, 
    hour, 
    day, 
    week, 
    month, 
    year, 
    weekday) 
SELECT timestamp 'epoch' + CAST(e.ts AS BIGINT)/1000 * interval '1 second' as start_time,
    DATE_PART(h, timestamp 'epoch' + CAST(e.ts AS BIGINT)/1000 * interval '1 second') as hour,
    DATE_PART(d, timestamp 'epoch' + CAST(e.ts AS BIGINT)/1000 * interval '1 second') as day,
    DATE_PART(w, timestamp 'epoch' + CAST(e.ts AS BIGINT)/1000 * interval '1 second') as week,
    DATE_PART(mon, timestamp 'epoch' + CAST(e.ts AS BIGINT)/1000 * interval '1 second') as month,
    DATE_PART(y, timestamp 'epoch' + CAST(e.ts AS BIGINT)/1000 * interval '1 second') as year,
    DATE_PART(dow, timestamp 'epoch' + CAST(e.ts AS BIGINT)/1000 * interval '1 second') as weekday
FROM staging_events e
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
