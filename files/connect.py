#!/usr/bin/env python3
import sys
import consul
import logging
import requests
from os import environ
from optparse import OptionParser

HELP_DESCRIPTION = """
This script queries Consul for Nim-Waku services and then
connects them to a node using JSON RPC API.
""".strip()
HELP_EXAMPLE = """
Example: ./connect.py -s nim-waku-v2
"""

# Setup logging.
log_format = '%(asctime)s [%(levelname)s] %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
LOG = logging.getLogger(__name__)

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-n', '--service-name',
                      help='Name of Consul services to query for.')
    parser.add_option('-e', '--service-env',
                      help='Env for Consul query filter.')
    parser.add_option('-s', '--service-stage',
                      help='Stage for Consul query filter.')
    parser.add_option('-t', '--consul-token', default=environ.get('CONSUL_HTTP_TOKEN'),
                      help='Consul ACL token for catalog API access.')
    parser.add_option('-c', '--consul-host', default='localhost',
                      help='Consul listening address.')
    parser.add_option('-d', '--consul-port', default=8500,
                      help='Consul listening port.')
    parser.add_option('-H', '--rpc-host', default='localhost',
                      help='JSON RPC listening address.')
    parser.add_option('-P', '--rpc-port', type=int, default=8545,
                      help='JSON RPC listening port.')
    parser.add_option('-M', '--rpc-method', default='post_waku_v2_admin_v1_peers',
                      help='JSON RPC method to call.')
    parser.add_option('-l', '--log-level', default='info',
                      help='Change default logging level.')

    for option in parser.option_list:
        if option.default != ("NO", "DEFAULT"):
            option.help += (" " if option.help else "") + "(default: %default)"

    return parser.parse_args()

class RPC:
    def __init__(self, host='localhost', port=8545):
        self.host = host
        self.port = port

    def call(self, method, params=[]):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        return requests.post(
            'http://%s:%d' % (self.host, self.port),
            json=payload
        ).json()

def main():
    (opts, args) = parse_opts()

    LOG.setLevel(opts.log_level.upper())

    LOG.debug('Connecting to Consul: %s:%d', opts.consul_host, opts.consul_port)
    c = consul.Consul(
        host=opts.consul_host,
        port=opts.consul_port,
        token=opts.consul_token
    )

    dcs = c.catalog.datacenters()
    LOG.info('Found %d data centers.', len(dcs))

    node_meta = {}
    if opts.service_env:
        node_meta['env'] = opts.service_env
    if opts.service_stage:
        node_meta['stage'] = opts.service_stage

    services = []
    invalid = []
    for dc in dcs:
        rval = c.catalog.service(
            opts.service_name,
            dc=dc,
            node_meta=node_meta
        )[1]
        services += rval
        for s in rval:
            LOG.debug('Service: %s (%s)', s['Node'], ','.join(s['ServiceTags']))
            if s['ServiceMeta'].get('node_enode', 'unknown') == 'unknown':
                LOG.error('Unknown peer enode address: %s', s)
                invalid.append(s)

    LOG.info('Found %d services.', len(services))
    if len(services) == 0:
        raise Exception('No services found')

    enodes = [s['ServiceMeta']['node_enode'] for s in services]

    LOG.debug('Calling JSON RPC: %s:%d', opts.rpc_host, opts.rpc_port)
    rpc = RPC(host=opts.rpc_host, port=opts.rpc_port)

    LOG.debug('Adding services...')
    rval = rpc.call(opts.rpc_method, params=[enodes])
    if 'error' in rval:
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
