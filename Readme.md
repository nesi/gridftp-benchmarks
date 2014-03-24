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

## Run consecutive tests with different parameters

### scp local to remote using different ciphers

   transfer.py --working-directory /tmp/transfer --sizes 1000  -t gram.uoa.nesi.org.nz:/tmp/ --parameters="-c {x}" -x "arcfour,arcfour128,arcfour256"

### gridftp transfer local to remote, using different parallel stream values

   transfer.py --working-directory /home/markus/temp/transfer_temp --sizes 1000  -t gsiftp://transfer-i.uoa.nesi.org.nz/~/ --parameters="-p {x}" -x 1,2,4,8,16

## Repeat tests

### scp local to remote, every 30 minutes, without limit

    transfer.py --working-directory /tmp/transfer --sizes 1,4,8,16  -t gram.uoa.nesi.org.nz:/tmp/ --repeats 0 --delta 1800

### scp local to remote, every 30 minutes, 5 times

    transfer.py --working-directory /tmp/transfer --sizes 1,4,8,16  -t gram.uoa.nesi.org.nz:/tmp/ --repeats 5 --delta 1800



