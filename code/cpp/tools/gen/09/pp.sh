cat > config.h <<'EOF'
#ifndef CONFIG_H
#define CONFIG_H

#define MAX_ITEMS 3
#define SQUARE(x) ((x) * (x))

#endif
EOF
cat > expand.cpp <<'EOF'
#include "config.h"

int value = SQUARE(MAX_ITEMS);
EOF
echo '$ clang++ -E -P expand.cpp'
clang++ -E -P expand.cpp
