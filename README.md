# Description

This role runs a Python script to:

* Query Consul catalog for specified services
* Call JSON RPC API to connect the peers
* Verifies the node has connected peers

# Configuration

Bare minimum would include:
```yaml
waku_peers_consul_services:
  - { name: 'nim-waku-v2', env: 'wakuv2',  stage: 'test' }
  - { name: 'go-waku',     env: 'go-waku', stage: 'test' }
```

# Usage

The script can be used manually:
```sh
 > /usr/local/bin/connect_waku_peers.py -l debug -s '{"name": "go-waku", "env": "go-waku", "stage": "test"}'
[DEBUG] Connecting to Consul: localhost:8500
[INFO] Found 5 data centers.
[DEBUG] Querying: go-waku (dc=do-ams3, node_meta={'env': 'go-waku', 'stage': 'test'})
[DEBUG] Found: node-01.do-ams3.go-waku.test (env:go-waku,stage:test,go,waku)
[DEBUG] Querying: go-waku (dc=gc-us-central1-a, node_meta={'env': 'go-waku', 'stage': 'test'})
[DEBUG] Found: node-01.gc-us-central1-a.go-waku.test (env:go-waku,stage:test,go,waku)
[DEBUG] Querying: go-waku (dc=ac-cn-hongkong-c, node_meta={'env': 'go-waku', 'stage': 'test'})
[DEBUG] Found: node-01.ac-cn-hongkong-c.go-waku.test (env:go-waku,stage:test,go,waku)
[INFO] Found 2 services.
[DEBUG] Calling JSON RPC: localhost:8545
[DEBUG] Adding services...
[DEBUG] RPC Call URL: http://localhost:8545
[DEBUG] RPC Call Payload: {'method': 'post_waku_v2_admin_v1_peers', 'params': [['/ip4/35.223.183.91/tcp/30303/p2p/16Uiu2HAmPz63Xc6AuVkDeujz7YeZta18rcdau3Y1BzaxKAfDrBqz', '/ip4/8.218.2.110/tcp/30303/p2p/16Uiu2HAmBDbMWFiG9ki8sDw6fYtraSxo4oHU9HbuN43S2HVyq1FD']], 'jsonrpc': '2.0', 'id': 0}
[INFO] SUCCESS
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
