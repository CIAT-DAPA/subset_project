#!/usr/bin/env bash

# Execute restore in the background after 5s
# https://docs.docker.com/engine/reference/run/#detached--d
sleep 5 && mongorestore -d indicator --verbose /database/indicator/