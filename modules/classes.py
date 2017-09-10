import queue
import _pickle
import base64
from django.apps import apps
from random import randint
import math
import copy



CANVAS_WIDTH = 500
CANVAS_HEIGHT = 500

class Found(Exception):
    pass

###################Class ManageNamedGraph#######################

class ManageNamedGraph(): # Named Graph  = Graph + Description

    def __init__(self, app_name, model_name):
        self.graph = None
        self.description = ""
        self.app_name = app_name
        self.model_name = model_name

    def load_named_graph(self, id):
        named_graph = apps.get_model(self.app_name, self.model_name).objects.get(id=id)
        self.graph = _pickle.loads(base64.b64decode(named_graph.pickled_graph))
        self.graph.__init__
        self.description = named_graph.description

    def save_named_graph(self, id): # load_board must be called first
        named_graph = apps.get_model(self.app_name, self.model_name).objects.get(id=id)
        named_graph.pickled_graph = base64.b64encode(_pickle.dumps(self.graph))
        named_graph.description = self.description
        named_graph.save()

###################Class DirGraph#######################
class DirGraph(): #starting with 1
    """ Representation of directed graph by dictionary of adjancency lists.
        Graph of size n (=self.last+1) holds n vertices labeled from 1 to n (as ints)
        Each list is sorted
    """
    def __init__(self, size=0):
        self.graph = {}  #edges
        self.size = 0
        self.parent = {} # parents of vertices on path from start_v to end_v (bfs)

        for i in range(0, size):
            self.append_vertex()

    def append_vertex(self):
        self.graph[self.size] = []
        self.size += 1

    def check_vertex(self, *args):
        for vertex in args:
            single_result = 0 <= vertex < self.size and type(vertex) is int
            if not single_result:
                return False
        return True

    def check_edge(self, vertex_from, vertex_to):
        if not self.check_vertex(vertex_from, vertex_to):
            return False
        if vertex_to in self.graph[vertex_from]:
            return True
        else:
            return False


    def add_edge(self, vertex_from, vertex_to):
        if not(self.check_vertex(vertex_from, vertex_to)):
            return -1 #Invalid vertices
        if vertex_to not in self.graph[vertex_from]: #avoid duplicates
            if vertex_to != vertex_from:
                self.graph[vertex_from].append(vertex_to)
                return 0 #successful
            else:
                return -3 #self-loop
        else:
            return -2 #duplicate

    def del_edge(self, vertex_from, vertex_to):
        if not(self.check_vertex(vertex_from, vertex_to)):
            return -1 #Invalid vertices
        if vertex_to in self.graph[vertex_from]:
            self.graph[vertex_from].remove(vertex_to)
            return 0 #successful
        else:
            return -2 #no edge

    def relabel(self, deleted_vertex):
        for in_vertex in range(0, self.size-1):
            if in_vertex >= deleted_vertex: #relabel all vertices >= del_vertex, refer to next vertex
                self.graph[in_vertex] = self.graph[in_vertex+1]

        for in_vertex in range(0, self.size-1):
            for out_vertex in self.graph[in_vertex]:
                if out_vertex > deleted_vertex:
                 #relabel all edges leading after del_vertex
                    self.graph[in_vertex].remove(out_vertex) #(every vertex>del_vertex decreases by 1)
                    self.graph[in_vertex].append(out_vertex-1)
                    self.graph[in_vertex].sort()

        del self.graph[self.size-1]


    def del_vertex(self, vertex):
        if not(self.check_vertex(vertex)):
            return -1
        self.cut_vertex(vertex)
        self.relabel(vertex)
        self.size -=1 # we removed 1 vertex

    def cut_vertex(self, vertex):
        if not(self.check_vertex(vertex)):
            return -1
        for ingoing in self.graph: #delete ingoing edges
            if ingoing == vertex:
                continue
            if vertex in self.graph[ingoing]:
                self.del_edge(ingoing, vertex)
        self.graph[vertex] = [] #delete outgoing edges

    def cut_vertex_outgoing(self, vertex): #
        if not(self.check_vertex(vertex)):
            return -1
        self.graph[vertex] = [] #delete outgoing edges

    def normalize(self, size): #adapts to new size
        for in_vertex in self.graph:
            if in_vertex <= size:
                self.graph[in_vertex] = [out_vertex for out_vertex in self.graph[in_vertex] if out_vertex <= size]
            else:
                self.del_vertex(in_vertex)
        for i in range(self.size+1, size+1):
            self.append_vertex()
        self.size = size

    def degree(self, vertex):
        if not(self.check_vertex(vertex)):
            return -1
        return len(self.graph[vertex])

    def is_cyclic(self):
        #Performing DFS and checking if there are back edges, if yes graph is cyclic otherwise it is not
        if self.size == 0:
            return -1 #empty
        stack = [0]
        discovered = []
        while stack != []:
            in_vertex = stack.pop()
            if in_vertex not in discovered:
                discovered.append(in_vertex)
                for out_vertex in self.graph[in_vertex]:
                    if out_vertex in stack:
                        return True #back edge
                    if out_vertex not in discovered:
                        stack.append(out_vertex)
                        print(stack)
        return False

    def is_connected(self):
        # Performing DFS to check if graph is connected
        if self.size == 0:
            return -1
        stack = [0]
        discovered = []
        while stack != []:
            in_vertex = stack.pop()
            if in_vertex not in discovered:
                discovered.append(in_vertex)
                for out_vertex in self.graph[in_vertex]:
                    if out_vertex not in discovered:
                        stack.append(out_vertex)
        return set(discovered) == set(self.graph.keys())

    def bfs (self, vertex_from, vertex_to, graph):
        if not self.check_vertex(vertex_from, vertex_to):
            return -1 #invalid input
        visited = [False] * self.size
        self.parent = {}
        processing = queue.Queue()
        processing.put(vertex_from)
        visited[vertex_from] = True

        while not processing.empty():
            current = processing.get()
            for out_vertex in graph[current]:
                if not visited[out_vertex]:
                    visited[out_vertex] = True
                    processing.put(out_vertex)
                    self.parent[out_vertex] = current

        return visited[vertex_to]




