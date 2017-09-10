from django.shortcuts import render
from mode1.views import ManageNamedGraph
from django.views import View
from mode4.models import NamedGraph
from django.db import connection
import _pickle
import base64
from modules.classes import CanvasFlowNetwork
from django.http import HttpResponse
import json

class Main(View):
    def get(self, request):
        named_graphs = NamedGraph.objects.all()
        return render(request, 'mode4/main.html', {"named_graphs": named_graphs})

class SetDefault(View):
    def get(self, request):
        graph1 = CanvasFlowNetwork(5, 500, 500)
        graph1.add_edge_w(0, 1, 500)
        graph1.add_edge_w(0, 2, 100)
        graph1.add_edge_w(0, 3, 100)
        graph1.add_edge_w(1, 4, 200)
        graph1.add_edge_w(2, 4, 200)
        graph1.add_edge_w(3, 4, 600)
        graph1.draw_default()
        print(list(graph1.__dict__))

        pickled_graph1 = base64.b64encode(_pickle.dumps(graph1))

        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE mode4_namedgraph;")
        NamedGraph.objects.create(description="Simple example", pickled_graph=pickled_graph1)
        return render(request, 'project/success.html', {"message": "Loaded", "link": "/mode4/main"})

class EditAddGraph(View):
    def dispatch(self, *args, **kwargs):
        if kwargs["mode"] == "0":
            self.mng = ManageNamedGraph('mode4', 'NamedGraph')
            self.mng.load_named_graph(int(kwargs["id"]))
            print(list(self.mng.graph.__dict__))
        return View.dispatch(self, *args, **kwargs)

    def get(self, request, id, mode):
        if mode == "0":
            return render(request, 'mode4/edit_add_graph.html', {"id": id, "graph": self.mng.graph, \
                                                                 "description": self.mng.description,  "mode": 0, "empty_list": []})
        else: #"1"
            return render(request, 'mode4/edit_add_graph.html', {"mode": 1})

    def post(self, request, id, mode):
        try:
            size = int(request.POST["size"])
            self.mng.description = request.POST["description"]
        except KeyError:
            return render(request, 'project/failure.html',
                          {"message": "Invalid input", "link": "/mode2/edit_add_graph/{}/0".format(id)})
        if mode == "0":
            self.mng.graph.normalize(size)
            self.mng.save_named_graph(id)
            return render(request, 'project/success.html',\
                          {"message": "Edited graph.", "link": "/mode2/edit_add_graph/{}/0".format(id)})
        else: #create
            self.mng.graph = UndirGraph(size)
            named_graph = NamedGraph.objects.create(description=self.mng.description, pickled_graph=base64.b64encode(_pickle.dumps(self.mng.graph)))
            id = named_graph.id
            return render(request, 'project/success.html',\
                          {"message": "Created graph.", "link": "/mode2/edit_add_graph/{}/0".format(id)})

class EditAddEdge(View):

    def dispatch(self, *args, **kwargs):
        self.mng = ManageNamedGraph('mode4', 'NamedGraph')
        self.mng.load_named_graph(int(kwargs["id"]))
        return View.dispatch(self, *args, **kwargs)

    def get(self, request, id, from_v, to_v, mode):
        from_v = int(from_v)
        to_v = int(to_v)
        if mode == "0":
            capacity = self.mng.graph.weights[(from_v, to_v)]
            return render(request, 'mode4/edit_add_edge.html', {"from_v": from_v, "to_v": to_v, "capacity": capacity, "mode": 0})
        else:
            return render(request, 'mode4/edit_add_edge.html', {"from_v": from_v, "to_v": to_v, "mode": 1})

    def post(self, request, id, from_v, to_v, mode):
        try:
            new_from_v = int(request.POST["new_from_v"])
            new_to_v = int(request.POST["new_to_v"])
            new_capacity = int(request.POST["new_capacity"])
        except KeyError:
            return render(request, 'project/failure.html', {"message": "Invalid input", "link": "/mode4/edit_add_graph/{}/0".format(id)})
        if mode == "0": #edit edge
            from_v = int(from_v)
            to_v = int(to_v)

            capacity = self.mng.graph.weights[(from_v, to_v)]
            error_code = self.mng.graph.add_edge_w(new_from_v, new_to_v, new_capacity)


            if error_code == -1:
                return render(request, 'project/failure.html', {"message": "Vertices are not in graph!", \
                                                                "link": "/mode4/edit_add_graph/{}/0".format(id)})
            elif error_code == -3:
                return render(request, 'project/failure.html', {"message": "No self-loops allowed!", \
                                                                "link": "/mode4/edit_add_graph/{}/0".format(id)})
            elif error_code == -2: #duplicate
                print(capacity, new_capacity)
                if from_v == new_from_v and to_v == new_to_v and capacity == new_capacity:
                    return render(request, 'project/success.html', \
                           {"message": "Nothing changed", "link": "/mode4/edit_add_graph/{}/0".format(id)})

            if error_code != -2:
                self.mng.graph.del_edge(from_v, to_v)
            self.mng.save_named_graph(id)
            return render(request, 'project/success.html',\
                          {"message": "Edited edge", "link": "/mode4/edit_add_graph/{}/0".format(id)})
        else: #add edge
            error_code = self.mng.graph.add_edge_w(new_from_v, new_to_v, new_capacity)
            if error_code == -1:
                return render(request, 'project/failure.html', {"message": "Vertices are not in graph!", \
                                                                "link": "/mode4/edit_add_graph/{}/0".format(id)})
            elif error_code == -3:
                return render(request, 'project/failure.html', {"message": "No self-loops allowed!", \
                                                                "link": "/mode4/edit_add_graph/{}/0".format(id)})
            elif error_code == -2:
                return render(request, 'project/failure.html', {"message": "No duplicates allowed!", \
                                                                "link": "/mode4/edit_add_graph/{}/0".format(id)})
            self.mng.save_named_graph(id)
            return render(request, 'project/success.html', \
                          {"message": "Added edge", "link": "/mode4/edit_add_graph/{}/0".format(id)})


