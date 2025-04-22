# ph-challenge
There are lots of error conditions that are not handled and things to be thought of or fixed.

FIXME are throughout the code flagging issues. 

FYI, Initially,  alpine was used as base container, but ImageMagick used for converting to dicom to png, did not have that feature compiled in the alpine package

How to build the container

```
podman build -t dicomd:v2 .
```

how to run the image
```
#podman run -ti --rm -p 5000:8080 -v ./data:/data dicomd:v2
podman run -ti --rm -p 5000:8080 dicomd:v2
```

testing commands I'm working with

```
http --form POST http://localhost:5000/upload  file@IM000001

#This is img header, does it break
http GET http://localhost:5000/tag/0029,1010
```