###################Class MultiDirGraph#######################
class MultiDirGraph(DirGraph):
    #Multigraph, edges can be duplicated

    def add_edge(self, vertex_from, vertex_to):
        if not(self.check_vertex(vertex_from, vertex_to)):
            return -1 #Invalid vertices
        self.graph[vertex_from].append(vertex_to) #accept duplicates

###################Class UndirGraph#######################
class UndirGraph(DirGraph):
    # edges are bidirectional
    def add_edge(self, vertex1, vertex2):
        if not(self.check_vertex(vertex1, vertex2)):
            return -1
        if vertex1 == vertex2: #no loops allowed!
            return -2
        if vertex1 not in self.graph[vertex2] and vertex2 not in self.graph[vertex1]:
            self.graph[vertex1].append(vertex2)
            self.graph[vertex1].sort()
            self.graph[vertex2].append(vertex1)
            self.graph[vertex2].sort()
            return 0
        else:
            return -3

    def del_edge(self, vertex1, vertex2):
        if not(self.check_vertex(vertex1, vertex2)):
            return -1
        if vertex2 in self.graph[vertex1]:
            self.graph[vertex1].remove(vertex2)
        if vertex1 in self.graph[vertex2]:
            self.graph[vertex2].remove(vertex1)

    def find_bridges(self):
        if self.size == 0:
            return -1 #Empty graph
        stack = [(0, -1, 0)]
        # (v, p, i): v - current vertex, p - current parent, i - index of adjacency
        min_up = {}
        #min_up[vertex] is a minimum entry_time reachable from DFS subtree rooted at vertex,
        #  no parent-son edges!
        entry_time = {}
        bridges = {}
        discovered = []
        time = 0

        for i in range(0, self.size):
            bridges[i] = []

        while stack != []:
            current = stack.pop()
            from_v = current[0]
            parent = current[1]
            adj_index = current[2]
            size = len(self.graph[from_v])

            if adj_index > 0:
                to_v = self.graph[from_v][adj_index-1]
                #computation of min_up[to_v] is finished
                if to_v != parent: # no parent-son edges!
                    min_up[from_v] = min(min_up[from_v], min_up[to_v])
                #update min_up[from_v]
                if min_up[to_v] > entry_time[from_v]:
                    #cannot reach lower value from to_v than entry_time[from_v]: we found a bridge
                    bridges[from_v].append(to_v) #bidirectional edge
                    bridges[to_v].append(from_v)
            elif adj_index == 0:
                discovered.append(from_v)
                min_up[from_v] = entry_time[from_v] = time
                time += 1

            if adj_index == size:
                continue #it handles: adj_index is out of range, vertex is disconnected
            to_v = self.graph[from_v][adj_index]
            stack.append((from_v, parent, adj_index + 1))

            if to_v == parent:
                continue
            if to_v in discovered:
                min_up[from_v] = min(min_up[from_v], entry_time[to_v])
                #no parent-son edges!
            else:
                stack.append((to_v, from_v, 0)) #prioritize depth
        return bridges


    def number_single_edges(self):
        result = 0
        for in_vertex in self.graph:
            for out_vertex in self.graph[in_vertex]:
                result += 1
        return result // 2 #handshake lemma



    def find_euler_path(self):
        # Fleury's Algorithm
        if self.size == 0:
            return -1 #Empty graph
        if not self.is_connected():
            return -2 #Not connected
        odd_degrees = [vertex for vertex in self.graph.keys() if self.degree(vertex) % 2 == 1 ]
        if len(odd_degrees) not in [0, 2]:
            return -3 #No euler path
        else:
            if len(odd_degrees) == 0: #all degrees even
                from_v = randint(0, self.size - 1)
            else: #choose random odd degree vertex as a start
                from_v = odd_degrees[randint(0, 1)]
            bridges = self.find_bridges()
            graph = copy.deepcopy(self)
            number_single_edges = self.number_single_edges()
            path = [from_v]
            while number_single_edges > 0:
                only_bridges = True
                for out_vertex in graph.graph[from_v]:
                    if out_vertex not in bridges[from_v]: # go this way
                        to_v = out_vertex
                        only_bridges = False
                        break
                if only_bridges:
                    to_v = bridges[from_v][0] #choose first bridge
                path.append(to_v) #we moved 1 edge
                graph.del_edge(from_v, to_v) #delete from copy of graph
                number_single_edges -= 1
                from_v = to_v #to next iteration
        self.euler_path = path

