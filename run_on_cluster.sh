#!/usr/bin/bash -l
echo "login cluster:"
cd pycuda_hash_crack || exit

# delete old output files
rm gpu_node.sh.*

ssh woody.rrze.uni-erlangen.de #'bash -s' < woody.sh

# print outputs
cat gpu_node.sh.*

