
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

RUN curl -sSL https://gist.githubusercontent.com/b01/0a16b6645ab7921b0910603dfb85e4fb/raw/5186ea07a06eac28937fd914a9c8f9ce077a978e/download-vs-code-server.sh | sed "s/server-linux-x64/server-linux-$(dpkg --print-architecture)/" | sed "s/amd64/x64/" | bash

ENV VSCODE_SERVER=/root/.vscode-server/bin/*/server.sh

RUN $VSCODE_SERVER --install-extension ms-python.vscode-pylance \
    $VSCODE_SERVER --install-extension ms-python.python \
    $VSCODE_SERVER --install-extension himanoa.python-autopep8 \
    $VSCODE_SERVER --install-extension esbenp.prettier-vscode \
    $VSCODE_SERVER --install-extension littlefoxteam.vscode-python-test-adapter

COPY ./start.sh /start.sh
ADD ./detector /app
ENV PYTHONPATH=/app

EXPOSE 80

CMD ["/start.sh"]
