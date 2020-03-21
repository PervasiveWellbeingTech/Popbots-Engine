#!/bin/bash
nohup python3 slack_socket.py &> ~/nohup_slack.out &
nohup python3 telegram_socket.py &> ~/nohup_telegram.out &