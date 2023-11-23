# syntax=docker/dockerfile:1.4
FROM python:3.10-alpine AS builder

# upgrade pip
RUN pip install --upgrade pip

# get curl for healthchecks
RUN apk add curl

# permissions and nonroot user for tightened security
RUN adduser -D nonroot
RUN mkdir /home/app/ && chown -R nonroot:nonroot /home/app
RUN mkdir /home/app/app/ && chown -R nonroot:nonroot /home/app/app
RUN mkdir -p /var/log/flask-app && touch /var/log/flask-app/flask-app.err.log && touch /var/log/flask-app/flask-app.out.log
RUN chown -R nonroot:nonroot /var/log/flask-app
WORKDIR /home/app
USER nonroot

# copy all the files to the container
COPY --chown=nonroot:nonroot . .

# install poetry
ENV POETRY_HOME=/home/app/poetry
RUN curl -sSL https://install.python-poetry.org | python3 - 
RUN echo ls $POETRY_HOME

# venv
ENV VIRTUAL_ENV=/home/app/venv
ENV FLASK_SERVER_PORT=8080

# python virtual env setup
RUN python -m venv $VIRTUAL_ENV

# intall rust
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

ENV HOME=/home/app
ENV PATH="$VIRTUAL_ENV/bin:$HOME/.cargo/bin:$POETRY_HOME/bin:$PATH"
ENV DEBUG=${DEBUG}

RUN export FLASK_APP=app.py
RUN poetry install

# define the port number the container should expose
EXPOSE 8080
EXPOSE 5678

CMD ["gunicorn", "-b", "0.0.0.0:8080", "--workers", "2", "app.main:app"]