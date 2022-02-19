#!/bin/bash

./extract_network.py ../Sample/campus.json > network.json
./percolation.py network.json

