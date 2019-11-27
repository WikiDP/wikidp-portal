Docker Instructions
===================
There are two docker images for WikiDP, one for use as a local development environment
the other as a demonstration server. Unless you intend to write and test your own
code the demonstration server is probably the right container for you.

Docker Development Environment
------------------------------
### Build a copy of the image
```
$ docker build -t wikidp-dev -f Dockerfile.dev .

...

Successfully built 0069200c9c28
Successfully tagged wikidp-dev:latest

$ docker image ls

REPOSITORY                 TAG                 IMAGE ID            CREATED             SIZE
wikidp-dev                 latest              0069200c9c28        4 minutes ago       1.14GB
```

### Run the docker image
```
docker run -p 5000:5000 -v "$PWD":/wikidp --rm  --name wikidp-dev wikidp-dev
```
The server should be available on http://0.0.0.0:5000/.

Docker Demonstration Server
---------------------------
### Build a copy of the image

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

### Run the docker image
```
docker run --name wikidp wikidp
```
