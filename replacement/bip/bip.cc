#include "bip.h"
#include <algorithm>

bip::bip(CACHE* cache) : bip(cache, cache->NUM_SET, cache->NUM_WAY) {}

bip::bip(CACHE* cache, long sets, long ways) : replacement(cache), NUM_WAY(ways), last_used_cycles(static_cast<std::size_t>(sets * ways), 0) {}

long bip::find_victim(uint32_t triggering_cpu, uint64_t instr_id, long set, const champsim::cache_block* current_set, champsim::address ip,
                      champsim::address full_addr, access_type type)
{
  auto begin = std::next(std::begin(last_used_cycles), set * NUM_WAY);
  auto end = std::next(begin, NUM_WAY);
  auto victim = std::min_element(begin, end);
  return std::distance(begin, victim);
}

void bip::replacement_cache_fill(uint32_t triggering_cpu, long set, long way, champsim::address full_addr, champsim::address ip, champsim::address victim_addr,
                                 access_type type)
{
  bip_counter++;
  if (bip_counter % 32 == 0) {
    last_used_cycles.at(static_cast<std::size_t>(set * NUM_WAY + way)) = cycle++;
  } else {
    auto begin = std::next(std::begin(last_used_cycles), set * NUM_WAY);
    auto end = std::next(begin, NUM_WAY);
    last_used_cycles.at(static_cast<std::size_t>(set * NUM_WAY + way)) = *std::min_element(begin, end);
  }
}

void bip::update_replacement_state(uint32_t triggering_cpu, long set, long way, champsim::address full_addr, champsim::address ip,
                                   champsim::address victim_addr, access_type type, uint8_t hit)
{
  if (hit && access_type{type} != access_type::WRITE)
    last_used_cycles.at(static_cast<std::size_t>(set * NUM_WAY + way)) = cycle++;
}