###################Class Grid#######################

class Grid():
    def __init__(self, width, height):
        self.width = width
        self.height = height


    def coords_to_vertex(self, x, y): #we start at (0,0)
        if 0 <= x < self.width and 0 <= y < self.height:
            return x + y * self.width
        else:
            return -1

    def vertex_to_coords(self, vertex):
        x = vertex % self.width
        y = (vertex - x) // self.width
        return (x, y)

###################Class CanvasGrid#######################
class CanvasGrid(Grid):
    def __init__(self, width, height, canvas_width, canvas_height):
        Grid.__init__(self, width, height)
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.cell_width = self.canvas_width // self.width
        self.cell_height = self.canvas_height // self.height

###################Class CanvasUndirGraph#######################

class CanvasUndirGraph(UndirGraph):

    def __init__(self, size, canvas_width, canvas_height):
        UndirGraph.__init__(self, size)
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.x_center = self.canvas_width // 2
        self.y_center = self.canvas_height // 2
        self.circles = []
        self.lines = []
        self.radius_large = 0
        self.radius_small = 0
        self.get_radius_small_large()




    def vertex_to_pixels(self, vertex):
        angle = (2*math.pi / self.size) * vertex
        x = int(self.x_center + math.cos(angle)*self.radius_large)
        y = int(self.y_center - math.sin(angle)*self.radius_large) #y-axis is inverted
        return x, y

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


    def get_radius_small_large(self):
        self.radius_large = min(self.canvas_width, self.canvas_height) // 2
        x1, y1 = self.vertex_to_pixels(0)
        x2, y2 = self.vertex_to_pixels(1)
        self.radius_small = self.distance(x1, y1, x2, y2) // 4
        self.radius_large -= self.radius_small
        x1, y1 = self.vertex_to_pixels(0)
        x2, y2 = self.vertex_to_pixels(1)
        self.radius_small = self.distance(x1, y1, x2, y2) // 4


    def draw_default(self):
        self.find_euler_path()
        if self.size < 2:
            return -1 #size needs to be >=2
        self.drawn = {}
        for in_vertex in self.graph:
            x_in, y_in = self.vertex_to_pixels(in_vertex)
            self.circles.append([x_in, y_in, self.radius_small, 1])
            for out_vertex in self.graph[in_vertex]:
                if (in_vertex, out_vertex) not in self.drawn:
                    x_out, y_out = self.vertex_to_pixels(out_vertex)
                    self.lines.append([x_in, y_in, x_out, y_out, in_vertex, out_vertex, 1])
                    self.drawn[(out_vertex, in_vertex)] = True #value not used
                    #don't need to append(in_vertex, out_vertex), each in_vertex is visited once

        #lines: [x_in y_in x_out y_out in_v, out_v, visible]
        #vertices: [x_in, y_in, radius, visible]





###################Class Board#######################

