#!/usr/bin/env bash

docker build -t miner_monitor .
docker run --name miner_monitor --rm -d -w /working -v $PWD:/working -v ssh:/working/.ssh miner_monitor
