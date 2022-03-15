#!/bin/bash

./extract_network.py ../Sample/campus.json > network.json
./percolation.py network.json
Rscript alpha.R
xdg-open budget-vs-alpha.png

