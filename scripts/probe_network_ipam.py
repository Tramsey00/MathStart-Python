"""Classify automatic-IPAM static attachment using only new owned resources.

No service is started, no credentials are passed and arbitrary Docker stderr
is never exported. This diagnostic is not a substitute for image recovery.
"""
import argparse
import hashlib
import ipaddress
import json
import shutil
import subprocess
import uuid
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('New diagnostic output required')
    docker = shutil.which('docker')
    if not docker:
        parser.error('Docker CLI required')
    purpose = 'disposable-ipam-probe-' + uuid.uuid4().hex
    networks = []
    container = None
    receipt = {'status': 'IN_PROGRESS', 'scope': 'AUTOMATIC_IPAM_DIAGNOSTIC_ONLY'}

    def command(*argv):
        result = subprocess.run([docker, *argv], capture_output=True, timeout=30)
        if result.returncode:
            raise RuntimeError('Owned diagnostic Docker operation failed')
        return result.stdout.decode().strip()

    def inspect(kind, identity):
        state = json.loads(command(kind, 'inspect', identity))[0]
        labels = state['Config']['Labels'] if kind == 'container' else state['Labels']
        assert state['Id'] == identity and labels['mathstart.purpose'] == purpose
        return state

    try:
        receipt['docker_version'] = json.loads(command('version', '--format', '{{json .Server}}'))['Version']
        internal = command('network', 'create', '--internal', '--label', 'mathstart.purpose=' + purpose, purpose + '-internal')
        networks.append(internal)
        front = command('network', 'create', '--label', 'mathstart.purpose=' + purpose, purpose + '-front')
        networks.append(front)
        subnet = ipaddress.ip_network(inspect('network', internal)['IPAM']['Config'][0]['Subnet'])
        assert subnet.version == 4 and subnet.num_addresses > 12
        container = command('create', '--name', purpose, '--label', 'mathstart.purpose=' + purpose,
                            '--network', front, '--entrypoint', 'python', args.image, '-c', 'pass')
        inspect('container', container)
        result = subprocess.run([docker, 'network', 'connect', '--ip', str(subnet.network_address + 10), internal, container],
                                capture_output=True, timeout=30)
        diagnostic = result.stdout + result.stderr
        known = b'user specified IP address is supported only when connecting to networks with user configured subnets'
        receipt.update(status='OBSERVED', operation='network connect --ip', exit_code=result.returncode,
                       classification='SUCCESS' if not result.returncode else
                       'STATIC_IP_REQUIRES_EXPLICIT_SUBNET' if known.lower() in diagnostic.lower() else 'UNCLASSIFIED',
                       diagnostic_sha256=hashlib.sha256(diagnostic).hexdigest())
    finally:
        errors = []
        if container:
            try:
                state = inspect('container', container)
                assert not state['State']['Running']
                command('container', 'rm', container)
            except Exception as error:
                errors.append(type(error).__name__)
        for identity in reversed(networks):
            try:
                assert not inspect('network', identity).get('Containers')
                command('network', 'rm', identity)
            except Exception as error:
                errors.append(type(error).__name__)
        receipt['cleanup'] = 'FAIL' if errors else 'PASS'
        receipt['cleanup_errors'] = errors
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(receipt))
        if errors:
            raise RuntimeError('Owned diagnostic cleanup failed')


if __name__ == '__main__':
    main()
