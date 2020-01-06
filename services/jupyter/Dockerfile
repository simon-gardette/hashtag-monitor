FROM jupyter/scipy-notebook

USER jovyan


COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

RUN jupyter labextension install @jupyterlab/celltags

RUN apt-get update -y && apt-get install -y wget curl unzip libgconf-2-4
RUN apt-get update -y && apt-get install -y chromium xvfb python3 python3-pip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Set display port and dbus env to avoid hanging
ENV DISPLAY=:99
ENV DBUS_SESSION_BUS_ADDRESS=/dev/null
# Bash script to invoke xvfb, any preliminary commands, then invoke project
COPY run.sh .
CMD /bin/bash run.sh
