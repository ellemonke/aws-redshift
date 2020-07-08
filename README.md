## Data Warehouse on AWS Redshift

A sample company, Sparkify, has provided song data (<s3://udacity-dend/song_data>) and log data (<s3://udacity-dend/log_data>) from their music streaming app in JSON format. The data is a sample subset of real data from the [Million Song Dataset](https://labrosa.ee.columbia.edu/millionsong/). The goal is to build an ETL pipeline that extracts the data from S3 buckets, stages it in AWS Redshift, and loads the data into a new set of dimensional tables. 

Sample of the song data:

`{"num_songs": 1, "artist_id": "ARJIE2Y1187B994AB7", "artist_latitude": null, "artist_longitude": null, "artist_location": "", "artist_name": "Line Renaud", "song_id": "SOUPIRU12A6D4FA1E1", "title": "Der Kleine Dompfaff", "duration": 152.92036, "year": 0}`

Sample of the log data:

<img src="log-data.png">

<hr>

### 1. Create an AWS Redshift Cluster
- Complete the initial data warehouse configuration in [dwh.cfg](dwh.cfg) under the following sections.
   - [AWS]
   - [DWH]
- Run the notebook [connect.ipynb](connect.ipynb) to create an IAM Role and Redshift Cluster. 
- After the cluster is finished being added, take note of the cluster endpoint and role ARN that are created. 

   For example: 
   - DWH_ENDPOINT ::  redshift-cluster.xxxxxxxxxxxx.us-west-2.redshift.amazonaws.com
   - DWH_ROLE_ARN ::  arn:aws:iam::xxxxxxxxxxxx:role/dwhRole
- Complete the cluster configuration in [dwh.cfg](dwh.cfg) under the following sections where 'HOST' is the 'DWH_ENDPOINT' and 'ARN' is the 'DWH_ROLE_ARN'.
   - [CLUSTER]

      HOST = 'redshift-cluster.xxxxxxxxxxxx.us-west-2.redshift.amazonaws.com'
   - [IAM_ROLE]

      ARN = 'arn:aws:iam::xxxxxxxxxxxx:role/dwhRole'

<hr>

### 2. Create a star schema of tables in the database
- Run `python create_tables.py` in Bash/Terminal. The file [create_tables.py](create_tables.py) creates a connection to the cluster, drops any old tables, and create new empty tables. The queries are pulled from [sql_queries.py](sql_queries.py). 

- The tables created include:

   #### 1. `staging_events` (copy of log data)

   #### 2. `staging_songs` (copy of song data) 

   #### 3. `songplays` (fact table)
   | Column Name | Data Source | 
   | ----------- | ----------- | 
   | `songplay_id` | IDENTITY(0,1) PRIMARY KEY | 
   | `start_time` | `ts` from `staging_events` |
   | `user_id` | `userId` from `staging_events` |
   | `level` | `level` from `staging_events` |
   | `song_id` | `song_id` from `staging_songs` |
   | `artist_id` | `artist_id` from `staging_songs` |
   | `session_id` | `sessionId` from `staging_events` |
   | `location` | `location` from `staging_events` |
   | `user_agent` | `userAgent` from `staging_events` |

   #### 4. `users` (dimension table)
   | Column Name | Data Source | 
   | ----------- | ----------- |
   | `user_id` | `userId` from `staging_events` |
   | `first_name ` | `firstName` from `staging_events` |
   | `last_name` | `lastName` from `staging_events` |
   | `gender ` | `gender` from `staging_events` |
   | `level ` | `level` from `staging_events` |

   #### 5. `songs` (dimension table)
   | Column Name | Data Source |
   | ----------- | ----------- | 
   | `song_id` | `song_id` from `staging_songs` |
   | `title` | `title` from `staging_songs` |
   | `artist_id` | `artist_id` from `staging_songs` |
   | `year` | `year` from `staging_songs` |
   | `duration` | `duration` from `staging_songs` |

   #### 6. `artists` (dimension table)
   | Column Name | Data Source | 
   | ----------- | ----------- | 
   | `artist_id` | `artist_id` from `staging_songs` |
   | `name` | `artist_name` from `staging_songs` |
   | `location` | `artist_location` from `staging_songs` |
   | `latitude` | `artist_latitude` from `staging_songs` |
   | `longitude` | `artist_longitude` from `staging_songs` |

   #### 7. `time` (dimension table)
   | Column Name | Data Source | 
   | ----------- | ----------- | 
   | `start_time` | `ts` from `staging_events` converted to timestamp |
   | `hour` | hour parsed from `start_time` | 
   | `day` | day parsed from `start_time` | 
   | `week` | week parsed from `start_time` | 
   | `month` | month parsed from `start_time` | 
   | `year` | year parsed from `start_time` | 
   | `weekday` | day of week parsed from `start_time` | 

<hr>

### 3. Create an ETL Pipeline
- Run `python etl.py` in Bash/Terminal. The file [etl.py](etl.py) creates a connection to the cluster and runs SQL queries from [sql_queries.py](sql_queries.py).

   1. **EXTRACT**
      - Data is copied from <s3://udacity-dend/log_data> to `staging_events` and from <s3://udacity-dend/song_data> to `staging_songs` using COPY statements.
   2. **TRANSFORM**
      - In `staging_events` table, the column `ts` refers to the event timestamp. This must be transformed from epoch format to timestamp format `YYYY-MM-DD HH:MI:SS`, then named `start_time` to fit into the `time` table.
      - Then the `hour`, `day`, `week`, `month`, `year`, and `weekday` can be parsed from `start_time` to also go into the `time` table.
   3. **TRANSFORM/LOAD**
      - Data is inserted into the tables according to the star schema above using INSERT INTO statements.

<hr>

### 4. Clean up created resources
- Once the work has been completed and/or the cluster is no longer needed, open the file [connect.ipynb](connect.ipynb). 
- Go to the last section 'Clean up created resources'.
- Uncomment the cells in this section and run them to delete the Redshift cluster and attached IAM role(s). 

**IMPORTANT: All relevant Redshift clusters must be deleted to ensure they are no longer being charged to your account.**