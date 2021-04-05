import configparser
from datetime import datetime
import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format


def create_spark_session():
    """Create an apache spark session on AWS"""
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    """Load data from song_data dataset and extract columns
    for songs and artist tables. While writing songs table,
    write the data into parquet files to be loaded on S3
    
    spark: session created from the create_spark_session
    input_data: path input from the song_data s3 bucket
    output_data: path to where the parquet file will be written
    """
    # get filepath to song data file
    song_data = os.path.join(input_data, 'song_data/*/*/*/*.json')
    
    # read song data file
    df = spark.read.json(song_data)

    # extract columns to create songs table
    songs_table = df['song_id', 'title', 'artist_id', 'year', 'duration']
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.withColumn('_year', df.year).withColumn('_artist_id', df.artist_id)\
        .write.partitionBy(['_year', '_artist_id']).parquet(os.parth.join(output_data, 'songs'), 'overwrite')

    # extract columns to create artists table
    artists_table = df['artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_longitude']
    artists_table = artists_table.drop_duplicates(subset=['artist_id'])
    
    # write artists table to parquet files
    artists_table.write.parquet(os.path.join(output_data, 'artists'), 'overwrite')


def process_log_data(spark, input_data, output_data):
    """Load data from log_data dataset and extract columns
    for users and time tables. While writing user table,
    write the data inot parquet files to be loaded on S3
    
    spark: sesion created from the create_spark_session
    input_data: path input from the log_data s3 bucket
    output_data: path to where the parquet file will be written
    """
    
    
    # get filepath to log data file
    log_data = os.path.join(input_data, 'log_data/*/*/*.json')

    # read log data file
    df = spark.read.json(log_data)
    
    # filter by actions for song plays
    df = df.filter(df.page == 'NextSong')

    # extract columns for users table    
    users_table = df['userId', 'firstName', 'lastName', 'gender', 'level']
    users_table = users_table.drop_duplicates(subset='userId')
    
    # write users table to parquet files
    users_tables.write.parquet(os.path.join(output_data, 'users'), 'overwrite')

    # create datetime column from original timestamp column
    get_timestamp = F.udf(lambda ts: datetime.fromtimestamp(ts // 1000), DateType())
    df = df.withColumn('datetime', get_datetime(df.ts))
        
    # extract columns to create time table
    time_table = df.select(
        F.col('datetime').alias('start_time'),
        F.hour('datetime').alias('hour'),
        F.dayofmonth('datetime').alias('day'),
        F.weekofyear('datetime').alias('year'),
        F.month('datetime').alias('month'),
        F.year('datetime').alias('year'),
        F.date_format('datetime', 'u').alias('weekday')
    )
    time_table = time_table.drop_duplicates(subset=['start_time'])
    
    # write time table to parquet files partitioned by year and month
    time_table.write.partitionBy(['year', 'month']).parquet(os.path.join(output_data, 'time'), 'overwrite')

    # read in song data to use for songplays table
    song_df = spark.read.parquet(os.path.join(output_data, 'songs/_year=*/_artist_id=*/*.parquet'))

    # extract columns from joined song and log datasets to create songplays table 
    df = df['datetime', 'userId', 'level', 'song', 'artist', 'sessionId', 'location', 'userAgent']
    
    log_song_df = df.join(song_df, df.song == song_df.title)
    
    songplays_table = log_song_df.select(
        F.monotonically_increasing_id().alias('songplay_id'),
        F.col('datetime').alias('start_time'),
        F.year('datetime').alias('year'),
        F.month('datetime').alias ('month'),
        F.col('userId').alias('user_id'),
        'level',
        'song_id',
        'artist_id',
        F.col('sessionId').alias('session_id'),
        'location',
        F.col('userAgent').alias('user_agent')
    )

    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.partitionBy("year", "month").parquet(os.path.join(output_data, "songplays.parquet"), "overwrite")


def main():
    """Function to create a spark ses"""
    
    
    if len(sys.argv) == 3:
        input_data = sys.argv[1]
        output_data = sys.argv[2]
    else:
        config = configparser.ConfigParser()
        config.read('dl.cfg')
        
        os.environ['AWS_ACCESS_KEY_ID'] = config['AWS']['AWS_ACCESS_KEY_ID']
        os.environ['AWS_SECRET_ACCESS_KEY'] = config['AWS']['AWS_SECRET_ACCESS_KEY']
        
        input_data = config['DATALAKE']['INPUT_DATA']
        output_data = config['DATALAKE']['OUTPUT_DATA']
        
    spark = create_spark_session()
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