class Board(MultiDirGraph):

    def __init__(self, size, dice_sides=6):
        super(Board, self).__init__()
        # dice_sides > 1
        # minimum number of size is ceil(dice_size/2)
        # when we roll and got out of size, we "bounce back"
        # from last vertex. For example: on 98, rolled 6, we move:
        # 99(1) -> 100(2) -> 99(3) -> 98(4) -> 97(5) -> 96(6)
        # we move to 96
        self.dice_sides = dice_sides
        self.transfers = []
        self.transfers_graph = DirGraph(size)
        for i in range(0, size + 1): #from 0 to self.size
            self.append_vertex()
        for i in range(0, size):  # last vertex has no edge
            self.default_link_vertex(i)

    def default_link_vertex(self, vertex):
        if not(self.check_vertex(vertex)):
            return -1 #Invalid vertex

        self.graph[vertex] = [] #firstly it clears list of graph[i]
        n = self.size - vertex - 1

        # min(dice_sides,n) is maximum possible dice number that
        # we can go forward
        delta = 0
        for moves in range(1, self.dice_sides+1):
            if 1 <= moves <= min(self.dice_sides, n): #forward
                delta += 1
            else: #backward
                delta -= 1
            self.add_edge(vertex, vertex + delta)

    def add_transfer(self, vertex_from, vertex_to):
    #both for snakes and ladders
        if not(self.check_vertex(vertex_from, vertex_to)):
            return -1
        new_transfers_graph = self.transfers_graph
        #new_graph.cut_vertex(vertex_from) #ladder or snake: only 1 edge
        new_transfers_graph.add_edge(vertex_from, vertex_to)
        if new_transfers_graph.is_cyclic(): #new_graph is not empty
            return -2 #Cannot add transfer
        self.transfers_graph.add_edge(vertex_from, vertex_to)
        self.cut_vertex_outgoing(vertex_from) #ingoing edges need to stay
        self.add_edge(vertex_from, vertex_to)

        if vertex_from not in self.transfers:
            self.transfers.append(vertex_from)
            self.transfers.sort()

    def del_edge(self, vertex_from, vertex_to): #edges including transfers
        super(Board, self).del_edge(vertex_from, vertex_to)
        if vertex_from in self.transfers: #delete from transfers
            self.transfers.remove(vertex_from) # now nothing is linked to vertex_from, call default_link

    def modify_transfer(self, prev_from, prev_to, new_from, new_to):
        if not (self.check_vertex(new_from, new_to)):
            return -1
        new_transfers_graph = copy.deepcopy(self.transfers_graph)
        new_transfers_graph.del_edge(prev_from, prev_to)
        new_transfers_graph.add_edge(new_from, new_to)
        if new_transfers_graph.is_cyclic(): #new_graph is not empty
            return -2 #Cannot modify_transfer it produces a cycle!
        self.default_link_vertex(prev_from) #No cycle, we update the graph
        self.transfers.remove(prev_from)
        self.add_transfer(new_from, new_to)

    def normalize(self, size): #adapts to new size
        transfer_pairs = [(in_vertex, self.graph[in_vertex][0]) for in_vertex in self.transfers if in_vertex <= size and self.graph[in_vertex][0] <= size]
        self.__init__(size)
        for t in transfer_pairs:
            self.add_transfer(t[0], t[1])
        self.size = size #update size

    def find_shortest_game(self, vertex_from, vertex_to):
        #using BFS to find game in least possible dice rolls, from vertex_from to vertex_to

        if not self.check_vertex(vertex_from, vertex_to):
            return -1 #invalid input
        visited = [vertex_from] #list of visited vertices
        processing = queue.Queue() #vertices of given distance from source (vertex_from)
        processing.put(vertex_from)
        possible_games = queue.Queue()
        previous_game = []

        while not processing.empty():
            current = processing.get()
            if current == vertex_to:
                if possible_games.empty():
                    return [] #we are already there, no dice rolls needed
                else:
                    return possible_games.get()

            else:
                if not possible_games.empty():
                    previous_game = possible_games.get()
                for out_vertex in self.graph[current]:
                    if out_vertex not in visited:
                        visited.append(out_vertex)
                        processing.put(out_vertex)
                        if len(self.graph[current]) == 1: #transfer
                            new_game = previous_game+[-1]
                        else: #dice roll
                            new_game = previous_game+[self.graph[current].index(out_vertex)]
                        possible_games.put(new_game)
        return [-2] #we cannot reach vertex_to











