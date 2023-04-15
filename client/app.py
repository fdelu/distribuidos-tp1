#!/usr/bin/python3
import logging
import zmq
import os
from common.log import setup_logs

setup_logs()

DATA_PATH = "/tmp/data"
context = zmq.Context()

#  Socket to talk to server
print("Connecting to the server")
socket = context.socket(zmq.REQ)

socket.connect("tcp://server:5555")

# print contents of directory DATA_PATH
cities = os.listdir(DATA_PATH)

for city in cities:
    logging.info(f"Sending data for {city}")
