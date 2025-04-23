# dicomd 
Errors or Issues I have thought of have been left as a comment in the code with a FIXME keyword, though fixing some of them are outside of my ability.

I used Image Magick for the conversion of the dicom file into the png.  Until this point I had been using alpine for my base image, however it looks like the alpine ImageMagick package is lacking dicom support, so I migrated to ubuntu.

# Build
How to build the container

```
podman build -t dicomd:v2 .
```

how to run the image
```
podman run -ti --rm -p 5000:8080 dicomd:v2
```

# Endpoints and general architecture
I don't like how I layed out the end points.  There seems to be a lack of upper level objects, but then again it is a fairly simple implementation.

# Testing/Usage examples

Upload a valid image file, get all tags from it, then get a single tag.
```
http --form POST http://localhost:5000/api/v1/upload  file@MRI/PA000001/ST000001/SE000001/IM000001
http GET http://localhost:5000/api/v1/tag
http GET http://localhost:5000/api/v1/tag/0051,100e
# in browser get png by loading http://localhost:5000/api/v1/image

````

Try to upload another file, verify failure, remove it.
```
http --form POST http://localhost:5000/api/v1/upload  file@MRI/PA000001/ST000001/SE000001/IM000002
http DELETE http://localhost:5000/api/v1/remove
```

Upload a non-image dicom file, get some tags, then try to get a png from it.
```
http --form POST http://localhost:5000/api/v1/upload  file@XRAY/DICOMDIR
http GET http://localhost:5000/api/v1/tag/0004,1212
http GET http://localhost:5000/api/v1/image
```

Try to upload an invalid file
```
http --form POST http://localhost:5000/api/v1/upload  file@src/dicomd.py
```

Get the image header, just because it's big binary and may break something.
```
http GET http://localhost:5000/tag/0029,1010
```



