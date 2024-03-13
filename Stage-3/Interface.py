#!/usr/bin/python2.7
#
# Interface for the assignement
#

import psycopg2

# Variables
CREATE_TABLE_COMMAND = "Create TABLE "
ALTER_TABLE_COMMAND = "ALTER TABLE "
RANGE_PARTITION_NAMESPACE = "range_part"
ROUND_ROBIN_PARTITION_NAMESPACE = "rrobin_part"
INSERT_INTO_COMMAND = "insert into "
RATINGS_COLUMNS_VALUES_COMMAND = "(userid,movieid,rating) values ("

def getOpenConnection(user='postgres', password='1234', dbname='postgres'):
    return psycopg2.connect("dbname='" + dbname + "' user='" + user + "' host='localhost' password='" + password + "'")


# This Function will load the data into the table - ratings
def loadRatings(ratings_table_name, ratings_file_path, openconnection):
    # open a connection object
    databaseCursor = openconnection.cursor()

    # This will drop the table if already exists
    drop_query = "DROP TABLE IF EXISTS " + ratings_table_name;
    databaseCursor.execute(drop_query)

    # This will create a new table with following columns - userid, t1, movieid, t2, rating, t3, timestamp
    create_query = "create table " + ratings_table_name + " (userid int not null, t1 varchar, movieid int, t2 varchar, rating float, t3 varchar, timestamp bigint)"
    databaseCursor.execute(create_query)

    # This will open a pointer to the data file.
    data = open(ratings_file_path, "r")

    # This will push the data from the file to the database.
    # Data file contains extra columns in between.
    databaseCursor.copy_from(
        data,
        ratings_table_name,
        sep=":",
        columns=("userid", "t1", "movieid", "t2", "rating", "t3", "timestamp"),
    )

    # This will remove the un-necessary columns - t1, t2, t3, timestamp from the table
    query = "alter table " + ratings_table_name + " DROP COLUMN t1, DROP COLUMN t2, DROP COLUMN t3, DROP COLUMN timestamp"
    databaseCursor.execute(query)

    # close and propogate the changes.
    databaseCursor.close()
    openconnection.commit()


# This is a Range Partition Function
def rangePartition(ratings_table_name, number_of_partitions, openconnection):

    part_values = round((5 / number_of_partitions), 2)

    database_cursor = openconnection.cursor()
    b = 0

    for part_index in range(0, number_of_partitions):

        if part_index == 0:

            database_cursor.execute("create table range_part{0} AS SELECT * FROM {3} where rating>={1} and rating<={2};".format(part_index, str(0), str(part_values), ratings_table_name))

            b = part_values

        else:

            database_cursor.execute("create table range_part{0} AS SELECT * FROM {3} where rating>{1} and rating<={2};".format(part_index, str(b), str(b + part_values), ratings_table_name))

            b = b + part_values
        
    openconnection.commit()
    database_cursor.close()

# This is a Round Robin Partition
def roundRobinPartition(ratingstablename, numberofpartitions, openconnection):
    partitions_array = []
    database_cursor = openconnection.cursor()

    part_name = ROUND_ROBIN_PARTITION_NAMESPACE

    for part_index in range(0, numberofpartitions):
        partitions_array.append((part_name + str(part_index)))
    
    for part_index in range(0, numberofpartitions):

        create_query = "create table rrobin_part{0} (userid INT, movieid INT, rating FLOAT)".format(part_index)
        database_cursor.execute(create_query)

        if part_index != numberofpartitions - 1:

            database_cursor.execute(
                INSERT_INTO_COMMAND
                + partitions_array[part_index]
                + " select userid,movieid,rating from (select row_number() over() as row_id, * from "
                + ratingstablename
                + ") as imp where row_id%"
                + str(numberofpartitions)
                + "="
                + str(part_index + 1)
            )

        else:

            database_cursor.execute(
                INSERT_INTO_COMMAND
                + partitions_array[part_index]
                + " select userid,movieid,rating from (select row_number() over() as row_id, * from "
                + ratingstablename
                + ") as imp where row_id%"
                + str(numberofpartitions)
                + "="
                + str(0)
            )
        
    openconnection.commit()

