import os, sys

one = open('wordlists/hashesorg_1.txt', 'w', encoding='latin-1')
two = open('wordlists/hashesorg_2.txt', 'w', encoding='latin-1')
thr = open('wordlists/hashesorg_3.txt', 'w', encoding='latin-1')
vou = open('wordlists/hashesorg_4.txt', 'w', encoding='latin-1')
cnt = 1
with open('wordlists/HashesOrg.txt', 'r', encoding='latin-1') as fp:
    for line in fp:
        if cnt % 4 == 1:
            one.write(line)
        elif cnt % 4 == 2:
            two.write(line)
        elif cnt % 4 == 3:
            thr.write(line)
        elif cnt % 4 == 0:
            vou.write(line)

        cnt += 1

one.close()
two.close()
thr.close()
vou.close()
