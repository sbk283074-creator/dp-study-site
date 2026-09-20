CXX      = c++
CXXFLAGS = -std=c++17 -Wall -Wextra -Werror -O2

OBJS     = main.o store.o

prog: $(OBJS)
	$(CXX) $(CXXFLAGS) -o prog $(OBJS)

main.o: main.cpp store.h
	$(CXX) $(CXXFLAGS) -c main.cpp

store.o: store.cpp store.h
	$(CXX) $(CXXFLAGS) -c store.cpp

clean:
	rm -f prog $(OBJS)

.PHONY: clean
