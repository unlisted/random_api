# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

# upgrade pip
RUN pip install --upgrade pip

# get curl for healthchecks
RUN apk add curl

# permissions and nonroot user for tightened security
RUN adduser -D nonroot
RUN mkdir /home/app/ && chown -R nonroot:nonroot /home/app
RUN mkdir -p /var/log/flask-app && touch /var/log/flask-app/flask-app.err.log && touch /var/log/flask-app/flask-app.out.log
RUN chown -R nonroot:nonroot /var/log/flask-app
WORKDIR /home/app
USER nonroot

# copy all the files to the container

COPY --chown=nonroot:nonroot . .

# venv
ENV VIRTUAL_ENV=/home/app/venv
ENV FLASK_SERVER_PORT=8080

# python setup
RUN python -m venv $VIRTUAL_ENV

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

# install poetry
# RUN curl -sSL https://install.python-poetry.org | POETRY_HOME="$HOME/poetry" python3 -

ENV export PATH="$VIRTUAL_ENV/bin:$HOME/.cargo/bin:$PATH"
RUN export FLASK_APP=app.py
RUN pip install -r requirements.txt
# RUN poetry install

# # define the port number the container should expose
EXPOSE 8080
EXPOSE 5678

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8080"]