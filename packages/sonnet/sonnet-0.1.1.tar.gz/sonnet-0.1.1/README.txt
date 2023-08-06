========================
Sonnet J(SON + Net)workX
========================

Sonnet wraps a NetworkX graph and produces detailed JSON output for use with JavaScript to produce detailed graph visualizations in the browser.

Getting Started
===============

Install Sonnet::

	pip install sonnet

Build a NetworkX graph::
	
	import networkx as nx

	g = nx.gnp_random_graph(200, 0.5)

Wrap it with Sonnet::

	import sonnet as sn

	s = sn.Sonnet(g)

Build stats directly into node directory using modified NetworkX algorithms. Currently available: degree, degree_centrality, in_degree_centrality, out_degree_centrality, closeness_centrality, betweenness_centrality, eigenvector_centrality::

	s.betweenness_centrality()

	s.nodes()

	[{'betweenness_centrality': 0.2222222222222222, 'id': 0},
	 {'betweenness_centrality': 0.2152777777777778, 'id': 1},
	 {'betweenness_centrality': 0.006944444444444444, 'id': 2},
	 {'betweenness_centrality': 0.39814814814814814, 'id': 3},
	 {'betweenness_centrality': 0.11805555555555555, 'id': 4},
	 {'betweenness_centrality': 0.020833333333333332, 'id': 5},
	 {'betweenness_centrality': 0.06944444444444445, 'id': 6},
	 {'betweenness_centrality': 0.0, 'id': 7},
	 {'betweenness_centrality': 0.018518518518518517, 'id': 8},
	 {'betweenness_centrality': 0.041666666666666664, 'id': 9}]

Find communities and assign nodes to group based on community::

	s.find_communities()

Rank node size by nodes by attribute::

	s.rank_nodes(attr='betweenness_centrality')

Now we have a nodes with lots of relevant data::


Produce JSON data::

	json_graph = s.jsonify()


D3Graph
=======

D3Graph is designed to produce JSON output for D3.js graphs. It works just like Sonnet, but it has extra attributes set at during init.

Compare::

	s = sn.Sonnet()

	vars(s)

	d = ns.D3Graph()

	vars(d)
