#!/bin/sh
# This script appends a JSON object to file passed as first argument
# Example of invocation as a motion filter:
# /motion2json.sh /var/log/motion/events.json "%date%" "%host%" "%camera_id%"
# The last argument is added automatically when motion calls the filter

echo "{\"event_name\":\"picture_save\", \"date\":\"$2\",\"host\":\"$3\",\"camera_id\":\"$4\",\"event_id\":\"$5\", \"file\":\"$6\"}" >> $1
