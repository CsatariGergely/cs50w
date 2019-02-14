#!/bin/bash
set -x
docker rm postgres-books
docker run --name postgres-books -e POSTGRES_PASSWORD=mysecretpassword -d -p 5432:5432 postgres-books