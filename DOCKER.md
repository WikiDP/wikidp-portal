Docker Instructions
===================
There are two docker images for WikiDP, one for use as a local development server
the other as a demonstration server. Unless you intend to write and test your own
code the demonstration server is probably the right container for you.

Docker Development Server
------------------------------
The development server is based on the `python:3.6-stretch` Docker image. It's
an order of magnitude larger than the optimised demonstration server, 1GB to
100MB. The advantage is it comes with Python and build tools installed.

### Building the development environment image
You'll need to build a copy of the Docker image from the `Dockerfile.dev`
[Dockerfile](https://docs.docker.com/engine/reference/builder/) before starting
the container for the first time. The `-t wikidp-dev` arg means we creating a machine
with tag `wikidp-dev`, in fact the full tag is `wikidp-dev:latest`. The
`-f Dockerfile.dev` arg uses a named Dockerfile, `Dockerfile.dev` as a build source.

```
$ docker build -t wikidp-dev -f Dockerfile.dev .

...

Successfully built 0069200c9c28
Successfully tagged wikidp-dev:latest

$ docker image ls

REPOSITORY    TAG         IMAGE ID            CREATED             SIZE
wikidp-dev    latest      0069200c9c28        4 minutes ago       1.14GB
```
The same command can be used to update the image if changes are made to `Dockerfile.dev`.

### Run the Docker development environment
This command creates a named container from the `wikidp-dev` image created above.
The `-p 5000:5000` arg maps port 5000 on the host to the same on the container,
`-v "$PWD":/wikidp` arg share's the current host directory (local project root) as
the named volume `/wikidp` in the container. The `--rm` means the container
is cleaned up automatically when stopped, while `--name wikidp-dev` explicitly
names the container (with the image name).

From within the project directory:
```
docker run -p 5000:5000 -v "$PWD":/wikidp --rm --name wikidp-dev wikidp-dev
```
The server should be available on <http://0.0.0.0:5000/>.

Docker Demonstration Server
---------------------------
This is a lightweight optimised server meant to be easily downloaded from Dockerhub
and quickly deployed. It's easier to use than the development server but is less
flexible.
### Build a copy the WikiDP server
From the project root directory:
```
$ docker build -t wikidp .

...

Successfully built 3625ea189aea
Successfully tagged wikidp:latest

$ docker image ls

REPOSITORY    TAG         IMAGE ID            CREATED              SIZE
wikidp        latest      3625ea189aea        About a minute ago   95.4MB
```

### Run the demonstration server container
```
docker run --name wikidp wikidp
```
