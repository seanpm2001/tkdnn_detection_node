FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# We use Poetry for dependency management
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# needed for opencv 
RUN apt-get update && apt-get -y install libgl1-mesa-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app/

COPY ./pyproject.toml ./poetry.lock* ./

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

COPY ./ ./
ENV PYTHONPATH=/app

EXPOSE 80
CMD bash
