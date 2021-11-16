# Pipelines must-gather

`must-gather` is a tool built on top of [OpenShift must-gather](https://github.com/openshift/must-gather) that expands its capabilities to gather openshift-pipelines debug information.

It currently supports the following architectures:
- `linux/amd64`
- `linux/ppc64le`
- `linux/s390x`

## Usage

```sh
oc adm must-gather --image=quay.io/openshift-pipeline/must-gather
```

In order to get data about other parts of the cluster (not specific to Pipelines) you should run `oc adm must-gather` (without passing a custom image). Run `oc adm must-gather --help` to see more options.
