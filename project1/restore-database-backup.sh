#!/bin/bash
export POSTGRES_PASSWORD=mysecretpassword
psql -h 10.0.2.15 -p 5432 -U postgres -f database-dump.psql