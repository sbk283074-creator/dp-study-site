CXXFLAGS = -std=c++17 -Wall -Wextra -Werror
LDLIBS   = -lsqlite3

prog: main.cpp db.cpp db.h
	$(CXX) $(CXXFLAGS) -o prog main.cpp db.cpp $(LDLIBS)

clean:
	rm -f prog
