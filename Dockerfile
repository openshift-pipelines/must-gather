ARG OPENSHIFT_VERSION=4.17

FROM ghcr.io/tektoncd/plumbing/tkn:latest AS tkn
FROM fedora AS fetcher
ARG OPENSHIFT_VERSION

COPY hack/ .
RUN /bin/bash ./fetch-openshift-clients.sh ${OPENSHIFT_VERSION}

FROM quay.io/openshift/origin-must-gather:$OPENSHIFT_VERSION AS gather

FROM registry.access.redhat.com/ubi9/ubi:latest

COPY --from=gather /usr/bin/gather* /usr/bin/
COPY --from=gather /usr/bin/openshift-must-gather /usr/bin
COPY --from=gather /usr/bin/version /usr/bin
COPY bin/* /usr/bin/

RUN dnf install --setopt=tsflags=nodocs -y jq rsync && dnf clean all && rm -rf /var/cache/dnf/* \
&& chmod +x /usr/bin/gather_pipelines

COPY --from=fetcher /usr/bin/oc /usr/bin/oc
COPY --from=tkn /usr/local/bin/tkn /usr/local/bin/tkn

CMD ["bash", "/usr/bin/gather"]