# This is a RoundRobin Insert FUnction
def roundrobininsert(ratingstablename, userid, itemid, rating, openconnection):
    if rating < 0 or rating > 5:
        return
    database_cursor = openconnection.cursor()
    database_cursor.execute(
        "select count(*) from (SELECT tablename FROM pg_catalog.pg_tables WHERE tablename like 'rrobin_part%') as temp"
    )
    partition_count = int(database_cursor.fetchone()[0])
    database_cursor.execute("SELECT COUNT(*) from {}".format(ratingstablename))
    dataset_count = int(database_cursor.fetchone()[0])
    part_name = ROUND_ROBIN_PARTITION_NAMESPACE + str((dataset_count % partition_count))
    database_cursor.execute(
        INSERT_INTO_COMMAND
        + ratingstablename
        + RATINGS_COLUMNS_VALUES_COMMAND
        + str(userid)
        + ","
        + str(itemid)
        + ","
        + str(rating)
        + ")"
    )
    database_cursor.execute(
        INSERT_INTO_COMMAND
        + part_name
        + RATINGS_COLUMNS_VALUES_COMMAND
        + str(userid)
        + ","
        + str(itemid)
        + ","
        + str(rating)
        + ")"
    )
    openconnection.commit()

# This is a Range Insert
def rangeinsert(ratingstablename, userid, itemid, rating, openconnection):
    if rating < 0 or rating > 5:
        return
    database_cursor = openconnection.cursor()
    database_cursor.execute(
        "select count(*) from (SELECT tablename FROM pg_catalog.pg_tables WHERE tablename like 'range_part%') as temp"
    )
    count_of_partition = int(database_cursor.fetchone()[0])
    part_values = round((5 / count_of_partition), 2)
    partition_count = int(rating / part_values)
    if rating % part_values == 0 and partition_count != 0:
        partition_count = partition_count - 1
    part_name = RANGE_PARTITION_NAMESPACE + str(partition_count)
    database_cursor.execute(
        INSERT_INTO_COMMAND
        + ratingstablename
        + RATINGS_COLUMNS_VALUES_COMMAND
        + str(userid)
        + ","
        + str(itemid)
        + ","
        + str(rating)
        + ")"
    )
    openconnection.commit()
    database_cursor.execute(
        INSERT_INTO_COMMAND
        + part_name
        + RATINGS_COLUMNS_VALUES_COMMAND
        + str(userid)
        + ","
        + str(itemid)
        + ","
        + str(rating)
        + ")"
    )
    openconnection.commit()

def createDB(dbname='dds_assignment'):
    """
    We create a DB by connecting to the default user and database of Postgres
    The function first checks if an existing database exists for a given name, else creates it.
    :return:None
    """
    # Connect to the default database
    con = getOpenConnection(dbname='postgres')
    con.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    # Check if an existing database with the same name exists
    cur.execute('SELECT COUNT(*) FROM pg_catalog.pg_database WHERE datname=\'%s\'' % (dbname,))
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute('CREATE DATABASE %s' % (dbname,))  # Create the database
    else:
        print 'A database named {0} already exists'.format(dbname)

    # Clean up
    cur.close()
    con.close()

def deletepartitionsandexit(openconnection):
    cur = openconnection.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    l = []
    for row in cur:
        l.append(row[0])
    for tablename in l:
        cur.execute("drop table if exists {0} CASCADE".format(tablename))

    cur.close()

def deleteTables(ratingstablename, openconnection):
    try:
        cursor = openconnection.cursor()
        if ratingstablename.upper() == 'ALL':
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = cursor.fetchall()
            for table_name in tables:
                cursor.execute('DROP TABLE %s CASCADE' % (table_name[0]))
        else:
            cursor.execute('DROP TABLE %s CASCADE' % (ratingstablename))
        openconnection.commit()
    except psycopg2.DatabaseError, e:
        if openconnection:
            openconnection.rollback()
        print 'Error %s' % e
    except IOError, e:
        if openconnection:
            openconnection.rollback()
        print 'Error %s' % e
    finally:
        if cursor:
            cursor.close()
