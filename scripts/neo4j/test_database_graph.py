from py2neo import Graph
from py2neo import Node
from py2neo import Relationship

def node_name_exists(name):
    return_value = -1
    has_nodes = graph.run(graph.run("MATCH (p:Person) RETURN p.name AS "+str(name)))
    if len(has_nodes) != 0:
        return_value = has_nodes[0]

    return return_value

def add_node_to_neo(name, id_item, group, color):
    if not graph.exists():
        a = Node("Item", name=name, id_item=id_item, group=group, color=color)
    tx.create(a)
    tx.commit()
    return 0

def add_link_to_neo(id_node_source, id_node_target, motivation, poids):
    link = Relationship(id_node_source, motivation, id_node_target)
    tx.create(link)
    tx.commit()
    return 0

graph = Graph(password="=y88AQ.u")

graph.run("MATCH (n) DETACH DELETE n")

tx = graph.begin()

a = Node("Person", name="Alice")
tx.create(a)
tx.commit()

tx = graph.begin()
b = Node("Person", name="Bob")
tx.create(b)
tx.commit()

tx = graph.begin()
ab = Relationship(a, "KNOWS", b)
tx.create(ab)
tx.commit()

node = graph.run("MATCH (p:Person) WHERE p.name = 'Alice' RETURN p.name AS name")

#ab = Relationship(Node("Person", name="Alice"), "KNOWS", Node("Person", name="Bob"))

print node[0]

bc = Relationship(node[0], "KNOWS", Node("Person", name="Albert"))

#node = graph.cypher.execute("MATCH (p:Person) WHERE p.name = 'Alice' RETURN p.name AS name")

tx.create(bc)
tx.commit()