#!/bin/bash

while /bin/true; do
  # If a environment-discovery is scheduled:
  if /opt/shiftleader/manage.py puppet_envrefresh; then
    logger "[Shiftleader-Client] Discovering environments"

    # Run r10k to discover new environments
    /usr/bin/r10k deploy environment production &> /dev/null

    # Register new environments in shiftleader
    /opt/shiftleader/manage.py puppet_env2create &> /dev/null

    logger "[Shiftleader-Client] Finished reporting new environments"
  fi
  sleep 5
done
