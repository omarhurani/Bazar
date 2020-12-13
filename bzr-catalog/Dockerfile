# The environment to run
FROM alpine:latest

# Installing Python on image
RUN echo "**** install Python ****" && \
    apk add --no-cache python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    \
    echo "**** install pip ****" && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi

# Defining working directory
WORKDIR /app

# Copy files from this directory to the app directory in the image
# (Files in the .dockerignore are ignored)
COPY . /app

# Install pip dependencies from the requirements.txt file
RUN pip3 --no-cache-dir install -r requirements.txt

# Expose port 5000 from the image
# This needs to be mapped to a port on the host when the image is run in a container
EXPOSE 5000

# What command(s) to execute on container startup
# python3 app.py
ENTRYPOINT ["python3"]
CMD ["app.py"]
