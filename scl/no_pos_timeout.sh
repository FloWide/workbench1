#!/bin/bash

MS_SINCE_LAST_RESULT=`curl -sS http://127.0.0.1:80/taskInfo/statistics | jq -r '.[]  | select(.type == "TagTdoaSetPositionComputationTask") | .msSinceLatestTaskResult'`
echo "$MS_SINCE_LAST_RESULT milliseconds since last position calculation"

if [[ $MS_SINCE_LAST_RESULT -gt $SCL_NO_POSITION_TIMEOUT ]] || [[ "$MS_SINCE_LAST_RESULT" -eq "null" ]]; then
    exit 1
fi