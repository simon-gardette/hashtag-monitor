FROM jupyter/scipy-notebook

USER root

RUN apt-get update && apt-get install -y apt-transport-https
RUN apt-get update && apt-get install -y apt-utils
RUN apt-get update -y && apt-get install -y wget curl unzip libgconf-2-4
RUN apt-get update -y && apt-get install -y xvfb

# Chrome and chromedriver for selenium (headless browsing)
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

USER jovyan

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# required for papermill (notebook automation)
RUN jupyter labextension install @jupyterlab/celltags

# Set display port and dbus env to avoid hanging
ENV DISPLAY=:99
ENV DBUS_SESSION_BUS_ADDRESS=/dev/null

# Bash script to invoke xvfb, any preliminary commands, then invoke project
COPY run.sh .
CMD /bin/bash run.sh
