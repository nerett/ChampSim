#ifndef BRANCH_GAG_H
#define BRANCH_GAG_H

#include <array>
#include "address.h"
#include "modules.h"
#include "msl/fwcounter.h"

class gag : champsim::modules::branch_predictor
{
  static constexpr std::size_t GHR_LENGTH = 14;
  static constexpr std::size_t PHT_SIZE = 1 << GHR_LENGTH;
  static constexpr std::size_t BITS = 2;

  unsigned long ghr = 0;
  std::array<champsim::msl::fwcounter<BITS>, PHT_SIZE> pht;

public:
  using branch_predictor::branch_predictor;

  bool predict_branch(champsim::address ip);
  void last_branch_result(champsim::address ip, champsim::address branch_target, bool taken, uint8_t branch_type);
};

#endif
