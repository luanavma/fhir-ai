ARG IMAGE=intersystemsdc/irishealth-community:preview
FROM $IMAGE

USER root

RUN mkdir -p /opt/irisapp && chown ${ISC_PACKAGE_MGRUSER}:${ISC_PACKAGE_IRISGROUP} /opt/irisapp
WORKDIR /opt/irisapp

COPY --chown=$ISC_PACKAGE_MGRUSER:$ISC_PACKAGE_IRISGROUP iris.script /
COPY --chown=$ISC_PACKAGE_MGRUSER:$ISC_PACKAGE_IRISGROUP /data fhirdata

USER ${ISC_PACKAGE_MGRUSER}

RUN iris start IRIS \
    && iris session IRIS < /iris.script \
    && iris stop iris quietly
