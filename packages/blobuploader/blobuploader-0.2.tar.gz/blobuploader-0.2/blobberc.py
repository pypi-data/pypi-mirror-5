#!/usr/bin/env python
"""Usage: blobberc.py -u URL... -b BRANCH [-v] [-d] FILE

-u, --url URL          URL to blobber server to upload to.
-b, --branch BRANCH    Specify branch for the file (e.g. try, mozilla-central)
-v, --verbose          Increase verbosity
-d, --dir              Instead of a file, upload multiple files from a dir name

FILE                   Local file(s) to upload
"""
import urlparse
import os
import urllib2
import hashlib
import requests
import poster.encode
import logging
import random
log = logging.getLogger(__name__)

from functools import partial

def filehash(filename, hashalgo):
    h = hashlib.new(hashalgo)
    with open(filename, 'rb') as f:
        for block in iter(partial(f.read, 1024 ** 2), ''):
            h.update(block)
    return h.hexdigest()


sha1sum = partial(filehash, hashalgo='sha1')


def upload_file(hosts, filename, branch, hashalgo='sha1',
                blobhash=None, attempts=10):

    if blobhash is None:
        blobhash = filehash(filename, hashalgo)

    log.info("Attempting to upload file %s." % filename)
    host_pool = hosts[:]
    n = 1
    while n <= attempts:
        random.shuffle(host_pool)
        host = host_pool[0]
        log.info("Picking up %s host after shuffling." % host)
        post_params = {
            'host': host,
            'filename': filename,
            'branch': branch,
            'hashalgo': hashalgo,
            'blobhash': blobhash,
        }
        log.info("Call _post_file - attempt #%d." % (n))
        if _post_file(**post_params):
            log.info("File %s was uploaded successfully at %s." %
                        (filename, host))
            break
        n += 1

    if n == attempts+1:
        log.info("Nr. of attempts exceeded. Uploading %s file failed!" %
                    (filename))


def _post_file(host, filename, branch, hashalgo, blobhash):
    url = urlparse.urljoin(host, '/blobs/{}/{}'.format(hashalgo, blobhash))
    datagen, headers = poster.encode.multipart_encode({
        'data': open(filename, 'rb'),
        'filename': filename,
        'filesize': os.path.getsize(filename),
        'branch': branch,
        'mimetype': 'application/octet-stream',
    })
    req = urllib2.Request(url, datagen, headers)
    log.debug("Posting file to %s", url)
    try:
        urllib2.urlopen(req)
    except urllib2.URLError:
        log.debug("Posting file %s failed." % filename)
        return False

    log.debug("Posting file %s sucessfully." % filename)
    return True


def upload_dir(hosts, dirname, branch, hashalgo='sha1'):
    log.info("Opening the directory to read the files ...")
    dir_files = [f for f in os.listdir(dirname)
                 if os.path.isfile(os.path.join(dirname, f))]

    log.debug("Iterate through all files in directory:")
    for f in dir_files:
        filename = os.path.join(dirname, f)
        upload_file(hosts, filename, branch)

    log.info("Iteration through directory files is now over.")


def main():
    from docopt import docopt
    import poster.streaminghttp
    poster.streaminghttp.register_openers()

    args = docopt(__doc__)

    if args['--verbose']:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",
                        level=loglevel)
    logging.getLogger('requests').setLevel(logging.WARN)

    if args['--dir']:
        if os.path.isdir(args['FILE']):
            upload_dir(args['--url'], args['FILE'], branch=args['--branch'])
    else:
        if os.path.isfile(args['FILE']):
            upload_file(args['--url'], args['FILE'], branch=args['--branch'])

if __name__ == '__main__':
    main()
