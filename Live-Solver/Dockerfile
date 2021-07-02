FROM registry.access.redhat.com/ubi8/python-36

LABEL maintainer="ms@quantitec.de"

WORKDIR /opt/app-root/src

# Install requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source to contain
COPY . .

USER root

ENTRYPOINT [ "python", "/opt/app-root/src/main.py" ]
