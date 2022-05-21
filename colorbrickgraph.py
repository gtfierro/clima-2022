from graphviz import Digraph
import graphviz
import sys
from urllib.parse import quote
import re
import brickschema
from rdflib import Namespace
from brickschema.namespaces import BRICK, RDFS, RDF
graphviz.set_jupyter_format('png')

BOT = Namespace("https://w3id.org/bot#")

classg = brickschema.Graph()
classg.load_file("ttl/Brick.ttl")
typenodes = {}

colors = {
    BRICK.Location: "#ea9999",
    BRICK.Point: "#f0d890",
    BRICK.Equipment: "#b6d7a8",
    BOT.Element: "#8F8CE7",
    BOT.Storey: "#FF964F",
}

G = Digraph("unified-model", engine='sfdp')
# G.attr(ranksep=".3")
# G.attr(fontsize="10")
# G.attr(dpi="100")
# G.attr(width="100pt", height="100pt")

def get_name(node, graph):
    if node.startswith('http://openmetrics.eu/openmetrics#'):
        _, name = str(node).split('#')
        return name
    # return re.split(r'[/#:]', node)[-1]
    return graph.namespace_manager.normalizeUri(node)


def get_type_color(node):
    for (klass, color) in colors.items():
        # print(klass, color, node)
        if classg.query(f"ASK {{ {node.n3()} rdfs:subClassOf* {klass.n3()} }}").askAnswer:
            return color
    return "white"


def draw_node(n, graph, G):
    name = get_name(n, graph)
    if n.startswith('http://openmetrics.eu/openmetrics#'):
        G.node(quote(n), label=name, penwidth="4", fixedsize="false")
        return quote(n)
    else:
        color = get_type_color(n)
        nodename = quote(n)
        while nodename in str(G):
            nodename += "1"
        G.node(nodename, label=name, fillcolor=color, color=color, style="filled", fixedsize="false")
        return nodename

def viz(g):
    # add all example nodes to graph
    for (s, p, o) in g:
        if p == RDFS.label:
            continue
        s = draw_node(s, g, G)
        o = draw_node(o, g, G)

        # print(s,p,o)
        p_name = get_name(p, g)
        if p_name == "rdf:type":
            G.edge(s, o, penwidth="2", arrowhead="diamond", style="dashed")
        else:
            G.edge(s, o, label=p_name, penwidth="2")
    # G.attr(size="400,400")
    # G.attr(fixedsize='true')
    # G.format = 'png'
    # G.render()
    return G