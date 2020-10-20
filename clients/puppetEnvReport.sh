#!/bin/bash

# If we are the only instance of this script running; start doing something:
lockdir="/tmp/r10k.run.lock"
if mkdir $lockdir &> /dev/null; then
  # For each environment shiftleader knows about:
  for env in $(/opt/shiftleader/manage.py puppet_env2list); do
    # If it is tagged for an update:
    if [[ $(/opt/shiftleader/manage.py puppet_env2update "$env" 2> /dev/null) -eq '1' ]]; then
      logger "[Puppet-envupdate] Running r10k to update $env"
      /usr/bin/r10k deploy environment "$env" -pv

      logger "[Puppet-envupdate] Regenerating puppet types"
      /opt/puppetlabs/bin/puppet generate types --environment "$env" &> /dev/null
  
      logger "[Puppet-envupdate] Reporting the result of the update"
      /opt/shiftleader/manage.py puppet_env2report "$env"
    fi
  done

  # Remove the lock 
  rmdir $lockdir
  exit 0

# If other instances of the script runs, simply exit.
else
  logger "[Puppet-envupdate] $0 cannot run, as it is already running" >&2
  exit 1
fi
