# Description

This role runs a Python script to:

* Query Consul catalog for specified services
* Call JSON RPC API to connect the peers
* Verifies the node has connected peers

# Configuration

Bare minimum would include:
```yaml
nim_waku_connect_consul_service_names: ['nim-waku-v2', 'go-waku']
nim_waku_connect_consul_service_env: 'example'
nim_waku_connect_consul_service_stage: 'prod'
```

# Usage

The script can be used manually:
```sh
 > /usr/local/bin/nim_waku_connect.py -n nim-waku -e status -s test -l debug
2022-03-10 15:43:29,686 [INFO] Connecting to Consul: localhost:8500
2022-03-10 15:43:29,692 [INFO] Found 5 data centers.
2022-03-10 15:43:29,697 [DEBUG] Service: node-01.do-ams3.status.test (env:status,stage:test,nim,waku,libp2p)
2022-03-10 15:43:29,939 [DEBUG] Service: node-01.gc-us-central1-a.status.test (env:status,stage:test,nim,waku,libp2p)
2022-03-10 15:43:30,154 [DEBUG] Service: node-01.ac-cn-hongkong-c.status.test (env:status,stage:test,nim,waku,libp2p)
2022-03-10 15:43:30,154 [INFO] Found 3 services.
2022-03-10 15:43:30,155 [INFO] Calling JSON RPC: localhost:8545
2022-03-10 15:43:36,114 [INFO] SUCCESS
```

# Links

* https://github.com/status-im/infra-status/issues/4
* https://github.com/status-im/infra-role-nim-waku
