#!/bin/bash
pg_dumpall -h 10.0.2.15 -p 5432 -U postgres | tee database-dump.psql
