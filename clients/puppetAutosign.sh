#!/bin/bash

exit $(/opt/machineadmin/manage.py puppet_autosign $1)
