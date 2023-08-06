=======
MimicDB
=======

S3 Metadata without the Latency or Costs

By maintaining a transactional record of every API call to S3, MimicDB provides
a local, isometric key-value store of data on S3. MimicDB stores everything
except the contents of objects locally. Tasks like listing, searching and
calculating storage usage on massive amounts of data are now fast and free.

On average, tasks like these are 2000x faster using MimicDB.

Boto:

    >>> c = S3Connection(KEY, SECRET)
    >>> bucket = c.get_bucket('bucket_name')
    >>> start = time.time()
    >>> bucket.get_all_keys()
    >>> print time.time() - start
    0.425064992905

Boto + MimicDB:

    >>> c = S3Connection(KEY, SECRET)
    >>> bucket = c.get_bucket('bucket_name')
    >>> start = time.time()
    >>> bucket.get_all_keys()
    >>> print time.time() - start
    0.000198841094971

Installation
=============

To install MimicDB, simply:

    $ pip install mimicdb

MimicDB requires boto.

After installing, change the boto imports from boto.s3.* to mimicdb.s3.*

Additionally, register the database at the begining of the script:

    from mimicdb import MimicDB
    MimicDB(host='localhost', port=6379, db=0)

MimicDB takes the parameters of a redis connection.
