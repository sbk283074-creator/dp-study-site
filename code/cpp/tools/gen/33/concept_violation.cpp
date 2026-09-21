// The payoff of a concept: the error names the requirement that was not met,
// instead of pointing into the body of the template.
#include <concepts>

template <std::integral T>
T twice(T n) { return n + n; }

int main() { return twice(1.5); }
