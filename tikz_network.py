#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : tikz_network.py 
# Creation  : 18 Oct 2017
# Time-stamp: <Don 2017-10-19 16:51 juergen>
#
# Copyright (c) 2017 Jürgen Hackl <hackl@ibi.baug.ethz.ch>
#               http://www.ibi.ethz.ch
# $Id$ 
#
# Description : plotting igraph networks to tikz-networks
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
import numpy as np
from igraph.drawing.graph import AbstractGraphDrawer
from igraph.drawing.metamagic import AttributeCollectorBase
from igraph.drawing.colors import color_name_to_rgba
import collections

class plot:
    def __init__(self, graph, filename, *args, **kwds):
        drawer = TikzGraphDrawer()
        drawer.draw(graph, filename, **kwds)
        pass


class UnitConverter(object):
    def __init__(self, input_unit='px',output_unit='px'):
        self.digit = 4
        self.input_unit = input_unit
        self.output_unit = output_unit

    def px_to_mm(self,measure):
        return measure * 0.26458333333719

    def px_to_pt(self,measure):
        return measure * 0.75

    def pt_to_mm(self,measure):
        return measure * 0.352778

    def mm_to_px(self,measure):
        return measure * 3.779527559

    def mm_to_pt(self,measure):
        return measure * 2.83465

    def conv(self,value):
        measure = float(value)
        # to cm
        if self.input_unit == 'mm' and self.output_unit == 'cm':
            value = measure/10
        if self.input_unit == 'pt' and self.output_unit == 'cm':
            value = self.pt_to_mm(measure)/10
        if self.input_unit == 'px' and self.output_unit == 'cm':
            value = self.px_to_mm(measure)/10
        if self.input_unit == 'cm' and self.output_unit == 'cm':
            value = measure
        # to pt
        if self.input_unit == 'px' and self.output_unit == 'pt':
            value = self.px_to_pt(measure)
        if self.input_unit == 'mm' and self.output_unit == 'pt':
            value = self.mm_to_pt(measure)
        if self.input_unit == 'cm' and self.output_unit == 'pt':
            value = self.mm_to_pt(measure)*10
        if self.input_unit == 'pt' and self.output_unit == 'pt':
            value = measure
        # to px
        if self.input_unit == 'mm' and self.output_unit == 'px':
            value = self.mm_to_px(measure)
        if self.input_unit == 'cm' and self.output_unit == 'px':
            value = self.mm_to_px(10*measure)
        if self.input_unit == 'pt' and self.output_unit == 'px':
            value = measure*4/3
        if self.input_unit == 'px' and self.output_unit == 'px':
            value = measure
        # else:
        #     raise NotImplementedError("The units are not supported!")
        return np.round(value,self.digit)

