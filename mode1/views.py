from django.shortcuts import render
from django.views import View
from mode1.models import NamedGraph
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import _pickle
import base64
from modules.classes import CanvasBoard, ManageNamedGraph





class ProjectMain(View):
    def get(self, request):
        return render(request, 'project/main.html')

class Main(View):
    def get(self, request):
        named_boards = NamedGraph.objects.all()
        return render(request, 'mode1/main.html', {"named_boards": named_boards})


class SetDefault(View):
    def get(self, request):

        board = CanvasBoard(100, 500, 500)

        board.add_transfer(1, 38)
        board.add_transfer(4, 14)
        board.add_transfer(9, 31)
        board.add_transfer(16, 6)
        board.add_transfer(21, 42)
        board.add_transfer(28, 84)
        board.add_transfer(36, 44)
        board.add_transfer(47, 26)
        board.add_transfer(49, 11)
        board.add_transfer(51, 67)
        board.add_transfer(56, 53)
        board.add_transfer(62, 19)
        board.add_transfer(64, 60)
        board.add_transfer(71, 91)
        board.add_transfer(80, 100)
        board.add_transfer(87, 24)
        board.add_transfer(93, 73)
        board.add_transfer(95, 75)
        board.add_transfer(98, 78)

        board.board_to_rectangles()
        board.draw_transfers()


        pickled_graph = base64.b64encode(_pickle.dumps(board))
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE mode1_namedgraph;")
        NamedGraph.objects.create(description="Default board", pickled_graph=pickled_graph)

        return render(request, 'project/success.html', {"message": "Loaded", "link": "/mode1/main"})

class ViewBoard(View, ManageNamedGraph):
    def dispatch(self, *args, **kwargs):
        ManageNamedGraph.__init__(self, 'mode1', 'NamedGraph')
        self.load_named_graph(int(kwargs["id"]))
        return View.dispatch(self, *args, **kwargs)

    def get(self, request, id):
        backurl = request.GET["backurl"]
        return render(request, 'mode1/view_board.html', {"board": self.graph, "id": id, "backurl": backurl})
############EDIT, ADD###############

class EditAddBoard(View, ManageNamedGraph):

    def dispatch(self, *args, **kwargs):
        if kwargs["mode"] == "0":
            ManageNamedGraph.__init__(self, 'mode1', 'NamedGraph')
            self.load_named_graph(int(kwargs["id"]))
        return View.dispatch(self, *args, **kwargs)

    def get(self, request, id, mode):
        if mode == "0":
            return render(request, 'mode1/edit_add_board.html', {"id": id, "board": self.graph,\
                                                                 "description": self.description,  "mode": 0})
        else: #"1"
            return render(request, 'mode1/edit_add_board.html', {"mode": 1})

    def post(self, request, id, mode):
        try:
            size = int(request.POST["size"])
            self.description = request.POST["description"]
        except KeyError:
            return render(request, 'project/failure.html',
                          {"message": "Invalid input", "link": "/mode1/edit_add_board/{}/0".format(id)})
        if mode == "0":
            self.graph.normalize(size)
            self.save_named_graph(id)
            return render(request, 'project/success.html',\
                          {"message": "Edited board.", "link": "/mode1/edit_add_board/{}/0".format(id)})
        else: #create
            self.graph = CanvasBoard(size)
            named_graph = NamedGraph.objects.create(description=self.description, pickled_graph=base64.b64encode(_pickle.dumps(self.board)))
            id = named_graph.id
            return render(request, 'project/success.html',\
                          {"message": "Created board.", "link": "/mode1/main".format(id)})



