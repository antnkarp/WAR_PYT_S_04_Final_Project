from django.shortcuts import render
from django.views import View
from modules.classes import CanvasMaze

from modules.classes import Maze

class Main(View):
    def get(self, request):
        maze = CanvasMaze(100, 100, 0.1, 1000, 1000)
        maze.default_link()
        maze.generate_maze()
        maze.find_solution()
        maze.maze_to_rectangles()
        maze.generate_solution_data()
        return render(request, 'mode3/main.html', {"maze": maze})
# Create your views here.
