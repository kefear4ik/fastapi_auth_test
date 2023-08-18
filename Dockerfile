FROM python:3.11

WORKDIR /var/app
ADD Pipfile /var/app/Pipfile
ADD Pipfile.lock /var/app/Pipfile.lock

ENV FETCH_PACKAGES="wget gnupg2" \
    BUILD_PACKAGES="build-essential gcc linux-headers-amd64 libffi-dev libgeos-c1v5 libpq-dev libssl-dev" \
    PACKAGES="postgresql-client"

RUN apt update && \
    apt install -y ${FETCH_PACKAGES}

RUN apt update && apt upgrade -y
RUN apt install -y --no-install-recommends ${BUILD_PACKAGES} ${PACKAGES}
RUN rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -U pipenv

RUN pipenv install --deploy --system
RUN apt purge -y ${BUILD_PACKAGES} && \
    apt purge -y ${FETCH_PACKAGES} && \
    apt autoremove -y

ADD . /var/app
ENV PYTHONPATH "${PYTHONPATH}:/var/app/app"

CMD ["gunicorn", "app.main:app", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "-b", ":8081" ]