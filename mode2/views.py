from django.shortcuts import render
from django.views import View
from mode1.views import ManageNamedGraph
from mode2.models import NamedGraph
from django.db import connection
import _pickle
import base64
from modules.classes import UndirGraph

class Main(View):
    def get(self, request):
        named_graphs = NamedGraph.objects.all()
        return render(request, 'mode2/main.html', {"named_graphs": named_graphs})

class SetDefault(View):

    def get(self, request):
        graph1 = UndirGraph(6)
        graph1.add_edge(0, 1)
        graph1.add_edge(0, 2)
        graph1.add_edge(1, 2)
        graph1.add_edge(1, 3)
        graph1.add_edge(2, 3)
        graph1.add_edge(1, 4)
        graph1.add_edge(4, 3)
        graph1.add_edge(3, 5)
        graph1.add_edge(4, 5)
        graph1.add_edge(2, 5)
        pickled_graph1 = base64.b64encode(_pickle.dumps(graph1))

        graph2 = UndirGraph(6)
        graph2.add_edge(0, 1)
        graph2.add_edge(0, 2)
        graph2.add_edge(1, 0)
        graph2.add_edge(1, 2)
        graph2.add_edge(2, 3)
        graph2.add_edge(3, 4)
        graph2.add_edge(3, 5)
        graph2.add_edge(4, 5)
        pickled_graph2 = base64.b64encode(_pickle.dumps(graph2))

        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE mode2_namedgraph;")
        NamedGraph.objects.create(description="Envelope", pickled_graph=pickled_graph1)
        NamedGraph.objects.create(description="Bridge", pickled_graph=pickled_graph2)
        return render(request, 'project/success.html', {"message": "Loaded", "link": "/mode2/main"})

class ViewGraph(View, ManageNamedGraph):

    def dispatch(self, *args, **kwargs):
        ManageNamedGraph.__init__(self, 'mode2', 'NamedGraph')
        self.load_named_graph(int(kwargs["id"]))
        return View.dispatch(*args, **kwargs)

    def get(self, request, id):
        backurl = request.GET["backurl"]
        return render(request, 'mode2/view_graph.html', {"graph": self.graph, "id": id, "backurl": backurl})

############EDIT, ADD###############

class EditAddGraph(View, ManageNamedGraph):

    def dispatch(self, *args, **kwargs):
        if kwargs["mode"] == "0":
            ManageNamedGraph.__init__(self, 'mode2', 'NamedGraph')
            self.load_named_graph(int(kwargs["id"]))
        return View.dispatch(self, *args, **kwargs)

    def get(self, request, id, mode):
        if mode == "0":
            return render(request, 'mode2/edit_add_graph.html', {"id": id, "graph": self.graph,\
                                                                 "description": self.description,  "mode": 0, "empty_list": []})
        else: #"1"
            return render(request, 'mode2/edit_add_graph.html', {"mode": 1})

    def post(self, request, id, mode):
        try:
            size = int(request.POST["size"])
            self.description = request.POST["description"]
        except KeyError:
            return render(request, 'project/failure.html',
                          {"message": "Invalid input", "link": "/mode2/edit_add_graph/{}/0".format(id)})
        if mode == "0":
            self.graph.normalize(size)
            self.save_named_graph(id)
            return render(request, 'project/success.html',\
                          {"message": "Edited graph.", "link": "/mode2/edit_add_graph/{}/0".format(id)})
        else: #create
            self.graph = UndirGraph(size)
            named_graph = NamedGraph.objects.create(description=self.description, pickled_graph=base64.b64encode(_pickle.dumps(self.board)))
            id = named_graph.id
            return render(request, 'project/success.html',\
                          {"message": "Created graph.", "link": "/mode2/edit_add_graph/{}/0".format(id)})

