Paradrop Image Server
=====================

This snap acts as a virtual camera by serving images in sequence from an
image repository. An image repository is simply a collection of images
that can be downloaded as a tar file from a pre-determined location.
The snap does not install with any images at first, but they will be
fetched as needed.

[![Snap Status](https://build.snapcraft.io/badge/ParadropLabs/paradrop-imserve.svg)](https://build.snapcraft.io/user/ParadropLabs/paradrop-imserve)

Image Server
------------

The snap runs an HTTP server that listens on port 7466 by default and
which exposes all of the functions of the image server.

The two main operations are to get information about a repository and
to get the next image from a repository.

GET / - List available repositories

Lists the image repositories for which the server has metadata in memory
and knows are completely downloaded, which might not be all available
repositories.

```json
{
    "park": {
        "count": 921,
        "progress": 1,
        "status": "available"
    }
}
```

GET /:repository - Describe a repository

Describe a repository status and images available. If the repository
has not been loaded to disk, this may initiate a download.

```json
{
    "count": 0,
    "progress": 0.6,
    "status": "preparing",
    "images": []
}
```

```json
{
    "count": 921,
    "progress": 1,
    "status": "available",
    "images": [
        "frame-1537814188.jpg",
        "frame-1537814192.jpg",
        "frame-1537814197.jpg",
        ...
    ]
}
```

GET /:repository/video.jpg - Download the next frame

This uses a session cookie to iterate through the files and return
a different frame each time. The server always responds with either a
JPEG image or a static image with the text, "The image is not available."
If the repository has not been loaded, the server may initiate a download
in the hopes of making it available to future calls.
