#!/usr/bin/env python3
import sys
import json
import consul
import socket
import logging
from os import environ
from optparse import OptionParser
from urllib3 import util, PoolManager

HELP_DESCRIPTION = """
This script queries Consul for specified services and then
connects them to a Waku node using JSON RPC API.
""".strip()
HELP_EXAMPLE = """
Example: ./connect.py -s '{"name":"nim-waku","env":"status","stage":"test"}'
"""

# Setup logging.
log_format = '[%(levelname)s] %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
LOG = logging.getLogger(__name__)

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-s', '--services', type='string', action="append",
                      help='JSON object defining Consul service to query for.')
    parser.add_option('-t', '--consul-token', default=environ.get('CONSUL_HTTP_TOKEN'),
                      help='Consul ACL token for catalog API access.')
    parser.add_option('-c', '--consul-host', default='localhost',
                      help='Consul listening address.')
    parser.add_option('-d', '--consul-port', default=8500,
                      help='Consul listening port.')
    parser.add_option('-o', '--consul-timeout', type=int, default=10,
                      help='Consul query timeout in seconds.')
    parser.add_option('-H', '--rpc-host', default='localhost',
                      help='JSON RPC listening address.')
    parser.add_option('-P', '--rpc-port', type=int, default=8545,
                      help='JSON RPC listening port.')
    parser.add_option('-M', '--rpc-method', default='post_waku_v2_admin_v1_peers',
                      help='JSON RPC method to call.')
    parser.add_option('-T', '--rpc-timeout', type=int, default=10,
                      help='JSON RPC method timeout in seconds.')
    parser.add_option('-R', '--rpc-retries', type=int, default=3,
                      help='JSON RPC method timeout in seconds.')
    parser.add_option('-l', '--log-level', default='info',
                      help='Change default logging level.')

    for option in parser.option_list:
        if option.default != ("NO", "DEFAULT"):
            option.help += (" " if option.help else "") + "(default: %default)"

    return parser.parse_args()

class RPC:
    def __init__(self, host='localhost', port=8545, timeout=30, retries=3):
        self.host = host
        self.port = port
        self.timeout = util.Timeout(connect=timeout, read=timeout)
        self.retries = util.Retry(connect=retries, read=retries, method_whitelist=["POST"])
        self.http = PoolManager(retries=self.retries, timeout=self.timeout)

    def call(self, method, params=[]):
        url = 'http://%s:%d' % (self.host, self.port)
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        LOG.debug('RPC Call URL: %s', url)
        LOG.debug('RPC Call Payload: %s', payload)
        rval = self.http.request(
            'POST',
            url,
            headers={'Content-Type': 'application/json'},
            body=json.dumps(payload)
        )
        return json.loads(rval.data)

def main():
    (opts, args) = parse_opts()

    LOG.setLevel(opts.log_level.upper())

    LOG.debug('Connecting to Consul: %s:%d', opts.consul_host, opts.consul_port)
    c = consul.Consul(
        host=opts.consul_host,
        port=opts.consul_port,
        token=opts.consul_token,
        timeout=opts.consul_timeout
    )

    dcs = c.catalog.datacenters()
    LOG.info('Found %d data centers.', len(dcs))

    services = []
    invalid = []
    for service in opts.services:
        service = json.loads(service)
        if 'name' not in service:
            raise Exception('No service name given!')
        name = service['name']
        node_meta = {}
        if 'env' in service:
            node_meta['env'] = service['env']
        if 'stage' in service:
            node_meta['stage'] = service['stage']

        for dc in dcs:
            LOG.debug('Querying: %s (dc=%s, node_meta=%s)', name, dc, node_meta)
            rval = c.catalog.service(name, dc=dc, node_meta=node_meta)[1]
            services += rval
            for s in rval:
                LOG.debug('Found: %s (%s)', s['Node'], ','.join(s['ServiceTags']))
                if s['ServiceMeta'].get('node_enode', 'unknown') == 'unknown':
                    LOG.error('Unknown peer enode address: %s', s)
                    invalid.append(s)

    # Exclude services from current host.
    services = list(filter(lambda s: s['Node'] != socket.gethostname(), services))

    LOG.info('Found %d services.', len(services))
    if len(services) == 0:
        raise Exception('No services found')

    enodes = [s['ServiceMeta']['node_enode'] for s in services]

    LOG.debug('Calling JSON RPC: %s:%d', opts.rpc_host, opts.rpc_port)
    rpc = RPC(
        host=opts.rpc_host,
        port=opts.rpc_port,
        timeout=opts.rpc_timeout,
        retries=opts.rpc_retries
    )

    LOG.debug('Adding services...')
    rval = rpc.call(opts.rpc_method, params=[enodes])
    if rval is None:
        raise Exception('RPC Call failure!')
    elif 'error' in rval and rval['error'] is not None:
        raise Exception('RPC Error: %s' % rval['error'])

    if rval['result'] == True:
        LOG.info('SUCCESS')
    else:
        raise Exception('Unknown response: %s' % rval)

    if len(invalid) > 0:
        LOG.error('Some enode addresses were invalid!')
        sys.exit(1)

if __name__ == '__main__':
    main()