###################Class CanvasBoard#######################
class CanvasBoard(Board, CanvasGrid):
    def __init__(self, size, canvas_width, canvas_height):
        Board.__init__(self, size)
        sqrt = int(math.sqrt(size))
        if sqrt**2 == size:
            width = sqrt
            height = sqrt
        else:
            width = sqrt+1
            height = sqrt
        CanvasGrid.__init__(self, width, height, canvas_width, canvas_height)  # values not used
        self.rectangles = []
        self.lines = []
        self.circle_radius = min(self.cell_width, self.cell_height) // 2
        self.circle_border = min(self.cell_width, self.cell_height) // 7
        self.circle_color = 'yellow'


    def vertex_to_coords(self, vertex):
        x, y = Grid.vertex_to_coords(self, vertex-1)
        if y % 2 == 1:
            x = self.width - 1 - x #reverse next line
        return x, y

    def board_to_rectangles(self):
        for vertex in self.graph:
            if vertex == 0:
                continue
            x, y = self.vertex_to_coords(vertex)
            if vertex % 2 == 0:
                color = 'lightgray'
                font_color = 'black'
            else:
                color = 'black'
                font_color = 'lightgray'
            start_x = x*self.cell_width
            start_y = self.canvas_height - (y+1)*self.cell_height
            center_x = start_x + self.cell_width // 2
            center_y = start_y + self.cell_height // 2
            font_size = min(self.cell_width, self.cell_height) // 2

            self.rectangles.append([start_x, start_y,\
                                    self.cell_width, self.cell_height, color, center_x, center_y, font_size, font_color])
            # 0,1 - start x, y ; 2,3 - width, height; 4-color; 5,6- center_x, center_y, 7-font size, 8-font-color

    def coords_to_pixels(self, x, y): #returns upper left corner
        return (x * self.cell_width, self.canvas_height - (y+1) * self.cell_height)


    def draw_transfers(self):
        for in_vertex in self.transfers:
            color = "black"
            if self.graph[in_vertex][0] < in_vertex: #snake
                color = "red"
            elif self.graph[in_vertex][0] > in_vertex :#ladder
                color = "green"
            x1, y1 = self.vertex_to_coords(in_vertex)
            x1_pixels, y1_pixels = self.coords_to_pixels(x1, y1)
            x1_pixels += self.cell_width // 2
            y1_pixels += self.cell_height // 2
            x2, y2 = self.vertex_to_coords(self.graph[in_vertex][0])
            x2_pixels, y2_pixels = self.coords_to_pixels(x2, y2)
            x2_pixels += self.cell_width // 2
            y2_pixels += self.cell_height // 2
            line_width = min(self.cell_width, self.cell_height) // 10
            self.lines.append([x1_pixels, y1_pixels, x2_pixels, y2_pixels, color, line_width])
            dy = y1_pixels - y2_pixels
            dx = x1_pixels - x2_pixels
            alpha = math.atan2(dy, dx) #angle between line and x-axis (at ending vertex)
            beta = alpha + 0.523 #30 deg
            gamma = alpha - 0.523
            arrow_length = min(self.cell_width, self.cell_height) // 3
            beta_dx = arrow_length * math.cos(beta)
            beta_dy = arrow_length * math.sin(beta)
            gamma_dx = arrow_length * math.cos(gamma)
            gamma_dy = arrow_length * math.sin(gamma)
            beta_line = [x2_pixels, y2_pixels, x2_pixels + beta_dx, y2_pixels + beta_dy, color, line_width]
            gamma_line = [x2_pixels, y2_pixels, x2_pixels + gamma_dx, y2_pixels + gamma_dy, color, line_width]
            self.lines.append(beta_line)
            self.lines.append(gamma_line)

    def put_s_g_moves_pixels(self, vertex):
        if vertex==0:
            self.s_g_moves_pixels.append([-1]) #not used, because 0 is out of board
        else:
            x, y = self.vertex_to_coords(vertex)
            x_pixels, y_pixels = self.coords_to_pixels(x, y)
            x_pixels += self.cell_width // 2
            y_pixels += self.cell_height // 2
            self.s_g_moves_pixels.append([x_pixels, y_pixels])


    def produce_shortest_game(self, vertex_from, vertex_to):
        shortest_game = self.find_shortest_game(vertex_from, vertex_to)
        if shortest_game == -1:
            return -1
        elif shortest_game == []:
            return -2 #cannot draw
        elif shortest_game == -2:
            return -3
        current_vertex = vertex_from
        destination = vertex_from
        #s_g = shortest game
        self.s_g_descr = []
        self.s_g_vertex = [current_vertex]
        self.s_g_moves_pixels = []
        self.put_s_g_moves_pixels(current_vertex)
        moves = 0
        for index in shortest_game:
            if index == -1:
                destination = self.graph[current_vertex][0]
                if destination > current_vertex: #ladder
                    self.s_g_descr.append("Ladder from {} to {}".format(current_vertex, destination))
                else:  # snake
                    self.s_g_descr.append("Snake from {} to {}".format(current_vertex, destination))
            else:  # dice roll
                moves += 1
                destination = self.graph[current_vertex][index]
                self.s_g_descr.append("Roll nr {}. Dice is {}. Go from {} to {}".format(moves, index + 1, current_vertex, destination))
            self.put_s_g_moves_pixels(destination)
            self.s_g_vertex.append(destination)
            current_vertex = destination
        self.s_g_descr.append("Destination reached! This is the shortest game (by number of total moves).")


###################Class Maze#######################

