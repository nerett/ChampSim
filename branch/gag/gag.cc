#include "gag.h"

bool gag::predict_branch(champsim::address ip)
{
  auto value = pht[ghr];
  return value.value() > (value.maximum / 2);
}

void gag::last_branch_result(champsim::address ip, champsim::address branch_target, bool taken, uint8_t branch_type)
{
  pht[ghr] += taken ? 1 : -1;
  ghr = ((ghr << 1) | taken) & (PHT_SIZE - 1);
}
