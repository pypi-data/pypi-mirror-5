#!/bin/bash

#command old-release-file new-release-file

TMPDIR=$(mktemp -d)
OLDFILE=$1
NEWFILE=$2
CURDIR=$PWD

cd $TMPDIR
tar xf $OLDFILE
mv WingDBG WingDBG-old
tar xf $NEWFILE
diff -urNw WingDBG-old WingDBG> WingDBG.patch
cd $CURDIR
patch -p0 -i $TMPDIR/WingDBG.patch
rm -rf $TMPDIR

exit 0
