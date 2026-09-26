CXXFLAGS = -std=c++17 -Wall -Wextra -Werror

prog: poll_server.cpp common.hpp
	$(CXX) $(CXXFLAGS) -o prog poll_server.cpp

clean:
	rm -f prog
