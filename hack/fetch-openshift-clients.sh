#!/usr/bin/env bash
set -euo pipefail
set -x

cd /tmp

ARCH=$(uname -m)
echo "Fetch openshift-clients for ${ARCH}..."

case "${ARCH}" in
    amd64|x86_64)
        curl -fsSLO https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable-4.8/openshift-client-linux.tar.gz
        ;;
    ppc64le)
        curl -fsSLO https://mirror.openshift.com/pub/openshift-v4/ppc64le/clients/ocp/stable-4.8/openshift-client-linux.tar.gz
    ;;
    s390x)
        curl -fsSLO https://mirror.openshift.com/pub/openshift-v4/s390x/clients/ocp/stable-4.8/openshift-client-linux.tar.gz
    ;;
    *)
        echo "unsupported architecture"
        exit 1
        ;;
esac

tar xvzf openshift-client-linux.tar.gz
mv oc /usr/bin
rm README.md
rm kubectl
