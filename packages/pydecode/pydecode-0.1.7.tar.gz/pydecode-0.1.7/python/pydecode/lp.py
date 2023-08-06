import pulp
import pydecode.hyper as ph
from collections import defaultdict


class HypergraphLP:
    """
    Representation of a hypergraph LP.
    Requires the pulp library.

    Attributes
    -----------

    objective : float
       Get the objective of the solved LP.

    path : The hyperpath (if ILP)
       Get the path of the solved LP.

    edge_variables : Dict of edge values.
       Get the (fractional) path of the solved LP.

    """
    def __init__(self, lp, hypergraph, node_vars, edge_vars,
                 integral=False):
        r"""
        Initialize the hypergraph LP

        Parameters
        ------------

        lp : PuLP linear program

        hypergraph : :py:class:`Hypergraph`
           The hypergraph.

        node_vars :
           The node variables :math:`y(v)`
           for all :math:`v \in {\cal V}`.

        edge_vars :
           The hyperedge variables :math:`y(e)`
           for all :math:`e \in {\cal E}`.
        """

        self.lp = lp
        self.hypergraph = hypergraph
        self.node_vars = node_vars
        self.edge_vars = edge_vars
        self.integral = integral

    def solve(self, solver=None):
        r"""
        Solve the underlying hypergraph linear program
        and return the best path.

         :math:`\arg \max_{y \in {\cal X}} \theta^{\top}y`.

        Parameters
        ----------

        solver : LP solver
           A PuLP LP solver (glpsol, Gurobi, etc.)

        Returns
        ---------

        path
           The best path.
        """
        self._status = self.lp.solve()

    @property
    def path(self):
        if self._status != pulp.LpStatusOptimal:
            raise Exception("No optimal solution.")
        path_edges = [edge
                      for edge in self.hypergraph.edges
                      if pulp.value(self.edge_vars[edge.id]) == 1.0]
        return ph.Path(self.hypergraph, path_edges)

    @property
    def objective(self):
        return pulp.value(self.lp.objective)

    @property
    def edge_variables(self):
        return {edge: pulp.value(self.edge_vars[edge.id])
                for edge in self.hypergraph.edges
                if pulp.value(self.edge_vars[edge.id]) > 0.0}

    def add_constraints(self, constraints):
        """
        Add hard constraints to the hypergraph.

        Parameters
        -----------

        constraints : :py:class:`Constraints`
        """
        for constraint in constraints:
            self.lp += 0 == \
                constraint.constant + \
                sum([coeff * self.edge_vars[edge.id]
                     for (coeff, edge) in constraint])

    @staticmethod
    def make_lp(hypergraph, weights, name="", integral=False):
        r"""
        Construct a linear program from a hypergraph.

        .. math::
          \max \theta^{\top} x \\
          x(1) = 1 \\
          x(v) = \sum_{e \in {\cal E} : h(e) = v} x(e) \\
          x(v) = \sum_{e \in {\cal E} : v \in t(e)} x(e)

        Parameters
        ----------

        hypergraph : :py:class:`pydecode.hyper.Hypergraph`
        weights : :py:class:`pydecode.hyper.Weights`

        Returns
        --------

        lp : :py:class:`HypergraphLP`

        """

        if integral:
            var_type = pulp.LpInteger
        else:
            var_type = pulp.LpContinuous
        prob = pulp.LpProblem("Hypergraph Problem", pulp.LpMaximize)

        def node_name(node):
            return "node_{}".format(node.id)

        def edge_name(edge):
            return "edge_{}".format(edge.id)

        # Make variables for the nodes.
        node_vars = {node.id: pulp.LpVariable(node_name(node), 0, 1,
                                              var_type)
                     for node in hypergraph.nodes}

        edge_vars = {edge.id: pulp.LpVariable(edge_name(edge), 0, 1,
                                              var_type)
                     for edge in hypergraph.edges}

        # Build table of incoming edges
        in_edges = defaultdict(lambda: [])
        for edge in hypergraph.edges:
            for node in edge.tail:
                in_edges[node.id].append(edge)

        # max \theta x
        prob += sum([weights[edge] * edge_vars[edge.id]
                     for edge in hypergraph.edges])

        # x(r) = 1
        prob += node_vars[hypergraph.root.id] == 1

        # x(v) = \sum_{e : h(e) = v} x(e)
        for node in hypergraph.nodes:
            if node.is_terminal:
                continue
            prob += node_vars[node.id] == \
                sum([edge_vars[edge.id]
                     for edge in node.edges])

        # x(v) = \sum_{e : v \in t(e)} x(e)
        for node in hypergraph.nodes:
            if node.id == hypergraph.root.id:
                continue
            prob += node_vars[node.id] == \
                sum([edge_vars[edge.id]
                     for edge in in_edges[node.id]])

        return HypergraphLP(prob, hypergraph, node_vars,
                            edge_vars, integral)