class Maze(DirGraph, Grid):

    def __init__(self, width, height):
        Grid.__init__(self, width, height)
        self.solution = []
        DirGraph.__init__(self, width*height+2) #0- starting vertex, w*h+1 - ending vertex
        self.discovered = []
        self.discovered_init()
         #not yet discovered

    def coords_to_vertex(self, x, y):
        return Grid.coords_to_vertex(self, x, y) + 1

    def vertex_to_coords(self, vertex):
        return Grid.vertex_to_coords(self, vertex - 1)

    def discovered_init(self):
        self.discovered = []
        for i in range(0, self.width * self.height + 2):
            self.discovered.append(False)

    def all_visited(self):
        result = True
        for is_visited in self.discovered:
            result = result and is_visited
        return result

    def default_link(self):
        for y in range(0, self.height):
            for x in range(0, self.width):
                if x != self.width-1: #right
                    self.add_edge(self.coords_to_vertex(x, y), self.coords_to_vertex(x + 1, y))
                if x != 0: #left
                    self.add_edge(self.coords_to_vertex(x, y), self.coords_to_vertex(x - 1, y))
                if y != self.height-1: #top
                    self.add_edge(self.coords_to_vertex(x, y), self.coords_to_vertex(x, y + 1))
                if y != 0: #bottom
                    self.add_edge(self.coords_to_vertex(x, y), self.coords_to_vertex(x, y - 1))
        self.add_edge(0, 1) #start
        last = self.width * self.height
        self.add_edge(last, last+1) #last edge


    def generate_maze(self):
        # Generating maze using randomized DFS
        if self.size == 0:
            return -1  # empty
        maze = Maze(self.width, self.height)
        #self is default linked, maze is not, we will add edges chosen by DFS on self
        stack = []
        in_vertex = 0
        visited_counter = 1
        self.discovered[0] = True
        i=0
        while visited_counter < self.size:
            undiscovered_neighbours = [out_vertex for out_vertex in self.graph[in_vertex] if not self.discovered[out_vertex]]
            n = len(undiscovered_neighbours)
            if n != 0:
                out_vertex = undiscovered_neighbours[randint(0, n-1)]
                stack.append(in_vertex)
                maze.add_edge(in_vertex, out_vertex)  # add passage
                self.discovered[out_vertex] = True
                visited_counter += 1
                in_vertex = out_vertex
            elif stack: #not empty
                in_vertex = stack.pop()
        self.maze_graph = maze.graph  # copy the created maze


    def find_solution(self):
        #Performing BFS to generate solution of minimal steps
        for j in self.maze_graph:
            print(j, self.maze_graph[j])
        for j in self.graph:
            print(j, self.graph[j])


        if self.size == 0:
            return -1
        parent = {}
        self.discovered_init()
        self.discovered[0] = True
        processing = queue.Queue()  # vertices of given distance from source (vertex_from)
        processing.put(0)
        last = self.width * self.height + 1
        try:
            while not processing.empty() != 0:
                in_vertex = processing.get()
                for out_vertex in self.maze_graph[in_vertex]:
                    if not self.discovered[out_vertex]:
                        self.discovered[out_vertex] = True
                        processing.put(out_vertex)
                        parent[out_vertex] = in_vertex
                        if out_vertex == last:
                            raise Found

        except Found:
            vertex = last
            while vertex > 0:
                self.solution.append(vertex)
                vertex = parent[vertex]
            self.solution.append(0)
            self.solution = self.solution[::-1]


###################Class CanvasMaze#######################

class CanvasMaze(Maze, CanvasGrid):
    def __init__(self, width, height, border_to_cell_ratio, canvas_width, canvas_height):
        Maze.__init__(self, width, height)
        self.rectangles = []
        self.arrow = []
        self.solution_data = []
        CanvasGrid.__init__(self, width, height, canvas_width, canvas_height)
        self.border_to_cell_ratio = border_to_cell_ratio
        border_w = self.cell_width * self.border_to_cell_ratio
        border_h = self.cell_height * self.border_to_cell_ratio
        self.border = (border_w + border_h) // 2
        if self.border < 1:
            self.border = 1
        self.rotations = {"N": 270, "E": 0, "S": 90, "W": 180}


    def get_direction(self, in_vertex, out_vertex): #in_vertex and out_vertex must be connected!
        if out_vertex == in_vertex + 1: #right, it handles the exit too
            return 'E'
        elif out_vertex == in_vertex - 1: #left
            return 'W'
        elif out_vertex == in_vertex + self.width: #up, but y is inverted so: down
            return 'S'
        elif out_vertex == in_vertex - self.width: #down -> up
            return 'N'

    def coords_to_pixels(self, x, y):
        return (x*self.cell_width, y*self.cell_height)

    def maze_border_to_rectangles(self):
        self.rectangles.append([0, self.cell_height, self.border, self.canvas_height-self.cell_height, 0]) #left
        self.rectangles.append([self.canvas_width - self.border, 0, self.border, self.canvas_height, 0]) #right
        self.rectangles.append([0, 0, self.canvas_width, self.border, 0]) #top
        self.rectangles.append([0, self.canvas_height - self.border, self.canvas_width, self.border, 0]) #bottom

    def wall_to_rectangles(self, in_vertex, out_vertex):
        direction = self.get_direction(in_vertex, out_vertex)
        x_1, y_1 = self.vertex_to_coords(in_vertex)
        x_2, y_2 = self.vertex_to_coords(out_vertex)
        if direction == "S":
            self.rectangles.append([x_1*self.cell_width, y_1*self.cell_height + self.cell_height - self.border,\
                                   self.cell_width, self.border*2, 0])
        elif direction == "N":
            self.rectangles.append([x_2*self.cell_width, y_2*self.cell_height + self.cell_height - self.border,\
                                   self.cell_width, self.border*2, 0])
        elif direction == "E":
            self.rectangles.append([x_1*self.cell_width + self.cell_width - self.border, y_1*self.cell_height,\
                                    self.border*2, self.cell_height, 0])
        elif direction == "W":
            self.rectangles.append([x_2*self.cell_width + self.cell_width - self.border, y_2*self.cell_height,\
                                    self.border*2, self.cell_height, 0])


    def maze_to_rectangles(self):
        self.maze_border_to_rectangles()

        for in_vertex in self.graph:
            for out_vertex in self.graph[in_vertex]:
                if in_vertex != 0 and out_vertex != self.width*self.height+1:
                    if out_vertex not in self.maze_graph[in_vertex] and in_vertex not in self.maze_graph[out_vertex]: #double check edges
                        self.wall_to_rectangles(in_vertex, out_vertex)

    def generate_solution_data(self):
        self.generate_arrow()
        length = len(self.solution)
        for i in range(1, length-1): #except last
            direction = self.get_direction(self.solution[i], self.solution[i+1])
            x, y = self.vertex_to_coords(self.solution[i])
            x_pixels, y_pixels = self.coords_to_pixels(x, y)
            self.solution_data.append([x_pixels + self.cell_width // 2, y_pixels + self.cell_height // 2,\
                                       self.rotations[direction]])
            #(a, b, c) -> a: translate canvas a pixels right, b: translate canvas b pixels down,
            #c: rotate canvas by c degrees right
        print(self.solution_data)

    def generate_arrow(self):
        transl_x = self.cell_width // 2
        transl_y = self.cell_height // 2

        #start_x, start_y oriented such that left-upper corner of cell is (0,0)
        #we need to -transl_x, -transl_y to orient such that the center of cell is (0,0)
        start_x = 2 * self.cell_width // 3
        start_y = self.cell_height // 2
        #arrow to the east: "->"
        # 1. main line
        end_x = self.cell_width // 3
        end_y = start_y
        self.arrow.append([start_x - transl_x, start_y - transl_y, end_x - transl_x, end_y - transl_y])

        # 2. up line:
        end_x = self.cell_width // 2
        delta = start_x - end_x
        end_y = start_y + delta
        self.arrow.append([start_x - transl_x, start_y - transl_y, end_x - transl_x, end_y - transl_y])

        # 3. down line:
        end_y = start_y - delta
        self.arrow.append([start_x - transl_x, start_y - transl_y, end_x - transl_x, end_y - transl_y])

        #while processing lines we will rotate canvas - we will have arrows in all dierctions

