FROM jupyter/scipy-notebook

USER root

RUN apt-get update && apt-get install -y apt-transport-https
RUN apt-get update && apt-get install -y apt-utils
RUN apt-get update -y && apt-get install -y wget curl unzip libgconf-2-4
RUN apt-get update -y && apt-get install -y xvfb \
                                            libicu-dev


USER jovyan

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# required for papermill (notebook automation)
RUN jupyter labextension install @jupyterlab/celltags


# Bash script to invoke xvfb, any preliminary commands, then invoke project
COPY run.sh .
CMD /bin/bash run.sh
