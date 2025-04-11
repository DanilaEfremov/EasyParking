FROM ghcr.io/astral-sh/uv:python3.12-alpine AS web_builder
LABEL authors="ove"

# Параметры сборки по умолчанию
ARG BUILD_MOD=dev
ARG APP_ROOT=/app
ARG APP_CONFIG=/app_conf
ARG DJANGO_USER=myuser
ARG DJANGO_GROUP=mygroup
ARG DJANGO_USER_ID=2000
ARG DJANGO_GROUP_ID=2001

RUN echo "User is ${DJANGO_USER}:${DJANGO_USER} -> ${DJANGO_USER_ID}:${DJANGO_GROUP_ID}"

ARG APP_START=/run_app_${BUILD_MOD}.sh
ARG UV=${APP_ROOT}${APP_CONFIG}/uv_sync_${BUILD_MOD}.sh



# Очень важная переменная окружения.
# Если установлена, то uv считает, что по этому пути находится виртуальное окружение
# и устанавливает все пакеты исходя из этого.
# Системное виртуальное, т.е. глобольное окружение python в Debian находитсы в /usr/local.
# Подробнее: https://docs.astral.sh/uv/concepts/projects/config/#project-environment-path
ENV UV_PROJECT_ENVIRONMENT=/usr/local

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# First, build the application in the `/app` directory.
# See `Dockerfile` for details.
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the system interpreter
# across both images. If using a managed Python version, it needs to be
# copied from the build image into the final image; see `standalone.Dockerfile`
# for an example.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR ${APP_ROOT}
COPY . ${APP_ROOT}

RUN chmod +x ${UV} && chmod +x ${APP_ROOT}${APP_CONFIG}${APP_START}


RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    ${UV} --no-install-project
#    uv sync --frozen --no-install-project
#    uv sync --frozen --no-install-project --no-dev

#ADD ../uv_test ${APP_ROOT}
RUN --mount=type=cache,target=/root/.cache/uv \
    ${UV}
#    uv sync --frozen
#    uv sync --frozen --no-dev

RUN cat <<EOF > ${APP_ROOT}${APP_CONFIG}/run.sh
#!/bin/sh
sh -c ${APP_ROOT}${APP_CONFIG}${APP_START}
EOF
RUN chmod +x ${APP_ROOT}${APP_CONFIG}/run.sh

#RUN mkdir -p /app/logs/web

RUN addgroup -g ${DJANGO_GROUP_ID} ${DJANGO_GROUP}
#  \  &&  \
RUN adduser ${DJANGO_USER} --uid ${DJANGO_USER_ID} -G ${DJANGO_GROUP} --home /home/${DJANGO_USER}/ --disabled-password

#RUN mkdir -p /app/logs && \
#    mkdir -p /app/static && \
#RUN chown -R ${USER}:${GROUP} /app


#RUN chmod -R 755 /app/static && \
#    chmod -R 755 /app/logs

#RUN chown -R myuser:myuser /app/logs

#USER ${USER}


EXPOSE 8000

CMD ["/app/app_conf/run.sh"]
#CMD ["/app/app_conf/run_app_dev.sh"]