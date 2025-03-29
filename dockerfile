#FROM nvidia/cuda:10.2-base-ubuntu18.04
FROM nvcr.io/nvidia/base/ubuntu:20.04_x64_2022-09-23

SHELL ["/bin/bash", "-c"]

ENV TIME_ZONE UTC

ENV REF_DIR /gen_ref
ENV RESULTS_DIR /results_dir

ENV GMAIL_ID False
ENV GMAIL_PW False

ENV DJANGO_SUPERUSER_EMAIL xxx@email.com
ENV DJANGO_SUPERUSER_USERNAME admin
ENV DJANGO_SUPERUSER_PASSWORD Arrow

# Setup TZ
RUN ln -snf /usr/share/zoneinfo/${TIME_ZONE} /etc/localtime && echo ${TIME_ZONE} > /etc/timezone


RUN mkdir -p ${REF_DIR}
RUN chmod 755 ${REF_DIR}
RUN mkdir -p ${RESULTS_DIR}

# opencl cas-offinder install
RUN mkdir -p /tmp/install
WORKDIR /tmp/install
ADD docker/install_script install_script
RUN bash install_script/init_install.sh
RUN bash install_script/python_installer.sh

RUN bash install_script/install_cas_offinder.sh

RUN bash install_script/django_app.sh
RUN bash install_script/django_setting.sh

ARG DJANGO_PATH=/root/django
ARG DJANGO_APP_PATH=${DJANGO_PATH}/cas_web_app

ADD django ${DJANGO_PATH}
WORKDIR ${DJANGO_APP_PATH}
RUN python manage.py migrate --run-syncdb
RUN python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL




#RUN rm -rf /tmp/*

EXPOSE 80 443

CMD ["/bin/bash", "run_server.sh"]
#CMD ["/bin/bash"]
