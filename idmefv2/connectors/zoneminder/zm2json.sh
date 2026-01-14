#!/bin/sh
# This script appends a JSON object to file passed as first argument
# Example of invocation as a zoneminder filter:
# /zm2json.sh /var/log/zmjson/events.json "%ET%" "%ED%" "%MN%"
# The last argument is added automatically when zoneminder calls the filter

echo "{\"ET\":\"$2\",\"ED\":\"$3\",\"MN\":\"$4\",\"EDP\":\"$5\"}" >> $1
