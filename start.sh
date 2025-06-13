#!/bin/bash

# Start the Django application with Gunicorn
gunicorn backend.wsgi:application 