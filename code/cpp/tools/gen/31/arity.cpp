// Arity is fixed by the language. `!` is unary, so an operator! taking two
// parameters is not an overload of anything -- it is a syntax error.
struct Vec2 { double x; double y; };

bool operator!(Vec2 a, int extra) { return a.x == 0.0 && a.y == 0.0 && extra == 0; }

int main() { return 0; }
