from nose.tools import assert_true,assert_false,assert_equal
from nose import SkipTest
import os
import tempfile

import planarity


class TestPlanarity:

    def setUp(self):
        self.k5_adj_symmetric={0: {1: {}, 2: {}, 3: {}, 4: {}},
                     1: {0: {}, 2: {}, 3: {}, 4: {}},
                     2: {0: {}, 1: {}, 3: {}, 4: {}},
                     3: {0: {}, 1: {}, 2: {}, 4: {}},
                     4: {0: {}, 1: {}, 2: {}, 3: {}}}

        self.k5_adj={0: {1: {}, 2: {}, 3: {}, 4: {}},
                     1: {2: {}, 3: {}, 4: {}},
                     2: {3: {}, 4: {}},
                     3: {4: {}},
                     4: {}}

        self.k5_adj_set={0: set([1,2,3,4]),
                         1: set([2,3,4]),
                         2: set([3,4]),
                         3: set([4]),
                         4: set([])}

        self.k5_adj_list={0: list([1,2,3,4]),
                         1: list([2,3,4]),
                         2: list([3,4]),
                         3: list([4]),
                         4: list([])}

        self.k5_edgelist=[(0, 1),
                          (0, 2),
                          (0, 3),
                          (0, 4),
                          (1, 2),
                          (1, 3),
                          (1, 4),
                          (2, 3),
                          (2, 4),
                          (3, 4)]

        self.p4_adj={0: {1: {}},
                     1: {0: {}, 2: {}},
                     2: {1: {}, 3: {}},
                     3: {2: {}}}

        self.p4_edgelist=[(0, 1), (1, 2), (2, 3)]


    def test_is_planar_edgelist_input(self):
        P=planarity.PGraph(self.p4_edgelist)
        assert_true(P.is_planar())
        P=planarity.PGraph(self.k5_edgelist)
        assert_false(P.is_planar())

    def test_is_planar_edgelist_input_function(self):
        assert_false(planarity.is_planar(self.k5_edgelist))

    def test_is_planar_adj_input(self):
        P=planarity.PGraph(self.p4_adj)
        assert_true(P.is_planar())
        P=planarity.PGraph(self.k5_adj)
        assert_false(P.is_planar())

    def test_is_planar_adj_input_function(self):
        assert_false(planarity.is_planar(self.k5_adj))

    def test_is_planar_adj_symmetric(self):
        P=planarity.PGraph(self.k5_adj_symmetric)
        assert_false(P.is_planar())

    def test_is_planar_adj_set(self):
        P=planarity.PGraph(self.k5_adj_set)
        assert_false(P.is_planar())

    def test_is_planar_adj_list(self):
        P=planarity.PGraph(self.k5_adj_list)
        assert_false(P.is_planar())

    def test_goldner_harary(self):
        # goldner-harary graph
        # http://en.wikipedia.org/wiki/Goldner%E2%80%93Harary_graph
        # a maximal planar graph
        e= [(1,2 ),( 1,3 ),( 1,4 ),( 1,5 ),( 1,7 ),( 1,8 ),( 1,10 ),
            ( 1,11 ),( 2,3 ),( 2,4 ),( 2,6 ),( 2,7 ),( 2,9 ),( 2,10 ),
            ( 2,11 ),( 3,4 ),( 4,5 ),( 4,6 ),( 4,7 ),( 5,7 ),( 6,7 ),
            ( 7,8 ),( 7,9 ),( 7,10 ),( 8,10 ),( 9,10 ),( 10,11)]
        P=planarity.PGraph(e)
        assert_true(P.is_planar())

    def test_kuratowski_k5(self):
        P=planarity.PGraph(self.k5_edgelist)
        edges=P.kuratowski_edges()
        assert_equal(sorted(edges),sorted(self.k5_edgelist))

    def test_kuratowski_k5_function(self):
        edges=planarity.kuratowski_edges(self.k5_edgelist)
        assert_equal(sorted(edges),sorted(self.k5_edgelist))

    def test_no_kuratowski_k5m(self):
        edges=self.k5_edgelist[:]
        edges.remove((0,1))
        P=planarity.PGraph(edges)
        edges=P.kuratowski_edges()
        assert_equal(edges,[])

    def test_draw_text(self):
        e=([1,2],)
        P=planarity.PGraph(e)
        s=P.ascii().decode()
        assert_equal(s,'1\n|\n2\n \n')

    def test_write_adjlist(self):
        e=([1,2],)
        P=planarity.PGraph(e)
        fname=tempfile.mktemp()
        P.write(fname)
        d=open(fname).read()
        answer='N=2\n1: 2 0\n2: 1 0\n'
        assert_equal(d,answer)
        os.unlink(fname)
