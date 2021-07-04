
FROM zauberzeug/l4t-tkdnn-darknet:nano-r32.5.0

RUN apt-get update && apt-get -y install build-essential python3-dev curl libgl1-mesa-dev && apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV LANG C.UTF-8
RUN python3 -m pip install --upgrade pip
# fixing pyYAML upgrade error (see https://stackoverflow.com/a/53534728/364388)
RUN python3 -m pip install --ignore-installed PyYAML

# We use Poetry for dependency management
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

WORKDIR /app/

COPY ./pyproject.toml ./poetry.lock* ./

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

COPY ./ ./
ENV PYTHONPATH=/app
RUN ln -s /app/data /data

EXPOSE 80

ENV SERVER_BASE_URL=https://learning-loop.ai
ENV WEBSOCKET_BASE_URL=wss://learning-loop.ai

CMD ["/app/start.sh"]
