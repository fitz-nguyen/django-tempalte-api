ARG PYTHON_VERSION=3.12-slim-bullseye

###########
# BUILDER #
###########

# pull official base image
FROM python:${PYTHON_VERSION} as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install dependencies
RUN pip install --upgrade pip
RUN pip install config

COPY ./api/requirements requirements
RUN pip install -r requirements/local.txt --no-cache-dir

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements/local.txt

#########
# FINAL #
#########


FROM python:${PYTHON_VERSION}

RUN apt-get update \
    && apt-get -y install gdal-bin libgdal-dev  \
    && apt-get -y install libgeos++-dev libgeos-3.9.0 libgeos-c1v5 libgeos-dev libgeos-doc

ARG USER=app
ENV APP_HOME=/home/$USER/api

# create directory for the app user
RUN mkdir -p $APP_HOME

# create the app user
RUN adduser $USER


# working dir
WORKDIR $APP_HOME

# install dependencies
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements requirements
RUN pip install --no-cache /wheels/*

# copy project
COPY api .

# copy entrypoint.sh
COPY containers/django/entrypoint.sh $APP_HOME
COPY containers/django/gunicorn.sh $APP_HOME
RUN chmod +x $APP_HOME/entrypoint.sh
RUN chmod +x $APP_HOME/gunicorn.sh

# chown all the files to the app user
RUN chown -R $USER:$USER $APP_HOME

# change to the app user
USER $USER

# run entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
