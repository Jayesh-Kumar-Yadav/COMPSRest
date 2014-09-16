#!/bin/bash

gunicorn --log-file=- --debug --paste compsrest.ini
