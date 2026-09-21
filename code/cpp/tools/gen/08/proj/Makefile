CXX      = clang++
CXXFLAGS = -std=c++17 -Wall -Wextra -Werror

prog: main.o wire.o
	$(CXX) $(CXXFLAGS) -o prog main.o wire.o

main.o: main.cpp wire.h
	$(CXX) $(CXXFLAGS) -c main.cpp

wire.o: wire.cpp wire.h
	$(CXX) $(CXXFLAGS) -c wire.cpp

clean:
	rm -f prog *.o
