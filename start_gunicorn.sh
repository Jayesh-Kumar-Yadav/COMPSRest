#!/bin/bash

gunicorn_paster -c gunicorn_config.py compsrest.ini
