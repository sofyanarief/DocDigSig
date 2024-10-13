#!/bin/bash

i=1
./home/engine/Documents/Penelitian-2024/apache-jmeter-5.6.2/bin/jmeter.sh -n -t "/home/engine/Documents/Penelitian-2024/Test-Plan-Dynamic-User.jmx" -l "/home/engine/Documents/Penelitian-2024/${i}-user.csv" -Jusers=$i -JcsvFilename="/home/engine/Documents/Penelitian-2024/user_keys.csv"
sleep 60
for i in $(seq 5 5 100)
do
    ./home/engine/Documents/Penelitian-2024/apache-jmeter-5.6.2/bin/jmeter.sh -n -t "/home/engine/Documents/Penelitian-2024/Test-Plan-Dynamic-User.jmx" -l "/home/engine/Documents/Penelitian-2024/${i}-user.csv" -Jusers=$i -JcsvFilename="/home/engine/Documents/Penelitian-2024/user_keys.csv"
    sleep 60
done