CXX      = c++
CXXFLAGS = -std=c++17 -Wall -Wextra -Werror -O2

OBJS     = main.o json.o api.o

prog: $(OBJS)
	$(CXX) $(CXXFLAGS) -o prog $(OBJS)

main.o: main.cpp api.h json.h
	$(CXX) $(CXXFLAGS) -c main.cpp

json.o: json.cpp json.h
	$(CXX) $(CXXFLAGS) -c json.cpp

api.o: api.cpp api.h json.h
	$(CXX) $(CXXFLAGS) -c api.cpp

clean:
	rm -f prog $(OBJS)

.PHONY: clean
