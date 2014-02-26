# Gridftp benchmarks

Can run gridftp & scp transfers, creating files on the fly.

 - doesn't create any directories except for the working directory that is specified in the arguments
 - also, doesn't check size of files if they already exist in either working directory or source

## Gridftp

### local to gridftp:

    transfer.py --working-directory /tmp/transfer --sizes 1,2,4,8,16  -t gsiftp://transfer.uoa.nesi.org.nz/tmp/

### gridftp to local

    transfer.py --working-directory /tmp/transfer --sizes 1,2,4,8,16  -s gsiftp://transfer.uoa.nesi.org.nz/tmp/ -t /tmp/target

### gridftp to gridftp

    transfer.py --working-directory /tmp/transfer --sizes 1,2,4,8,16  -s gsiftp://transfer.uoa.nesi.org.nz/tmp/ -t gsiftp://gram.uoa.nesi.org.nz/tmp/

## Scp

### local to remote

    transfer.py --working-directory /tmp/transfer --sizes 1,4,8,16  -t gram.uoa.nesi.org.nz:/tmp/

### remote to local

    transfer.py --working-directory /tmp/transfer --sizes 1,4,8,16 -s gram.uoa.nesi.org.nz:/tmp/ -t /tmp/scptransfers


