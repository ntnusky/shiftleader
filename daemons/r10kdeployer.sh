#!/bin/bash

host=$(hostname -f)

while /bin/true; do
  environment=$(/opt/shiftleader/manage.py puppet_deploy_start "$host")
  if $?; then
    logger "[SLDaemon-R10k-Deploy] Deploying environment $environment"
    /usr/bin/r10k deploy environment $environment -pv

    logger "[SLDaemon-R10k-Deploy] Regenerating puppet types"
    /opt/puppetlabs/bin/puppet generate types --environment "$environment"

    logger "[SLDaemon-R10k-Deploy] Reporting the result of the update"
    /opt/shiftleader/manage.py puppet_env2report "$environment"

    logger "[SLDaemon-R10k-Deploy] Mark the deployment as finished" 
    /opt/shiftleader/manage.py puppet_deploy_finish "$host" "$environment" 
  fi
  sleep 5
done
