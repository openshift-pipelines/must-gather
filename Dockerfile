FROM gcr.io/tekton-releases/dogfooding/tkn:latest as tkn
FROM fedora as fetcher

COPY hack/ .
RUN /bin/bash ./fetch-openshift-clients.sh

FROM quay.io/openshift/origin-must-gather:4.11 as gather

FROM registry.access.redhat.com/ubi8/ubi:8.6

COPY --from=gather /usr/bin/gather* /usr/bin
COPY --from=gather /usr/bin/openshift-must-gather /usr/bin
COPY --from=gather /usr/bin/version /usr/bin
COPY bin/* /usr/bin/

RUN chmod +x /usr/bin/gather_pipelines

COPY --from=fetcher /usr/bin/oc /usr/bin/oc
COPY --from=tkn /usr/local/bin/tkn /usr/local/bin/tkn

CMD ["bash", "/usr/bin/gather"]
