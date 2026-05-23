#include "plru.h"

plru::plru(CACHE* cache) : plru(cache, cache->NUM_SET, cache->NUM_WAY) {}

plru::plru(CACHE* cache, long sets, long ways) : replacement(cache), NUM_WAY(ways), tree(static_cast<std::size_t>(sets), 0) {}

long plru::find_victim(uint32_t triggering_cpu, uint64_t instr_id, long set, const champsim::cache_block* current_set, champsim::address ip,
                       champsim::address full_addr, access_type type)
{
  long victim = 0;
  long shift = NUM_WAY;
  uint32_t index = 0;

  while (shift > 1) {
    shift >>= 1;
    if ((tree.at(static_cast<std::size_t>(set)) & (1ULL << index)) == 0) {
      index = index * 2 + 1;
    } else {
      index = index * 2 + 2;
      victim += shift;
    }
  }

  return victim;
}

void plru::replacement_cache_fill(uint32_t triggering_cpu, long set, long way, champsim::address full_addr, champsim::address ip, champsim::address victim_addr,
                                  access_type type)
{
  long node = way + NUM_WAY - 1;
  while (node > 0) {
    long parent = (node - 1) / 2;
    if (node == parent * 2 + 1) {
      tree.at(static_cast<std::size_t>(set)) |= (1ULL << parent);
    } else {
      tree.at(static_cast<std::size_t>(set)) &= ~(1ULL << parent);
    }
    node = parent;
  }
}

void plru::update_replacement_state(uint32_t triggering_cpu, long set, long way, champsim::address full_addr, champsim::address ip,
                                    champsim::address victim_addr, access_type type, uint8_t hit)
{
  if (hit && access_type{type} != access_type::WRITE) {
    long node = way + NUM_WAY - 1;
    while (node > 0) {
      long parent = (node - 1) / 2;
      if (node == parent * 2 + 1) {
        tree.at(static_cast<std::size_t>(set)) |= (1ULL << parent);
      } else {
        tree.at(static_cast<std::size_t>(set)) &= ~(1ULL << parent);
      }
      node = parent;
    }
  }
}
