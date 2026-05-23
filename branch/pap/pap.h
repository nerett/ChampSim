#ifndef BRANCH_PAP_H
#define BRANCH_PAP_H

#include <array>
#include "address.h"
#include "modules.h"
#include "msl/fwcounter.h"

class pap : champsim::modules::branch_predictor
{
  static constexpr std::size_t PC_BITS = 9;
  static constexpr std::size_t LHR_BITS = 5;
  static constexpr std::size_t NUM_TABLES = 1 << PC_BITS;
  static constexpr std::size_t TABLE_ENTRIES = 1 << LHR_BITS;
  static constexpr std::size_t PHT_SIZE = NUM_TABLES * TABLE_ENTRIES;
  static constexpr std::size_t BITS = 2;

  [[nodiscard]] static constexpr auto hash_pc(champsim::address ip) {
      return (ip.to<unsigned long>() >> 2) & (NUM_TABLES - 1);
  }

  std::array<unsigned long, NUM_TABLES> bht{};
  std::array<champsim::msl::fwcounter<BITS>, PHT_SIZE> pht;

public:
  using branch_predictor::branch_predictor;

  bool predict_branch(champsim::address ip);
  void last_branch_result(champsim::address ip, champsim::address branch_target, bool taken, uint8_t branch_type);
};

#endif
