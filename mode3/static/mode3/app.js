$(function(){

    var canvas = document.getElementById("show_maze");
    var context = canvas.getContext("2d");
    var canvas2 = document.getElementById("solution");
    var context2 = canvas2.getContext("2d");

    function drawMaze() {
        for (var i=0; i < maze_rectangles.length; i++) {
            context.fillRect(maze_rectangles[i][0], maze_rectangles[i][1], maze_rectangles[i][2], maze_rectangles[i][3]);
        }
    }

    function showSolution() {
        for (var i=0; i < maze_solution_data.length; i++) {
            context2.save();
            context2.translate(maze_solution_data[i][0], maze_solution_data[i][1]);
            context2.rotate(maze_solution_data[i][2]*(Math.PI/180));
            for (var j=0; j<maze_arrow.length; j++) {
                context2.beginPath();
                context2.moveTo (maze_arrow[j][0], maze_arrow[j][1]);
                context2.lineTo (maze_arrow[j][2], maze_arrow[j][3]);
                context2.stroke();
            }
            context2.restore();
        }
    }

    function hideSolution() {
        context2.clearRect(0, 0, 500, 500);
    }

    $("#showHideSolution").on('click', function(event) {
        event.preventDefault;
        var linkText = $("#showHideSolution").text();
        if (linkText === "Show solution") {
            $("#showHideSolution").text('Hide solution')
            showSolution();
        } else {
            $("#showHideSolution").text('Show solution')
            hideSolution();
        }
    });
    drawMaze();
});