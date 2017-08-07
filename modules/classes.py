import queue
import _pickle
import base64
from django.apps import apps
from random import randint
import math

class Found(Exception):
    pass

class ManageNamedGraph(): # Named Graph  = Graph + Description

    def __init__(self, app_name, model_name):
        self.graph = None
        self.description = ""
        self.app_name = app_name
        self.model_name = model_name

    def load_named_graph(self, id):
        named_graph = apps.get_model(self.app_name, self.model_name).objects.get(id=id)
        self.graph = _pickle.loads(base64.b64decode(named_graph.pickled_graph))
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
        self.graph = {}
        self.last = -1
        self.size = 0
        for i in range(0, size):
            self.append_vertex()

    def append_vertex(self):
        self.graph[self.last+1] = []
        self.last += 1
        self.size += 1

    def check_vertex(self, *args):
        for vertex in args:
            single_result = 0 <= vertex <= self.last and type(vertex) is int
            if not single_result:
                return False
        return True



    def add_edge(self, vertex_from, vertex_to):
        if not(self.check_vertex(vertex_from, vertex_to)):
            return -1 #Invalid vertices
        if vertex_to not in self.graph[vertex_from]: #avoid duplicates
            self.graph[vertex_from].append(vertex_to)

    def del_edge(self, vertex_from, vertex_to):
        if not(self.check_vertex(vertex_from, vertex_to)):
            return -1 #Invalid vertices
        if vertex_to in self.graph[vertex_from]:
            self.graph[vertex_from].remove(vertex_to)

    def relabel(self, deleted_vertex):

        for in_vertex in range(0, self.last):
            if in_vertex >= deleted_vertex: #relabel all vertices >= del_vertex, refer to next vertex
                self.graph[in_vertex] = self.graph[in_vertex+1]

        for in_vertex in range(0, self.last):
            for out_vertex in self.graph[in_vertex]:
                if out_vertex > deleted_vertex:
                 #relabel all edges leading after del_vertex
                    self.graph[in_vertex].remove(out_vertex) #(every vertex>del_vertex decreases by 1)
                    self.graph[in_vertex].append(out_vertex-1)
                    self.graph[in_vertex].sort()

        del self.graph[self.last]


    def del_vertex(self, vertex):
        if not(self.check_vertex(vertex)):
            return -1
        #delete edges to vertex
        for ingoing in self.graph:
            if ingoing == vertex:
                continue
            if vertex in self.graph[ingoing]:
                self.del_edge(ingoing, vertex)

        self.relabel(vertex)
        self.last -= 1 # we removed 1 vertex

    def cut_vertex(self, vertex): #
        if not(self.check_vertex(vertex)):
            return -1
        self.graph[vertex] = []

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
                    if out_vertex in discovered:
                        return True #back edge
                    else:
                        stack.append(out_vertex)
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
        if vertex2 not in self.graph[vertex1]:
            self.graph[vertex1].append(vertex2)
            self.graph[vertex1].sort()
        if vertex1 not in self.graph[vertex2]:
            self.graph[vertex2].append(vertex1)
            self.graph[vertex2].sort()

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
            graph = self
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
        self.cut_vertex(vertex_from)
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
        new_graph = self
        new_graph.default_link_vertex(prev_from)
        new_graph.transfers.remove(prev_from)
        new_graph.add_transfer(new_from, new_to)
        if new_graph.is_cyclic(): #new_graph is not empty
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
        return [-1] #we cannot reach vertex_to



class Coords():
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def coords_to_vertex(self, x, y): #we start at (0,0)
        if 0 <= x < self.width and 0 <= y < self.height:
            return (x + 1) + y * self.width
        else:
            return -1

    def vertex_to_coords(self, vertex):
        if vertex == 0:
            return (0, 0)
        else:
            x = vertex % self.width
            if x == 0:
                x = self.width
            y = (vertex - x) // self.width
            x -= 1
        return (x, y)


class CanvasBoard(Board, Coords):
    def __init__(self, size, canvas_width, canvas_height):
        Coords.__init__(self, 0, 0) #values not used
        Board.__init__(self, size)
        self.width = int(math.sqrt(size)) + 1
        self.height = self.width
        self.rectangles = []
        self.lines = []
        self.cell_width = canvas_width // self.width
        self.canvas_width = self.cell_width * self.width
        self.cell_height = canvas_height // self.height
        self.canvas_height = self.cell_height * self.height

    def board_to_rectangles(self):
        for vertex in self.graph:
            if vertex == 0:
                continue
            x, y = self.vertex_to_coords(vertex)
            if vertex % 2 == 0:
                color = "gray"
            else:
                color = "black"
            self.rectangles.append((x*self.cell_width, self.canvas_height - (y+1)*self.cell_height,\
                                    self.cell_width, self.cell_height, color, vertex))

    def coords_to_pixels(self, x, y): #returns upper left corner
        return (x * self.cell_width, self.canvas_height - (y+1) * self.cell_height)

    def draw_transfers(self):
        print(self.transfers)
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
            self.lines.append((x1_pixels, y1_pixels, x2_pixels, y2_pixels, color))


