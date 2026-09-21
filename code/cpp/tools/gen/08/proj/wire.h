#ifndef WIRE_H
#define WIRE_H

#include <cstddef>
#include <cstdint>

/* Every integer is written most-significant byte first, the order the network
   uses and the order a hex dump reads naturally. */
void put_u16_be(std::uint8_t *out, std::uint16_t value);
void put_u32_be(std::uint8_t *out, std::uint32_t value);

std::uint16_t get_u16_be(const std::uint8_t *in);
std::uint32_t get_u32_be(const std::uint8_t *in);

unsigned popcount32(std::uint32_t value);

#endif
