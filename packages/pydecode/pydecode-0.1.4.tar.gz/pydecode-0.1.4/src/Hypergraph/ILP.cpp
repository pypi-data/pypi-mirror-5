// Copyright [2013] Alexander Rush
#include "Hypergraph/ILP.h"

const HypergraphILP * HypergraphILP::build_ILP(
    const Hypergraph *,
    const HypergraphWeights *,
    const HypergraphConstraints *) {

}


// Add an LP var for each node and edge in the hypergraph.
void HypergraphLP::add_vars() {
  assert(_initialized);

  foreach(HNode node, _h.nodes()) {
    stringstream buf;
    buf << "node_" << node->id();
    node_vars.set_value(*node, lp_conf->addSimpleVar(0.0, buf));
  }

  foreach (HEdge edge, _h.edges()) {
    stringstream buf;
    buf << "edge_" << edge->id() << "_"<<edge->label();

    edge_vars.set_value(*edge, lp_conf->addSimpleVar(
                                            _weights.get_value(*edge) /*Obj*/,
                                            buf));
  }
  _vars_initialized = true;
}

void HypergraphLP::add_constraints( ) {
  assert(_initialized && _vars_initialized);

  foreach(HNode node, _h.nodes()) {
    // Downward edges
    if (node->edges().size() > 0) {
      GRBLinExpr sum;
      foreach (HEdge edge, node->edges()) {
        /* hyperedges[i] = sum node out ;*/
        sum += edge_vars.get(*edge);
      }
      stringstream buf;
      buf << "Downward_edge";

      lp_conf->addSimpleConstr(node_vars.get(*node) == sum, buf);
    }

    // Upward edges
    if (node->in_edges().size() > 0) {
      GRBLinExpr sum;
      foreach (HEdge edge, node->in_edges()) {
        sum += edge_vars.get(*edge);
      }
      stringstream buf;
      buf << "Upward_edge";

      lp_conf->addSimpleConstr(node_vars.get(*node) == sum, buf);
    }
  }

  stringstream buf;
  buf << "Root";
  lp_conf->addSimpleConstr(node_vars.get(_h.root()) == 1, buf);
}
