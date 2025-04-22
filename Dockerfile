#FIXME PIN TO VERSION
FROM debian:12.10

RUN apt-get update && apt-get install -y python3-pip python3-flask python3-pydicom python3-wand dcmtk
#RUN apt install -y  --no-cache py3-pip py3-flask py3-pydicom py3-wand dcmtk py3-pillow py3-werkzeug && mkdir /src
COPY /src/*.py /src/
RUN chmod +x /src/*

#FIXME add entry point
ENTRYPOINT ["/src/dicomd.py"]

