# Service Types
There are 2 types of services in the system: Cup Process and systemd service. In general, 

## Cup Process
Cup Processes are the parts of CT App and they run on host. In general, CT App is composed of about 50~60 Cup Processes (different version/config has different number) and some Cup Process crash/failed to start could cause the entire CT App shutdown. Some systemd services (run on host or remote nodes) have a Cup Process watchdog to represent it in the CT App, such as raw_data_service Cup Process is the watchdog of raw-data-service (which is a systemd service) runs on sdac.

Some important Cup Processes need to focus:
- ig_watchdog: It manages and watches all the recon nodes. If the ig_watchdof crash or failed to start, the entire Recon subsystem will shutdown.
- sda_watchdog: It manages the watches the sdac node. It may crash/failed to start if there is something wrong with SDA subsystem, such as RAID failed or network disconnected.
- scan_record_service: It watches the scan-record-service runs on host. If it crash, the scan database is not available.

## Systemd Service
Some services of hardware level or non-APP service are managed by systemd.

Some important systemd service need to focus:
- sigpower/xig1power: These services run on host and are used to power on/off the remote nodes automatically when the host node power on/off. So these services need to check systemctl is-enabled.
- ge_cpuset: This service runs on sdac, which is used to manage the cgroups and cpu affinity.
- raw-data-service: This service runs on sdac, which is used to send raw data to igc nodes.
- docker: This service runs on all nodes, which is used to manage docker images/containers.