class EditAddTransfer(View, ManageNamedGraph):

    def dispatch(self, *args, **kwargs):
        ManageNamedGraph.__init__(self, 'mode1', 'NamedGraph')
        self.load_named_graph(int(kwargs["id"]))
        return View.dispatch(self, *args, **kwargs)

    def get(self, request, id, t_id, mode):
        if mode == "0":
            return render(request, 'mode1/edit_add_transfer.html', {"board": self.graph.graph, "transfers": self.graph.transfers, "t_id": int(t_id), "id": id, "mode": 0})
        else:
            return render(request, 'mode1/edit_add_transfer.html', {"id": id, "mode": 1})

    def post(self, request, id, t_id, mode):
        try:
            new_from = int(request.POST["new_from"])
            new_to = int(request.POST["new_to"])
        except KeyError:
            return render(request, 'project/failure.html', {"message": "Invalid input", "link": "/mode1/edit_add_board/{}/0".format(id)})
        if mode == "0": #edit transfer
            prev_from = self.graph.transfers[int(t_id)]
            prev_to = self.graph.graph[prev_from][0]
            error_code = self.graph.modify_transfer(prev_from, prev_to, new_from, new_to)
            if error_code == -1:
                return render(request, 'project/failure.html', {"message":\
                        "Vertices are not in graph!", "link": "/mode1/edit_add_board/{}/0".format(id)})
            elif error_code == -2:
                return render(request, 'project/failure.html', {"message": \
                        "Cannot edit transfer, it produces cycle!", "link": "/mode1/edit_add_board/{}/0".format(id)})

            self.save_named_graph(id)
            return render(request, 'project/success.html',\
                          {"message": "Edited transfer", "link": "/mode1/edit_add_board/{}/0".format(id)})
        else: #add transfer
            error_code = self.graph.add_transfer(new_from, new_to)
            if error_code == -1:
                return render(request, 'project/failure.html', {"message":\
                        "Vertices are not in graph!", "link": "/mode1/edit_add_board/{}/0".format(id)})
            elif error_code == -2:
                return render(request, 'project/failure.html', {"message": \
                        "Cannot add transfer, it produces cycle!", "link": "/mode1/edit_add_board/{}/0".format(id)})
            self.save_named_graph(id)
            return render(request, 'project/success.html', \
                          {"message": "Added transfer", "link": "/mode1/edit_add_board/{}/0".format(id)})


############DELETE################

class DeleteTransfer(View, ManageNamedGraph):

    def dispatch(self, *args, **kwargs):
        ManageNamedGraph.__init__(self, 'mode1', 'NamedGraph')
        self.load_named_graph(int(kwargs["id"]))
        return View.dispatch(self, *args, **kwargs)

    def get(self, request, id, t_id):
        vertex_from = self.graph.transfers[int(t_id)]
        vertex_to = self.graph.graph[vertex_from][0]
        self.graph.del_edge(vertex_from, vertex_to)
        self.save_named_graph(id)
        return render(request, 'project/success.html', {"message": "Deleted transfer.", "link": "/mode1/edit_add_board/{}/0".format(id)})

class DeleteBoard(View):

    def get(self, request, id):
        NamedGraph.objects.get(id=int(id)).delete()
        return render(request, 'project/success.html', {"message": "Deleted board", "link": "/mode1/main".format(id)})


#########SHORTEST GAME###############

class FindShortestGame(View, ManageNamedGraph):

    def dispatch(self, *args, **kwargs):
        ManageNamedGraph.__init__(self, 'mode1', 'NamedGraph')
        self.load_named_graph(int(kwargs["id"]))
        return View.dispatch(self, *args, **kwargs)

    def get(self, request, id):
        return render(request, 'mode1/find_shortest_game.html', {'id': id})

    def post(self, request, id):
        try:
            vertex_from = int(request.POST["vertex_from"])
            vertex_to = int(request.POST["vertex_to"])
        except KeyError:
            return render(request, 'project/failure.html', {"message": "Invalid input", "link": "/mode1/edit_add_board/{}/0".format(id)})
        path = self.graph.find_shortest_game(vertex_from, vertex_to)
        if path == -1:
            return render(request, 'project/failure.html',
                          {"message": "Vertices are not in graph!", "link": "/mode1/edit_add_board/{}/0".format(id)})
        message = []
        current_vertex = vertex_from
        moves = 0
        if path == []:
            message.append("You're already at the destination!")
        elif path == [-1]:
            message.append("Destination cannot be reached")
        else:
            for index in path:
                if index == -1: #transfer
                    destination = self.graph.graph[current_vertex][0]
                    if destination > current_vertex: #ladder
                        message.append("Ladder from {} to {}".format(current_vertex, destination))
                    else: #snake
                        message.append("Snake from {} to {}".format(current_vertex, destination))
                else: #dice roll
                    moves += 1
                    destination = self.graph.graph[current_vertex][index]
                    message.append("Roll nr {}. Dice is {}. Go from {} to {} \n".format(moves, index+1, current_vertex, destination))
                current_vertex = destination
            message.append("Destination reached! This is the shortest game (by number of rolls).")
        return render (request, 'mode1/view_shortest_game.html'.format(id), {"message": message, "id":id})