class DeleteEdge(View):
    def dispatch(self, *args, **kwargs):
        self.mng = ManageNamedGraph('mode4', 'NamedGraph')
        self.mng.load_named_graph(int(kwargs["id"]))
        return View.dispatch(self, *args, **kwargs)

    def get(self, request, id, from_v, to_v):
        self.mng.graph.del_edge(int(from_v), int(to_v))
        self.mng.save_named_graph(id)
        return render(request, 'project/success.html', \
                      {"message": "Deleted edge.", "link": "/mode4/edit_add_graph/{}/0".format(id)})


class DeleteVertex(View):
    def dispatch(self, *args, **kwargs):
        self.mng = ManageNamedGraph('mode4', 'NamedGraph')
        self.mng.load_named_graph(int(kwargs["id"]))
        return View.dispatch(self, *args, **kwargs)

    def get(self, request, id, v_id):
        self.mng.graph.del_vertex(int(v_id))
        self.mng.save_named_graph(id)
        return render(request, 'project/success.html', \
                      {"message": "Deleted vertex.", "link": "/mode4/edit_add_graph/{}/0".format(id)})

class AddVertex(View):
    def dispatch(self, *args, **kwargs):
        self.mng = ManageNamedGraph('mode4', 'NamedGraph')
        self.mng.load_named_graph(int(kwargs["id"]))
        return View.dispatch(self, *args, **kwargs)

    def get(self, request, id):
        self.mng.graph.append_vertex()
        self.mng.save_named_graph(id)
        return render(request, 'project/success.html',\
                          {"message": "Added vertex.", "link": "/mode4/edit_add_graph/{}/0".format(id)})

class DeleteGraph(View):
    def get(self, request, id):
        NamedGraph.objects.get(id=int(id)).delete()
        return render(request, 'project/success.html',
                    {"message": "Deleted graph", "link": "/mode4/main".format(id)})


class FindMaximumFlow(View):

    def dispatch(self, *args, **kwargs):
        self.mng = ManageNamedGraph('mode4', 'NamedGraph')
        self.mng.load_named_graph(int(kwargs["id"]))
        return View.dispatch(self, *args, **kwargs)


    def post(self, request, id):
        try:
            vertex_from = int(request.POST["vertex_from"])
            vertex_to = int(request.POST["vertex_to"])
        except ValueError:
            return HttpResponse(json.dumps({'error': 1, 'message': 'Invalid input'}), content_type="application/json")

        return_code = self.mng.graph.find_maximum_flow(vertex_from, vertex_to)
        if return_code == -2:
            return HttpResponse(json.dumps({'error': 1, 'message': 'Vertices are not in graph!'}), content_type="application/json")

        elif return_code == -1:
            return HttpResponse(json.dumps({'error': 1, 'message': 'Graph cannot be cyclic'}),
                                content_type="application/json")
        else:
            self.mng.graph.produce_flow_lines()
            return HttpResponse(json.dumps({'error': 0, 'flow_lines': self.mng.graph.flow_lines}), content_type="application/json")


