import binascii
import os
import tarfile
import tempfile
import threading


import requests
from flask import Flask, jsonify, request, send_from_directory, session


CHUNK_SIZE = 4096

# Space-separated list of repositories to download immediately.
INITIAL_REPOSITORIES = os.environ.get("INITIAL_REPOSITORIES", "park")

PORT = int(os.environ.get("PORT", 7466))
REPOSITORY_URL = os.environ.get("REPOSITORY_URL", "http://pages.cs.wisc.edu/~hartung/paradrop/imserve")
SNAP_DATA = os.environ.get("SNAP_DATA", "/tmp")


complete_repositories = dict()
download_progress = dict()
download_threads = dict()
server = Flask(__name__)


def add_complete_repository(repository):
    d = os.path.join(SNAP_DATA, repository)

    complete_repositories[repository] = {
        "count": len(os.listdir(d)),
        "progress": 1,
        "status": "available"
    }


def download_repository(repository):
    download_progress[repository] = 0
    downloaded = 0
    download_complete = False

    temp = tempfile.TemporaryFile()

    url = "{}/{}.tar".format(REPOSITORY_URL, repository)
    try:
        with requests.get(url, stream=True) as response:
            if response.ok:
                content_length = float(response.headers['content-length'])

                for chunk in response.iter_content(CHUNK_SIZE):
                    downloaded += len(chunk)
                    download_progress[repository] = downloaded / content_length
                    temp.write(chunk)

                download_progress[repository] = 1
                download_complete = True

        if download_complete:
            temp.seek(0)
            tar = tarfile.open(fileobj=temp)
            tar.extractall(SNAP_DATA)
            add_complete_repository(repository)
    except:
        pass

    # Clean up thread state. Even if the download was not successful, we want
    # to remove these entries so that it can be retried.
    if repository in download_progress:
        del download_progress[repository]
    if repository in download_threads:
        del download_threads[repository]


def start_download(repository):
    if repository not in download_threads:
        thread = threading.Thread(target=download_repository, args=[repository])
        download_threads[repository] = thread
        thread.start()


@server.route("/")
def list_repositories():
    return jsonify(complete_repositories)


@server.route("/<repository>")
def get_repository(repository):
    result = {
        "count": 0,
        "progress": 0,
        "status": "unknown",
        "images": []
    }

    d = os.path.join(SNAP_DATA, repository)
    if os.path.isdir(d):
        images = os.listdir(d)
        result['count'] = len(images)
        result['progress'] = 1
        result['status'] = "available"
        result['images'] = images
        add_complete_repository(repository)
        return jsonify(result)
    elif repository in download_threads:
        result['progress'] = download_progress.get(repository, 1)
        result['status'] = "preparing"
        return jsonify(result)
    else:
        result['progress'] = 0
        result['status'] = "preparing"
        start_download(repository)
        return jsonify(result)


@server.route("/<repository>/video.jpg")
def get_video(repository):
    d = os.path.join(SNAP_DATA, repository)
    if os.path.isdir(d):
        images = sorted(os.listdir(d))
    else:
        start_download(repository)
        images = []

    # Directory is empty or does not exist.
    if len(images) == 0:
        d = os.path.abspath(os.path.dirname(__file__))
        return send_from_directory(d, "missing.jpg")

    index = session.get(repository, 0)
    if index >= len(images):
        index = 0

    session[repository] = index + 1

    return send_from_directory(d, images[index])


def initialize():
    for name in INITIAL_REPOSITORIES.split():
        if len(name) == 0:
            continue

        d = os.path.join(SNAP_DATA, name)
        if os.path.isdir(d):
            print("Initialize: found repository {}".format(name))
            add_complete_repository(name)
        else:
            print("Initialize: download repository {}".format(name))
            start_download(name)


def main():
    initialize()

    # Setting the secret key enables session support.
    Flask.secret_key = binascii.b2a_hex(os.urandom(32))

    server.run(host="0.0.0.0", port=PORT)
