echo '$ make clean'
make clean
echo '$ make'
make
echo '$ ./prog'
./prog
sleep 1
echo '$ touch config.h && make'
touch config.h && make
echo '$ make clean > /dev/null && make -f Makefile.nodep'
make clean > /dev/null && make -f Makefile.nodep
sleep 1
echo '$ touch config.h && make -f Makefile.nodep'
touch config.h && make -f Makefile.nodep
