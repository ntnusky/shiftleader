#!/bin/bash

# If we are the only instance of this script running; start doing something:
lockdir="/tmp/r10k.run.lock"
if mkdir $lockdir; then
  # Run r10k to discover new environments
  /usr/bin/r10k deploy environment production

  # Register new environments in shiftleader
  /opt/shiftleader/manage.py puppet_env2create
  
  # For each environment shiftleader knows about:
  for env in $(/opt/shiftleader/manage.py puppet_env2list); do
    # If it is tagged for an update:
    if [[ $(/opt/shiftleader/manage.py puppet_env2update $env) -eq '1' ]]; then
      echo "Running r10k to update $env"
      /usr/bin/r10k deploy environment $env -pv

      echo "Regenerating puppet types"
      /opt/puppetlabs/bin/puppet generate types --environment $env &> /dev/null
  
      echo "Reporting the result of the update"
      /opt/shiftleader/manage.py puppet_env2report $env
    fi
  done

  # Remove the lock 
  rmdir $lockdir
  exit 0

# If other instances of the script runs, simply exit.
else
  echo "Lock failed - exit" >&2
  exit 1
fi