###################Class Maze#######################

class Maze(DirGraph, Coords):

    def __init__(self, width, height):
        Coords.__init__(self, width, height)
        self.solution = []
        DirGraph.__init__(self, width*height+2) #0- starting vertex, w*h+1 - ending vertex

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
        last = 0
        all_vertices = list(self.graph.keys())
        all_vertices_no_exit = all_vertices[:]
        all_vertices_no_exit.remove(self.width*self.height+1) #remove exit

        in_vertex = 0
        discovered = [0]

        while set(discovered) != set(all_vertices):
            undiscovered_neighbours = [out_vertex for out_vertex in self.graph[in_vertex] if out_vertex not in discovered ]
            n = len(undiscovered_neighbours)
            if n != 0:
                out_vertex = undiscovered_neighbours[randint(0, n-1)]
                stack.append(in_vertex)
                maze.add_edge(in_vertex, out_vertex)  # add passage
                if out_vertex not in discovered:
                    discovered.append(out_vertex)
                in_vertex = out_vertex
            elif stack: #not empty
                in_vertex = stack.pop() #we know that stack is not empty, because graph is connected

        self.maze_graph = maze.graph #copy the created maze to self

    def find_solution(self):
        #Performing BFS to generate solution of minimal steps
        if self.size == 0:
            return -1
        parent = {}
        discovered = [0]  # list of visited vertices
        processing = queue.Queue()  # vertices of given distance from source (vertex_from)
        processing.put(0)
        last = self.width * self.height + 1
        try:
            while not processing.empty():
                in_vertex = processing.get()
                for out_vertex in self.maze_graph[in_vertex]:
                    if out_vertex not in discovered:
                        discovered.append(out_vertex)
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



class CanvasMaze(Maze):
    def __init__(self, width, height, border_to_cell_ratio, canvas_width, canvas_height):
        super().__init__(width, height)
        self.rectangles = []
        self.arrow = []
        self.solution_data = []
        self.border_to_cell_ratio = border_to_cell_ratio
        self.cell_width = canvas_width // self.width
        self.cell_height = canvas_height // self.height
        self.canvas_width = self.cell_width * self.width
        self.canvas_height = self.cell_height * self.height
        border_w = self.cell_width * self.border_to_cell_ratio
        border_h = self.cell_height * self.border_to_cell_ratio
        self.border = (border_w + border_h) // 2
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
        self.rectangles.append((0, self.cell_height, self.border, self.canvas_height-self.cell_height, 0)) #left
        self.rectangles.append((self.canvas_width - self.border, 0, self.border, self.canvas_height, 0)) #right
        self.rectangles.append((0, 0, self.canvas_width, self.border, 0)) #top
        self.rectangles.append((0, self.canvas_height - self.border, self.canvas_width, self.border, 0)) #bottom

    def wall_to_rectangles(self, in_vertex, out_vertex):
        direction = self.get_direction(in_vertex, out_vertex)
        x_1, y_1 = self.vertex_to_coords(in_vertex)
        x_2, y_2 = self.vertex_to_coords(out_vertex)
        if direction == "S":
            self.rectangles.append((x_1*self.cell_width, y_1*self.cell_height + self.cell_height - self.border,\
                                   self.cell_width, self.border*2, 0))
        elif direction == "N":
            self.rectangles.append((x_2*self.cell_width, y_2*self.cell_height + self.cell_height - self.border,\
                                   self.cell_width, self.border*2, 0))
        elif direction == "E":
            self.rectangles.append((x_1*self.cell_width + self.cell_width - self.border, y_1*self.cell_height,\
                                    self.border*2, self.cell_height, 0))
        elif direction == "W":
            self.rectangles.append((x_2*self.cell_width + self.cell_width - self.border, y_2*self.cell_height,\
                                    self.border*2, self.cell_height, 0))

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
            self.solution_data.append((x_pixels + self.cell_width // 2, y_pixels + self.cell_height // 2,\
                                       self.rotations[direction]))
            #(a, b, c) -> a: translate canvas a pixels right, b: translate canvas b pixels down,
            #c: rotate canvas by c degrees right

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
        self.arrow.append((start_x - transl_x, start_y - transl_y, end_x - transl_x, end_y - transl_y))

        # 2. up line:
        end_x = self.cell_width // 2
        delta = start_x - end_x
        end_y = start_y + delta
        self.arrow.append((start_x - transl_x, start_y - transl_y, end_x - transl_x, end_y - transl_y))

        # 3. down line:
        end_y = start_y - delta
        self.arrow.append((start_x - transl_x, start_y - transl_y, end_x - transl_x, end_y - transl_y))

        #while processing lines we will rotate canvas - we will have arrows in all dierctions




