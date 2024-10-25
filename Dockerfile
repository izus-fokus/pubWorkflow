FROM python:3.12.7-bookworm AS builder
RUN apt-get install bash git

LABEL maintainer="florian.fritze@ub.uni-stuttgart.de"

ARG REPO_ACCESS_TOKEN

SHELL ["/bin/bash", "-c"]

WORKDIR /app
COPY . /app

RUN python3 -m venv /app/venv
ENV PATH=/app/venv/bin:$PATH
RUN source /app/venv/bin/activate
RUN sed -i "s/REPO_ACCESS_TOKEN/$REPO_ACCESS_TOKEN/g" /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip uninstall --yes easyDataverse
RUN pip install -e "git+https://ac143675:$REPO_ACCESS_TOKEN@github.tik.uni-stuttgart.de/ac143675/easyDataverse.git@main_0.4.1#egg=easyDataverse"
RUN sed -i "s/$REPO_ACCESS_TOKEN/REPO_ACCESS_TOKEN/g" /app/requirements.txt

FROM python:3.12.7-slim-bookworm
SHELL ["/bin/bash", "-c"]
WORKDIR /app
COPY --from=builder /app /app
ENV PATH=/app/venv/bin:/usr/local/bin:$PATH
RUN source /app/venv/bin/activate

ENV PORT=5000

ENV ADDRESS=127.0.0.1

EXPOSE $PORT

ENTRYPOINT gunicorn -b $ADDRESS:$PORT pubworkflowApi:app

RUN echo "We are done!"