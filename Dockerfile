# Override with a registry mirror when docker.io is unreachable,
# e.g. --build-arg BASE_IMAGE=docker.m.daocloud.io/library/python:3.12-alpine
ARG BASE_IMAGE=python:3.12-alpine
FROM ${BASE_IMAGE}

WORKDIR /app

COPY setup.py README.rst LICENSE ./
COPY autoremovetorrents ./autoremovetorrents

# Install the package and bake the PLY parser tables (lextab/parsetab) into
# the image so the container doesn't need write access to site-packages.
# The trailing cleanup removes the setuptools build tree and the smoke-run
# log so the shipped image contains only the installed copy.
RUN pip install --no-cache-dir . \
    && python -c "import autoremovetorrents.conditionparser, autoremovetorrents.conditionlexer" \
    && autoremove-torrents --view -c /dev/null \
    && rm -rf /app/build /app/autoremove.*.log

ENTRYPOINT ["autoremove-torrents"]
CMD ["--conf", "/etc/autoremove/config.yml"]
