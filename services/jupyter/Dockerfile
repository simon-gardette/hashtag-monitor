FROM jupyter/scipy-notebook

USER jovyan


COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

RUN jupyter labextension install @jupyterlab/celltags