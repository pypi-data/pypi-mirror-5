// Copyright [2013] Alexander Rush

#ifndef HYPERGRAPH_ILP_H_
#define HYPERGRAPH_ILP_H_

#include <gurobi_c++.h>

class HypergraphILP {
 public:
  static const HypergraphILP *build_ILP(
      const Hypergraph *,
      const HypergraphWeights *,
      const HypergraphConstraints *);



 private:




};


#endif  // HYPERGRAPH_ILP_H_
