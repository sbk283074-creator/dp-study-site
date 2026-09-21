mkdir -p include
cat > include/units.h <<'EOF'
#ifndef UNITS_H
#define UNITS_H

int metres_to_centimetres(int metres);

#endif
EOF
cat > units.cpp <<'EOF'
#include "units.h"

int metres_to_centimetres(int metres) {
    return metres * 100;
}
EOF
cat > report.cpp <<'EOF'
#include <cstdio>

#include "units.h"

int main() {
    std::printf("%d\n", metres_to_centimetres(3));
    return 0;
}
EOF
echo '$ clang++ -c -std=c++17 -Iinclude units.cpp'
clang++ -c -std=c++17 -Iinclude units.cpp
echo '$ ar rcs libunits.a units.o'
ar rcs libunits.a units.o
echo '$ clang++ -c -std=c++17 -Iinclude report.cpp'
clang++ -c -std=c++17 -Iinclude report.cpp
echo '$ clang++ -o prog -L. -lunits report.o'
clang++ -o prog -L. -lunits report.o 2>&1 | head -1
echo '$ clang++ -o prog report.o -L. -lunits'
clang++ -o prog report.o -L. -lunits
echo '$ ./prog'
./prog
