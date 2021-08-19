FROM registry.redhat.io/openshift-pipelines/pipelines-cli-tkn-rhel8:0.19.0-2 as tkn

FROM quay.io/openshift/origin-must-gather:4.8.0

# Save original gather script
RUN mv /usr/bin/gather /usr/bin/gather_original

# Copy all collection scripts to /usr/bin
COPY bin/* /usr/bin/

RUN chmod +x /usr/bin/gather_pipelines

COPY --from=tkn /usr/bin/tkn /usr/local/bin/tkn

CMD ["bash", "/usr/bin/gather"]
