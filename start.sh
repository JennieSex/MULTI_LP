#!/bin/bash
DBport=56101
LPport=56001

trap 'kill 0' EXIT

./longpoll/lp 56011 &
./longpoll/lp 56022 &
./longpoll/lp 56033 &
./longpoll/lp 56044 &
./longpoll/lp 56055 &
./longpoll/lp 56066 &
./longpoll/lp 56077 &
./longpoll/lp 56088 &
./longpoll/lp 56099 &
./longpoll/lp 56110 &
./longpoll/lp 56101 &

cat | python3 Python4.py -lp1 56011 -lp2 56022 -lp3 56033 -lp4 56044 -lp5 56055 -lp6 56066 -lp7 56077 -lp8 56088 -lp9 56099 -lp10 56110