class EditAddEdge(View, ManageNamedGraph):

    def dispatch(self, *args, **kwargs):
        ManageNamedGraph.__init__(self, 'mode2', 'NamedGraph')
        self.load_named_graph(int(kwargs["id"]))
        return View.dispatch(self, *args, **kwargs)

    def get(self, request, id, from_v, to_v, mode):
        if mode == "0":
            return render(request, 'mode2/edit_add_edge.html', {"from_v": int(from_v), "to_v": int(to_v), "mode": 0})
        else:
            return render(request, 'mode2/edit_add_edge.html', {"from_v": int(from_v), "to_v": int(to_v), "mode": 1})

    def post(self, request, id, from_v, to_v, mode):
        try:
            new_from_v = int(request.POST["new_from_v"])
            new_to_v = int(request.POST["new_to_v"])
        except KeyError:
            return render(request, 'project/failure.html', {"message": "Invalid input", "link": "/mode2/edit_add_graph/{}/0".format(id)})
        if mode == "0": #edit edge
            from_v = int(from_v)
            to_v = int(to_v)

            error_code = self.graph.add_edge(new_from_v, new_to_v)
            if error_code == -1:
                return render(request, 'project/failure.html', {"message": "Vertices are not in graph!", \
                                                                "link": "/mode2/edit_add_graph/{}/0".format(id)})
            elif error_code == -2:
                return render(request, 'project/failure.html', {"message": "No self-loops allowed!", \
                                                                "link": "/mode2/edit_add_graph/{}/0".format(id)})
            self.graph.del_edge(from_v, to_v)
            self.save_named_graph(id)
            return render(request, 'project/success.html',\
                          {"message": "Edited edge", "link": "/mode2/edit_add_graph/{}/0".format(id)})
        else: #add edge
            error_code = self.graph.add_edge(new_from_v, new_to_v)
            if error_code == -1:
                return render(request, 'project/failure.html', {"message": "Vertices are not in graph!", \
                                                                "link": "/mode2/edit_add_graph/{}/0".format(id)})
            elif error_code == -2:
                return render(request, 'project/failure.html', {"message": "No self-loops allowed!", \
                                                                "link": "/mode2/edit_add_graph/{}/0".format(id)})
            self.save_named_graph(id)
            return render(request, 'project/success.html', \
                          {"message": "Added edge", "link": "/mode2/edit_add_graph/{}/0".format(id)})



class DeleteEdge(View, ManageNamedGraph):
    def dispatch(self, *args, **kwargs):
        ManageNamedGraph.__init__(self, 'mode2', 'NamedGraph')
        self.load_named_graph(int(kwargs["id"]))
        return View.dispatch(self, *args, **kwargs)

    def get(self, request, id, from_v, to_v):
        self.graph.del_edge(int(from_v), int(to_v))
        self.save_named_graph(id)
        return render(request, 'project/success.html', \
                      {"message": "Deleted edge.", "link": "/mode2/edit_add_graph/{}/0".format(id)})

class DeleteVertex(View, ManageNamedGraph):

    def dispatch(self, *args, **kwargs):
        ManageNamedGraph.__init__(self, 'mode2', 'NamedGraph')
        self.load_named_graph(int(kwargs["id"]))
        return View.dispatch(self, *args, **kwargs)

    def get(self, request, id, v_id):
        self.graph.del_vertex(int(v_id))
        self.save_named_graph(id)
        return render(request, 'project/success.html',\
                          {"message": "Deleted vertex.", "link": "/mode2/edit_add_graph/{}/0".format(id)})

class AddVertex(View, ManageNamedGraph):
    def dispatch(self, *args, **kwargs):
        ManageNamedGraph.__init__(self, 'mode2', 'NamedGraph')
        self.load_named_graph(int(kwargs["id"]))
        return View.dispatch(self, *args, **kwargs)

    def get(self, request, id):
        self.graph.append_vertex()
        self.save_named_graph(id)
        return render(request, 'project/success.html',\
                          {"message": "Added vertex.", "link": "/mode2/edit_add_graph/{}/0".format(id)})

class DeleteGraph(View, ManageNamedGraph):
    def get(self, request, id):
        NamedGraph.objects.get(id=int(id)).delete()
        return render(request, 'project/success.html',
                    {"message": "Deleted graph", "link": "/mode2/main".format(id)})

class FindEulerPath(View, ManageNamedGraph):
    def dispatch(self, *args, **kwargs):
        ManageNamedGraph.__init__(self, 'mode2', 'NamedGraph')
        self.load_named_graph(int(kwargs["id"]))
        return View.dispatch(self, *args, **kwargs)

    def get(self, request, id):
        self.graph.find_euler_path()
        return render(request, 'project/success.html', \
                      {"message": "Found euler path.", "link": "/mode2/edit_add_graph/{}/0".format(id)})