###################Class WeightedDirGraph#######################

class WeightedDirGraph(DirGraph):
    def __init__(self, size):
        DirGraph.__init__(self, size)
        self.weights = {} #key: (vertex1, vertex2), value: weight

    def add_edge_w(self, vertex_from, vertex_to, weight): #also update weight
        result = DirGraph.add_edge(self, vertex_from, vertex_to)
        if result == 0: #new edge
            self.weights[(vertex_from, vertex_to)] = weight
            return 0
        elif result == -2: #duplicate, but update the weight
            self.weights[(vertex_from, vertex_to)] = weight
            return -2
        elif result == -1:
            return -1 #invalid edge
        else: #-3:
            return -3 #no self loopd

    def del_edge(self, vertex_from, vertex_to):
        result = DirGraph.del_edge(self, vertex_from, vertex_to)
        if result == 0:
            del self.weights[(vertex_from, vertex_to)] #delete weight
        return result #0:successful, -1:invalid vertices, -2:no edge

    def relabel(self, deleted_vertex): #relabel weights
        DirGraph.relabel(self, deleted_vertex)
        for in_vertex in self.graph:
            for out_vertex in self.graph[in_vertex]:
                old_in_v = in_vertex
                old_out_v = out_vertex
                changed = False
                if in_vertex >= deleted_vertex:
                    old_in_v += 1
                    changed = True
                if out_vertex >= deleted_vertex:
                    old_out_v += 1
                    changed = True
                if changed:
                    weight = self.weights[(old_in_v, old_out_v)]
                    del self.weights[(old_in_v, old_out_v)]
                    self.weights[(in_vertex, out_vertex)] = weight

    def normalize(self, size):  # adapts to new size, cut edges if size smaller, add vertices if bigger
        for in_vertex in self.graph:
            if in_vertex <= size:
                new_outgoing = []
                for out_vertex in self.graph[in_vertex]:
                    if out_vertex <= size:
                        new_outgoing.append(out_vertex)
                    else: #delete weight and don't add to outgoing
                        del self.weights[(in_vertex, out_vertex)]
            else:
                self.del_vertex(in_vertex)
        for i in range(self.size + 1, size + 1):
            self.append_vertex()
        self.size = size

    def get_weight(self, in_vertex, out_vertex):
        if not self.check_edge(in_vertex, out_vertex):
            return -1
        return self.weights[(in_vertex, out_vertex)]



