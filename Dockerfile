FROM gcr.io/tekton-releases/dogfooding/tkn@sha256:f69a02ef099d8915e9e4ea1b74e43b7a9309fc97cf23cb457ebf191e73491677 as tkn

FROM quay.io/openshift/origin-must-gather:4.7.0

# Save original gather script
RUN mv /usr/bin/gather /usr/bin/gather_original

# Copy all collection scripts to /usr/bin
COPY bin/* /usr/bin/

RUN chmod +x /usr/bin/gather_pipelines

COPY --from=tkn /usr/local/bin/tkn /usr/local/bin/tkn

CMD ["bash", "/usr/bin/gather"]
