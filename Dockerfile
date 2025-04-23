FROM debian:12.10

RUN apt-get update && apt-get install -y python3-pip python3-flask python3-pydicom python3-wand dcmtk && mkdir /src /data
COPY /src/*.py /src/
RUN chmod +x /src/*

ENTRYPOINT ["/src/dicomd.py"]

