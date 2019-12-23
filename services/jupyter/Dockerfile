FROM jupyter/scipy-notebook

USER jovyan

RUN pip install --proxy=${http_proxy}\
    psycopg2-binary\
    SQLAlchemy

RUN jupyter labextension install @jupyterlab/celltags
