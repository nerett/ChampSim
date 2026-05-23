#include "pap.h"

bool pap::predict_branch(champsim::address ip)
{
  unsigned long pc_hash = hash_pc(ip);
  unsigned long local_history = bht[pc_hash];
  unsigned long index = (pc_hash << LHR_BITS) | local_history;

  auto value = pht[index];
  return value.value() > (value.maximum / 2);
}

void pap::last_branch_result(champsim::address ip, champsim::address branch_target, bool taken, uint8_t branch_type)
{
  unsigned long pc_hash = hash_pc(ip);
  unsigned long local_history = bht[pc_hash];
  unsigned long index = (pc_hash << LHR_BITS) | local_history;

  pht[index] += taken ? 1 : -1;
  bht[pc_hash] = ((local_history << 1) | taken) & (TABLE_ENTRIES - 1);
}