class TikzGraphDrawer(AbstractGraphDrawer):
    """Abstract class that serves as a base class for anything that
    draws an igraph.Graph."""

    def __init__(self):

        self.digit = 3
        self.vertex_defaults = dict(
            size = "",
            color = "",
            opacity = "",
            label = "",
            label_position = "",
            label_distance = "",
            label_color = "",
            label_size = "",
            shape = "",
            style = "",
            layer = "",
        )
        self.edge_defaults = dict(
            width = "",
            color = "",
            opacity = "",
            curved = "",
            label = "",
            label_position = "",
            label_distance = "",
            label_color = "",
            label_size = "",
            style = "",
            arrow_size = "",
            arrow_width = "",
        )

        pass

    def draw(self, graph, filename, *args, **kwds):
        # Some abbreviations for sake of simplicity
        directed = graph.is_directed()

        # Calculate/get the layout of the graph
        layout = self.ensure_layout(kwds.get("layout", None), graph)

        # Determine the size of the margin on each side
        margin = kwds.get("margin", 0)
        try:
            margin = list(margin)
        except TypeError:
            margin = [margin]
        while len(margin)<4:
            margin.extend(margin)

        unit = kwds.get("unit", ('px','px'))
        if isinstance(unit,tuple):
            px = UnitConverter(unit[0],'px')
            cm = UnitConverter(unit[0],'cm')
            pt = UnitConverter(unit[1],'pt')
        else:
            px = UnitConverter(unit,'px')
            cm = UnitConverter(unit,'cm')
            pt = UnitConverter(unit,'pt')
        px2cm = UnitConverter('px','cm')
        # Contract the drawing area by the margin and fit the layout
        box = kwds.get("bbox", (600,600))
        self.bbox = igraph.drawing.utils.BoundingBox(px.conv(box[0]),px.conv(box[1]))
        bbox = self.bbox.contract(margin)
        layout.fit_into(bbox, keep_aspect_ratio=kwds.get("keep_aspect_ratio", False))

        # Decide whether we need to calculate the curvature of edges
        # automatically -- and calculate them if needed.
        autocurve = kwds.get("autocurve", None)
        if autocurve or (autocurve is None and \
                "edge_curved" not in kwds and "curved" not in graph.edge_attributes() \
                and graph.ecount() < 10000):
            from igraph import autocurve
            default = kwds.get("edge_curved", 0)
            if default is True:
                default = 0.5
            default = float(default)
            kwds["edge_curved"] = autocurve(graph, attribute=None, default=default)


        def curve_conv(curved):
            if curved == 0:
                return 0
            else:
                v1 = np.array([0,0])
                v2 = np.array([1,1])
                v3 = np.array([(2*v1[0]+v2[0]) / 3.0 - curved * 0.5 * (v2[1]-v1[1]),
                               (2*v1[1]+v2[1]) / 3.0 + curved * 0.5 * (v2[0]-v1[0])
                ])
                vec1 = v2-v1
                vec2 = v3 -v1
                angle = np.rad2deg(np.arccos(np.dot(vec1,vec2) / np.sqrt((vec1*vec1).sum()) / np.sqrt((vec2*vec2).sum())))
                return np.round(np.sign(curved) * angle * -1,self.digit)


        # Custom color converter function
        def color_conv(color):
            if not color is "":
                rgba = color_name_to_rgba(color)
                RGB = [str(int(rgba[0]*255)),
                       str(int(rgba[1]*255)),
                       str(int(rgba[2]*255))]
                color = '{'+'.,'.join(RGB)+'}'
            return color

        # Custom label size converter function
        def label_size_conv(label_size):
            if not label_size is "":
                return np.round(pt.conv(label_size)/7,self.digit)

        # Construct the visual vertex/edge builders
        class VisualVertexBuilder(AttributeCollectorBase):
            """Collects some visual properties of a vertex for drawing"""
            _kwds_prefix = "vertex_"
            size = str(self.vertex_defaults["size"])
            color = (str(self.vertex_defaults["color"]), color_conv)
            opacity = str(self.vertex_defaults["opacity"])
            label = str(self.vertex_defaults["label"])
            label_position = str(self.vertex_defaults["label_position"])
            label_distance = str(self.vertex_defaults["label_distance"])
            label_color = (str(self.vertex_defaults["label_color"]), color_conv)
            label_size = (str(self.vertex_defaults["label_size"]),label_size_conv)
            shape = str(self.vertex_defaults["shape"])
            style = str(self.vertex_defaults["style"])
            layer = str(self.vertex_defaults["layer"])

        class VisualEdgeBuilder(AttributeCollectorBase):
            """Collects some visual properties of an edge for drawing"""
            _kwds_prefix = "edge_"
            width = str(self.edge_defaults["width"])
            color = (str(self.edge_defaults["color"]), color_conv)
            opacity = str(self.edge_defaults["opacity"])
            curved = (str(self.edge_defaults["curved"]), curve_conv)
            label = str(self.edge_defaults["label"])
            label_position = str(self.edge_defaults["label_position"])
            label_distance = str(self.edge_defaults["label_distance"])
            label_color = (str(self.edge_defaults["label_color"]), color_conv)
            label_size = (str(self.edge_defaults["label_size"]),label_size_conv)
            style = str(self.edge_defaults["style"])
            arrow_size = str(self.edge_defaults["arrow_size"])
            arrow_width = str(self.edge_defaults["arrow_width"])

        vertex_builder = VisualVertexBuilder(graph.vs, kwds)
        edge_builder = VisualEdgeBuilder(graph.es, kwds)

        # Create Vertices
        if "vertex_id" in kwds:
            vertex_ids = kwds["vertex_id"]
            if isinstance(vertex_ids, str):
                vertex_ids = graph.vs[vertex_id]
        else:
            vertex_ids = range(graph.vcount())
        vertex_ids = [str(identifier) for identifier in vertex_ids]

        self.vertices = []
        for vertex_id, vertex, coords in zip(vertex_ids, vertex_builder,layout):
            v = []
            v.append('x='+str(px2cm.conv(coords[0]))) if not coords[0] is "" else None
            v.append('y='+str(-px2cm.conv(coords[1]))) if not coords[1] is "" else None
            v.append('size='+str(cm.conv(vertex.size))) if not vertex.size is "" else None
            v.append('color='+vertex.color) if not vertex.color is "" else None
            v.append('opacity='+vertex.opacity) if not vertex.opacity is "" else None
            v.append('label='+vertex.label) if not vertex.label is "" else None
            v.append('position='+vertex.label_position) if not vertex.label_position is "" else None
            v.append('distance='+str(cm.conv(vertex.label_distance))) if not vertex.label_distance is "" else None
            v.append('fontcolor='+vertex.label_color) if not vertex.label_color is "" else None
            v.append('fontscale='+str(vertex.label_size)) if not vertex.label_size is None else None
            v.append('shape='+vertex.shape) if not vertex.shape is "" else None
            v.append('style={'+vertex.style+'}') if not vertex.style is "" else None
            v.append('layer='+str(vertex.layer)) if not vertex.layer is "" else None
            v.append('RGB') if not vertex.color is "" else None
            self.vertices.append([vertex_id,v])

        # Create Edges
        edge_ids = []
        for v1, v2 in graph.get_edgelist():
            edge_ids.append((vertex_ids[v1],vertex_ids[v2]))

        self.edges = []
        for edge_id, edge in zip(edge_ids, edge_builder):
            e = []
            e.append('lw='+str(pt.conv(edge.width))) if not edge.width is "" else None
            e.append('color='+edge.color) if not edge.color is "" else None
            e.append('opacity='+edge.opacity) if not edge.opacity is "" else None
            e.append('bend='+str(edge.curved)) if not edge.curved is 0 else None
            e.append('label='+edge.label) if not edge.label is "" else None
            e.append('position='+edge.label_position) if not edge.label_position is "" else None
            e.append('distance='+edge.label_distance) if not edge.label_distance is "" else None
            e.append('fontcolor='+edge.label_color) if not edge.label_color is "" else None
            e.append('fontscale='+str(edge.label_size)) if not edge.label_size is None else None
            a = []
            a.append('length='+str(15*cm.conv(edge.arrow_size))+'cm') if not edge.arrow_size is "" else None
            a.append('width='+str(10*cm.conv(edge.arrow_width))+'cm') if not edge.arrow_width is "" else None
            e.append('style={-{Latex['+', '.join(a)+']}, '+edge.style+'}') if len(a) > 0 else None
            e.append('Direct') if directed else None
            e.append('RGB') if not edge.color is "" else None
            self.edges.append([edge_id[0],edge_id[1],e])

        latex_header = ['\\documentclass{standalone}\n',
                        '\\usepackage{tikz-network}\n',
                        '\\begin{document}\n',
                        '\\begin{tikzpicture}\n']
        if "3d" in kwds:
            latex_header.append('[multilayer=3d]\n')
        elif 'vertex_layer' in kwds:
            latex_header.append('[multilayer]\n')
        with open(filename, 'w') as out:
            out.write("".join(latex_header))
            for vertex_id, args in self.vertices:
                out.write("\\Vertex["+", ".join(args)+"]{"+vertex_id + "}\n")
            for v1, v2, args in self.edges:
                out.write("\\Edge["+", ".join(args)+"]("+v1+")("+v2+")\n")
            out.write("\\end{tikzpicture}\n\\end{document}")
        pass


# =============================================================================
# eof
#
# Local Variables: 
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End: 

 
