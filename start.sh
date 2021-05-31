#!/usr/bin/env bash

cd detector
uvicorn main:node --host 0.0.0.0 --port 80 --reload --lifespan on