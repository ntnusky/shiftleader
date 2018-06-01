#!/bin/bash

# Run r10k to discover new environments
/usr/bin/r10k deploy environment production

for env in $(/opt/shiftleader/manage.py puppet_env2list); do
  if [[ $(/opt/shiftleader/manage.py puppet_env2update $env) -eq '1' ]]; then
    echo "Running r10k to update $env"
    /usr/bin/r10k deploy environment $env -pv

    echo "Reporting the result of the update"
    /opt/shiftleader/manage.py puppet_env2report $env
  fi
done
