#include "gap.h"

bool gap::predict_branch(champsim::address ip)
{
  unsigned long pc_hash = hash_pc(ip);
  unsigned long index = (pc_hash << GHR_BITS) | ghr;

  auto value = pht[index];
  return value.value() > (value.maximum / 2);
}

void gap::last_branch_result(champsim::address ip, champsim::address branch_target, bool taken, uint8_t branch_type)
{
  unsigned long pc_hash = hash_pc(ip);
  unsigned long index = (pc_hash << GHR_BITS) | ghr;

  pht[index] += taken ? 1 : -1;
  ghr = ((ghr << 1) | taken) & (TABLE_ENTRIES - 1);
}
