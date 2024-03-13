#!/usr/bin/python2.7
# Assignment4 Interface

import psycopg2
import os
import sys

DATABASE_NAME = 'dds_assignment'
RANGE_TABLE_PREFIX = 'RangeRatingsPart'
RROBIN_TABLE_PREFIX = 'RoundRobinRatingsPart'
RANGE_METADATA_TABLE = 'RangeRatingsMetadata'
RROBIN_METADATA_TABLE = 'RoundRobinRatingsMetadata'

def RangeQuery(ratingsTableName, ratingMinValue, ratingMaxValue, openconnection):
    cursor_ptr = openconnection.cursor()
    #Getting range partition tuples
    cursor_ptr.execute(
        "select PartitionNum from %s where MinRating between %s AND %s OR MaxRating between %s AND %s"
        % (RANGE_METADATA_TABLE, ratingMinValue, ratingMaxValue, ratingMinValue, ratingMaxValue)
    )
    rows = []
    for partition in cursor_ptr.fetchall():
        partition_name = RANGE_TABLE_PREFIX + str(partition[0])
        cursor_ptr.execute(
            "select * from %s where Rating between %s AND %s "
            % (partition_name, ratingMinValue, ratingMaxValue)
        )
        tuples = cursor_ptr.fetchall()
        for row in tuples:
            rows.append([partition_name] + list(row))
    #Get Round robin partition tuples
    cursor_ptr.execute(
        "select table_name from information_schema.tables where table_name like 'roundrobinratingspart%'"
    )
    partition_names = cursor_ptr.fetchall()
    for partName in partition_names:
        partName = partName[0]
        cursor_ptr.execute(
            "select * from %s where Rating between %s AND %s "
            % (partName, ratingMinValue, ratingMaxValue)
        )
        tuples = cursor_ptr.fetchall()
        for row in tuples:
            rows.append([partName] + list(row))
    writeToFile("RangeQueryOut.txt", rows)

def PointQuery(ratingsTableName, ratingValue, openconnection):
    cursor_ptr = openconnection.cursor()
    #Getting range partition tuples
    cursor_ptr.execute(
        "select PartitionNum from %s where %s between MinRating AND MaxRating"
        % (RANGE_METADATA_TABLE, ratingValue)
    )
    rows = []
    for partition in cursor_ptr.fetchall():
        partition_name = RANGE_TABLE_PREFIX + str(partition[0])
        cursor_ptr.execute(
            "select * from %s where Rating = %s"
            % (partition_name, ratingValue)
        )
        for row in cursor_ptr.fetchall():
            rows.append([partition_name] + list(row))
    #Get Round robin partition tuples
    cursor_ptr.execute(
        "select table_name from information_schema.tables where table_name LIKE 'roundrobinratingspart%'"
    )
    for partName in cursor_ptr.fetchall():
        partName = partName[0]
        cursor_ptr.execute(
            "SELECT * FROM %s WHERE Rating = %s "
            % (partName, ratingValue)
        )
        for row in cursor_ptr.fetchall():
            rows.append([partName] + list(row))
    writeToFile("PointQueryOut.txt", rows)

def writeToFile(filename, rows):
    f = open(filename, 'w')
    for line in rows:
        f.write(','.join(str(s) for s in line))
        f.write('\n')
    f.close()
