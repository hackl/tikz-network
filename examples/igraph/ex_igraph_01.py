#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : ex_igraph_01.py 
# Creation  : 19 Oct 2017
# Time-stamp: <Don 2017-10-19 16:29 juergen>
#
# Copyright (c) 2017 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$ 
#
# Description : example network in igraph
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 
# =============================================================================

import igraph

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.insert(0,parentdir) 
import tikz_network as tikz


def main():
    g = igraph.Graph([(0,1), (0,2), (2,3), (3,4), (4,2), (2,5), (5,0), (6,3),
                      (5,6), (6,6)],directed=True)

    g.vs["name"] = ["Alice", "Bob", "Claire", "Dennis", "Esther", "Frank", "George"]
    g.vs["age"] = [25, 31, 18, 47, 22, 23, 50]
    g.vs["gender"] = ["f", "m", "f", "m", "f", "m", "m"]
    g.es["is_formal"] = [False, False, True, True, True, False, True, False, False]



    color_dict = {"m": "blue", "f": "pink"}
    layer_dict = {"m": 1, "f": 2}

    visual_style = {}
    visual_style["vertex_id"] = g.vs["name"]
    visual_style["vertex_size"] = 20
    visual_style["vertex_color"] = [color_dict[gender] for gender in g.vs["gender"]]
    visual_style["vertex_opacity"] = [.5 for v in g.vs]
    visual_style["vertex_label"] = g.vs["name"]
    visual_style["vertex_label_position"] = [.5 for v in g.vs]
    visual_style["vertex_label_distance"] = [1.5 for v in g.vs]
    visual_style["vertex_label_color"] = "green"
    visual_style["vertex_label_size"] = 20
    visual_style["vertex_shape"] = 'rectangle'
    visual_style["vertex_style"] = 'dashed'
    visual_style["vertex_layer"] = [layer_dict[gender] for gender in g.vs["gender"]]

    visual_style["edge_width"] = [1 + 2 * int(is_formal) for is_formal in g.es["is_formal"]]
    visual_style["edge_color"] = "red"
    visual_style["edge_opacity"] = [.5 for v in g.vs]
    visual_style["edge_curved"] = 0.1
    visual_style["edge_label"] = "red"
    visual_style["edge_label_position"] = ['above' for v in g.vs]
    visual_style["edge_label_distance"] = [.7 for v in g.vs]
    visual_style["edge_label_color"] = "blue"
    visual_style["edge_label_size"] = 20
    visual_style["edge_style"] = 'dashed'
    visual_style["edge_arrow_size"] = 1.2
    visual_style["edge_arrow_width"] = 1.2

    # visual_style["unit"] = 'mm'
    visual_style["autocurve"] = True
    visual_style["bbox"] = (500, 500)
    visual_style["layout"] = g.layout('kk')
    visual_style["margin"] = 20

    igraph.plot(g, 'ex_igraph_01.png', **visual_style)
    tikz.plot(g, 'ex_igraph_01.tex', **visual_style)
    pass

if __name__ == "__main__":
    main()


# =============================================================================
# eof
#
# Local Variables: 
# mode: python
# mode: linum
# End: 

 
