Docker Instructions
===================

Build a copy of the image
-------------------------
You must have Docker installed on your machine. From the project root directory:
```
$ docker build -t wikidp .

...

Successfully built 3625ea189aea
Successfully tagged wikidp:latest

$ docker image ls

REPOSITORY                 TAG                 IMAGE ID            CREATED              SIZE
wikidp                     latest              3625ea189aea        About a minute ago   95.4MB
```

Run the docker image
--------------------
```
docker run --name wikidp wikidp
```
