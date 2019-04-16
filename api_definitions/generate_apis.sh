#!/bin/bash

echo '{
  "username": "user8",
  "department": "admin",
  "apis": [
'

n=100

for (( i=1; i<=n; i++ ))
do
   echo '    {
      "name": "CJAMS_DEV1_ACCESSLIST_API_'$i'",
      "description": "ACCESSLIST_API_'$i'",
      "context": "/api/cjams/dev1/accesslist'$i'",
      "version": "v1"
    }'
   
   if (( $i < n ))
   then
      echo ','
   fi
done

echo '  ]
}'
