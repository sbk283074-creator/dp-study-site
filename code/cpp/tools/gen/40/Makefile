CXXFLAGS = -std=c++17 -Wall -Wextra -Werror
LDLIBS   = -pthread

prog: main.cpp pool.cpp pool.h
	$(CXX) $(CXXFLAGS) -o prog main.cpp pool.cpp $(LDLIBS)

clean:
	rm -f prog
