#!/usr/bin/env bash

uvicorn main:node --host 0.0.0.0 --port 80 --reload --lifespan on