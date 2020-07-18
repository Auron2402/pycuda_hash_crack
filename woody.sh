#!/usr/bin/bash -l
echo "login woody:"
cd pycuda_hash_crack || exit
/usr/bin/qsub.tinygpu -cwd gpu_node.sh
