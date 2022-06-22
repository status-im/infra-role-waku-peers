# Description

This role runs a Python script to:

* Query Consul catalog for specified services
* Call JSON RPC API to connect the peers
* Verifies the node has connected peers

# Configuration

Bare minimum would include:
```yaml
waku_peers_connect_consul_service_names: ['nim-waku-v2', 'go-waku']
waku_peers_connect_consul_service_env: 'example'
waku_peers_connect_consul_service_stage: 'prod'
```

# Usage

The script can be used manually:
```sh
 > /usr/local/bin/connect_waku_peers.py -n nim-waku -e status -s test -l debug
2022-03-10 15:43:29,686 [INFO] Connecting to Consul: localhost:8500
2022-03-10 15:43:29,692 [INFO] Found 5 data centers.
2022-03-10 15:43:29,697 [DEBUG] Service: node-01.do-ams3.status.test (env:status,stage:test,nim,waku,libp2p)
2022-03-10 15:43:29,939 [DEBUG] Service: node-01.gc-us-central1-a.status.test (env:status,stage:test,nim,waku,libp2p)
2022-03-10 15:43:30,154 [DEBUG] Service: node-01.ac-cn-hongkong-c.status.test (env:status,stage:test,nim,waku,libp2p)
2022-03-10 15:43:30,154 [INFO] Found 3 services.
2022-03-10 15:43:30,155 [INFO] Calling JSON RPC: localhost:8545
2022-03-10 15:43:36,114 [INFO] SUCCESS
```

# Management

The script is called by a Systemd service:
```
 > sudo systemctl -o cat status waku-peers
● waku-peers.service - Script for connecting waku fleet peers.
     Loaded: loaded (/etc/systemd/system/waku-peers.service; static; vendor preset: enabled)
     Active: inactive (dead) since Wed 2022-06-22 11:01:49 UTC; 5min ago
TriggeredBy: ● waku-peers.timer
       Docs: https://github.com/status-im/infra-role-waku-peers
    Process: 2356000 ExecStart=/usr/local/bin/connect_waku_peers.py --log-level=info --rpc-host=localhost --rpc-port=8545 --service-env=status --service-stage=test --service-names=nim-waku,nim-waku-bridge (code=exited, status=0/SUCCESS)
   Main PID: 2356000 (code=exited, status=0/SUCCESS)

Starting Script for connecting waku fleet peers....
2022-06-22 11:01:42,565 [INFO] Found 5 data centers.
2022-06-22 11:01:43,317 [INFO] Found 4 services.
2022-06-22 11:01:49,305 [INFO] SUCCESS
```
Which runs hourly via a [Systemd timer](https://github.com/status-im/infra-role-systemd-timer).
```
 > sudo systemctl list-timers -a waku-peers
NEXT                        LEFT       LAST                        PASSED       UNIT             ACTIVATES         
Wed 2022-06-22 12:00:00 UTC 55min left Wed 2022-06-22 11:00:06 UTC 4min 52s ago waku-peers.timer waku-peers.service
```

# Links

* https://github.com/status-im/infra-status/issues/4
* https://github.com/status-im/infra-role-nim-waku
