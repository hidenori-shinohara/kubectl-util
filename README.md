# kubectlutil

A script to make it easy to monitor supercluster jobs.

* examples
    * `python3 kubectlutil.py --namespace hidenori configmap -n www-stellar-org-2`
        * This prints the configmap for the node `www-stellar-org-2`.
    * `watch -n 10 python3 ~/kubectlutil/kubectlutil.py --namespace hidenori --kubeconfig ~/.kube/config monitor`