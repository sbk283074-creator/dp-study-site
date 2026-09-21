echo '$ clang++ -c -std=c++17 config.cpp -o config.o'
clang++ -c -std=c++17 config.cpp -o config.o
echo '$ clang++ -c -std=c++17 main.cpp -o main.o'
clang++ -c -std=c++17 main.cpp -o main.o
echo '$ ls *.o'
ls *.o
echo '$ nm -g config.o | c++filt'
nm -g config.o | c++filt
echo '$ nm -g main.o | c++filt'
nm -g main.o | c++filt
echo '$ clang++ -o prog main.o config.o'
clang++ -o prog main.o config.o
echo '$ ./prog'
./prog