class FlowNetwork(WeightedDirGraph):

    def __init__(self, size):
        WeightedDirGraph.__init__(self, size)
        self.flow = {}
        self.residual = WeightedDirGraph(size) # residual network graph

    def init_flow(self):
        self.flow = self.weights.copy()
        for edge in self.flow:
            self.flow[edge] = 0


    def get_residual(self):
        for in_vertex in self.graph:
            for out_vertex in self.graph[in_vertex]:
                rev_residual_cap = self.flow[(in_vertex, out_vertex)]
                residual_cap = self.weights[(in_vertex, out_vertex)] - self.flow[(in_vertex, out_vertex)]
                if residual_cap > 0:
                    self.residual.add_edge_w(in_vertex, out_vertex, residual_cap)
                else: # is zero, delete from residual network
                    self.residual.del_edge(in_vertex, out_vertex)

                if rev_residual_cap > 0:
                    self.residual.add_edge_w(out_vertex, in_vertex, rev_residual_cap)
                else:
                    self.residual.del_edge(out_vertex, in_vertex)


    def find_maximum_flow(self, source, sink):
        self.init_flow()
        if not self.check_vertex(source, sink):
            return -2
        if self.is_cyclic():
            return -1 #graph cannot be cyclic
        self.init_flow()
        self.get_residual()
        self.max_flow = 0
        while self.bfs(source, sink, self.residual.graph):
            cur_vertex = sink
            path_flow = float("Inf")
            while cur_vertex != source: #recover the path and find min capacity

                path_flow = min(path_flow, self.residual.get_weight(self.parent[cur_vertex], cur_vertex))
                cur_vertex = self.parent[cur_vertex]
            self.max_flow += path_flow #augument flow


            cur_vertex = sink
            while cur_vertex != source:
                parent_vertex = self.parent[cur_vertex]
                if self.check_edge(parent_vertex, cur_vertex): #update flow
                    self.flow[(parent_vertex, cur_vertex)] += path_flow
                else:
                    self.flow[(parent_vertex, cur_vertex)] -= path_flow
                cur_vertex = self.parent[cur_vertex]
            self.get_residual()
        return 0


class CanvasFlowNetwork(FlowNetwork, CanvasUndirGraph):

    def __init__(self, size, canvas_width, canvas_height):

        FlowNetwork.__init__(self, size)
        CanvasUndirGraph.__init__(self, size, canvas_width, canvas_height)
        self.TOTAL_FLOW_WIDTH = 50
        self.get_radius_small_large()
        self.ANGLE = 0.523
        self.flow_lines = []
        self.flow_lines_index = []


    def draw_pointed_line(self, vertex_from, vertex_to):
        self.arrow_length = self.radius_small // 2
        x1, y1 = self.vertex_to_pixels(vertex_from)
        x2, y2 = self.vertex_to_pixels(vertex_to)

        dy = y1 - y2
        dx = x1 - x2
        alpha = math.atan2(dy, dx) #angle between line and x-axis(at ending vertex)
        beta = alpha + self.ANGLE
        gamma = alpha - self.ANGLE
        beta_dx = self.arrow_length * math.cos(beta)
        beta_dy = self.arrow_length * math.sin(beta)
        gamma_dx = self.arrow_length * math.cos(gamma)
        gamma_dy = self.arrow_length * math.sin(gamma)
        start_x = x2 + self.radius_small * math.cos(alpha)
        start_y = y2 + self.radius_small * math.sin(alpha)
        beta_line = [start_x, start_y, start_x + beta_dx, start_y + beta_dy, -1, -1]
        gamma_line = [start_x, start_y, start_x + gamma_dx, start_y + gamma_dy, -1, -1]
        flow_start_x = x2 + 2 * self.radius_small * math.cos(alpha)
        flow_start_y = y2 + 2 * self.radius_small * math.sin(alpha)
        flow_end_x = x1 - self.radius_small * math.cos(alpha)
        flow_end_y = y1 - self.radius_small * math.sin(alpha)
        self.lines.append([x1, y1, x2, y2, vertex_from, vertex_to])
        self.lines.append(beta_line)
        self.lines.append(gamma_line)
        self.flow_lines.append([flow_start_x, flow_start_y, flow_end_x, flow_end_y, vertex_from, vertex_to, -1])
        # last value: -1: dont draw !=-1 specifies width

    def draw_default(self):
        if self.size < 2:
            return -1 #size needs to be >=2
        for in_vertex in self.graph:
            x_in, y_in = self.vertex_to_pixels(in_vertex)
            self.circles.append([x_in, y_in, self.radius_small])
            for out_vertex in self.graph[in_vertex]:
                self.draw_pointed_line(in_vertex, out_vertex)


    def produce_flow_lines(self):
        #run find_maximum_flow first
        for in_vertex in self.graph:
            for out_vertex in self.graph[in_vertex]:
                frac = self.flow[(in_vertex, out_vertex)] / self.max_flow
                line_width = self.TOTAL_FLOW_WIDTH * frac
                for flow_line in self.flow_lines:
                    if flow_line[4] == in_vertex and flow_line[5] == out_vertex:
                        flow_line[6] = line_width








