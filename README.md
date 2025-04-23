# dicomd 
Errors or Issues I have thought of have been left as a comment in the code with a FIXME keyword, though fixing some of them are outside of my ability.

I used ImageMagick for the conversion of the dicom file into the png.  Until this point I had been using alpine for my base image, however it looks like the alpine ImageMagick package is lacking dicom support, so I migrated to ubuntu.

# Build
How to build the container.  I used podman, but docker should work just as well.

```
podman build -t dicomd:v2 .
```

how to run the image
```
podman run -ti --rm -p 5000:8080 dicomd:v2
```

# Endpoints and general architecture
I had initially asked if I needed to include a path of the uploaded file, which I was told I could simplify this assume the server only worked on 1 file at a time.  I realized there were issues with that.  For example if 2 clients used this api at the same time it pretty much guaranteed there would be a problem with file collision.  It also would have been severely limiting for future expandability.  Because of this, I put the effort into making the system work on path.  It wasn’t as complicated as I thought it does not remove collision on files being worked on it reduces the chance.

# Usage:
To upload a file.  POST
```
<BASE_URL>/api/v1/upload/<path>/<you>/<want>/filename
```
To get all tags in a given file.  GET
```
<BASE_URL>/api/v1/tags/<path>/<you>/<want>/filename
```
to get a specific tag.  GET
```
<BASE_URL>/api/v1/tags/<path>/<you>/<want>/filename?tag=<tag>
```
where tag is formatted as <4 hex char>,<4 hex char>.  Eg, 1234,5678
To get a png if the image.  GET
```
<BASE_URL>/api/v1/image/<path>/<you>/<want>/filename DELETE
```
To clean up and remove the image from the micro service 


# Testing/Usage examples

Upload a valid image file, get all tags from it, then get a single tag.
```
http --form POST http://localhost:5000/api/v1/upload/MRI/PA000001/ST000001/SE000001/IM000001  file@MRI/PA000001/ST000001/SE000001/IM000001
http GET http://localhost:5000/api/v1/tags/MRI/PA000001/ST000001/SE000001/IM000001
http GET http://localhost:5000/api/v1/tags/MRI/PA000001/ST000001/SE000001/IM000001?tag=0051,100e
# in browser get png by loading http://localhost:5000/api/v1/image/MRI/PA000001/ST000001/SE000001/IM000001

````

Try to upload another file to same location, verify failure, remove it.
```
http --form POST http://localhost:5000/api/v1/upload/MRI/PA000001/ST000001/SE000001/IM000001  file@MRI/PA000001/ST000001/SE000001/IM000001
http DELETE http://localhost:5000/api/v1/remove/MRI/PA000001/ST000001/SE000001/IM000001
```

Upload a non-image dicom file, get some tags, then try to get a png from it.
```
http --form POST http://localhost:5000/api/v1/upload/XRAY/DICOMDIR  file@XRAY/DICOMDIR
http GET http://localhost:5000/api/v1/tags/XRAY/DICOMDIR
http GET http://localhost:5000/api/v1/tags/XRAY/DICOMDIR?tag=0004,1212
http GET http://localhost:5000/api/v1/image/XRAY/DICOMDIR
```

Try to upload an invalid file
```
http --form POST http://localhost:5000/api/v1/upload/src/dicomd.py file@src/dicomd.py
```

Get the image header, just because it's big binary and may break something.
```
http --form POST http://localhost:5000/api/v1/upload/MRI/PA000001/ST000001/SE000001/IM000001  file@MRI/PA000001/ST000001/SE000001/IM000001
http GET http://localhost:5000/api/v1/tags/MRI/PA000001/ST000001/SE000001/IM000001?tag=0029,1010
```

# Issues and possible improvements
- ../ in paths do not provide a reasonable error message if they are early in the path, and go through and work as you would expect on a file system if later on in the url.  I’d say its not ideal.  Probably completely banning relative path information would be better.
- This code does not clean up empty directories ever
- there is likely a file length limitation on the uploaded image, but I don’t know what it is or how the code will handle a file that hits this limit.
- still running the dev we server
- 2 clients could try to work on the same file path at the same time and get in the way of each other without knowing it.
- I’m not entirely sure if the url responses should produce hyper links.  I generally think the output I have produced as responses is lacking.
- What happens if someone puts an incredibly long path in the name.  Likely something bad.  I see a possible problem here.  This may not have been a good idea not to restrict the length of the url/filepath

