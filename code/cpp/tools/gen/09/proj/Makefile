CXX      = clang++
CXXFLAGS = -std=c++17 -Wall -Wextra -Werror

OBJECTS  = main.o config.o

prog: $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $@ $(OBJECTS)

main.o: main.cpp config.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

config.o: config.cpp config.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f prog *.o

.PHONY: clean
