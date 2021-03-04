import argparse
import toml
import subprocess
from kubernetes import client, config

PREFERRED_PEERS = "PREFERRED_PEERS"
QUORUM_SET = "QUORUM_SET"

def getPodList(args):
    config.load_kube_config()

    v1 = client.CoreV1Api()
    a = v1.list_namespaced_config_map(args.namespace)
    return v1.list_namespaced_pod(args.namespace)

def getConfigMapList(args):
    config.load_kube_config()

    v1 = client.CoreV1Api()
    return v1.list_namespaced_config_map(args.namespace)


def getip2podname():
    ip2podname = dict()
    for item in ret.items:
        ip2podname[item.status.pod_ip] = item.metadata.name
    return ip2podname

def podname2name(podname, args):
    return podname[21:-(49 + len(args.namespace))]

def cleanPreferredPeers(preferredPeers, args):
    for i in range(len(preferredPeers)):
        preferredPeers[i] = podname2name(preferredPeers[i], args)
    preferredPeers.sort()

def cleanQuorumSet(quroumSet):
    # TODO
    return

def configmap(args):
    configMapList = getConfigMapList(args)
    for configMap in configMapList.items:
        if args.node in configMap.metadata.name:
            parsed_toml = toml.loads(configMap.data['stellar-core.cfg'])
            if not args.raw:
                cleanPreferredPeers(parsed_toml[PREFERRED_PEERS], args)
                cleanQuorumSet(parsed_toml[QUORUM_SET])
            print(toml.dumps(parsed_toml))

def httpCommand(args):
    podList = getPodList(args)
    podName = "not found"
    for pod in podList.items:
        podName = pod.metadata.name
        if args.node in podName:
            break
    # TODO: Find out a way to get ingress from the API.
    template = 'curl {}.stellar-supercluster.kube001.services.stellar-ops.com/{}/core/{}'
    cmd = template.format(podName[:16], podName, args.command)
    process = subprocess.Popen(cmd.split())
    process.communicate()


def addNodeArgument(parser):
    parser.add_argument("-n",
          "--node",
          default="www-stellar-org-0",
          help="Optional flag to specify the node. If none, www-stellar-org-0 will be used.")

def addConfigmapParser(subparsers):
    parserConfigMap = subparsers.add_parser("configmap",
                                           help="Get the configmap")
    addNodeArgument(parserConfigMap)
    parserConfigMap.add_argument("-r",
          "--raw",
          action='store_true',
          help="Optional flag to output the raw configmap. If not set, it simplifies the output")

    parserConfigMap.set_defaults(func=configmap)

def addHttpCommandParser(subparsers):
    parserHttpCommand = subparsers.add_parser("http",
                                           help="Run http command")
    addNodeArgument(parserHttpCommand)

    parserHttpCommand.add_argument("-c",
          "--command",
          default="info",
          help="HTTP command to run. If not set, it runs info")

    parserHttpCommand.set_defaults(func=httpCommand)


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-ns",
                                 "--namespace",
                                 default="hidenori",
                                 help="namespace")

    subparsers = argument_parser.add_subparsers()
    addConfigmapParser(subparsers)
    addHttpCommandParser(subparsers)

    args = argument_parser.parse_args()                              
    args.func(args)


if __name__ == '__main__':
    main()