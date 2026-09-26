CXXFLAGS = -std=c++17 -Wall -Wextra -Werror
LDLIBS   = -lsqlite3
HEADERS  = app.hpp auth.hpp config.hpp framework.hpp http.hpp log.hpp store.hpp views.hpp

# Two programs, one build. `all` is first so that a bare `make` produces both: the
# suite needs `prog`, the operator needs `server`, and neither should depend on the
# order somebody typed targets in.
all: prog server

prog: tests.cpp units.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -o prog tests.cpp units.cpp $(LDLIBS)

server: service.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -o server service.cpp $(LDLIBS)

clean:
	rm -f prog server

.PHONY: all clean
