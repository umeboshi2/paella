#!/bin/bash
for x in `ls *gz` ; do gzip -cd $x | tar xv -C themes ; done
