#!/bin/bash
ncat -l 10.0.0.7 81 --sh-exec "ncat localhost 81" &
python3 -u quickstart.py