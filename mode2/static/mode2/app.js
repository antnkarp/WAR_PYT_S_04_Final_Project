$(function(){

    var canvas = $("#show_graph");
    var context = canvas[0].getContext("2d");

    var dx = 0;
    var dy = 0;
    var moving_circle = -1;
    var last_x = 0;
    var last_y = 0;
    var initial_x1 = [];
    var initial_y1 = [];
    var diff_x;
    var diff_y;
    var cur_frac=1;
    var i=1;
    var j;
    var TRANSITION_TIME = 500;
    var STEPS = 100;
    var FRAC_STEP = cur_frac / STEPS;
    var DELAY = TRANSITION_TIME / STEPS;
    var stop = 0;
    var animation;



    function inCircle(circle, x, y) {
        var result = Math.pow(x-circle[0], 2) + Math.pow(y-circle[1], 2);
        if (result <= Math.pow(circle[2], 2)) {
            return true;
        } else {
            return false;
        }
    }
    function distance(x1, y1, x2, y2) {
        return Math.sqrt(Math.pow((x1-x2), 2) + Math.pow((y1-y2), 2));
    }

    function overlappingCircles(cur_index) {
        for (var i=0; i<circles.length; i++) {
            if (i==cur_index) {
                continue;
            }
            dist = distance(circles[cur_index][0], circles[cur_index][1], circles[i][0], circles[i][1]);
            if (dist <= circles[cur_index][2] + circles[i][2]) {
                return true;
            }
        }
        return false;
    }

    function reDraw() {
        context.clearRect(0, 0, 500, 500);
        for (var i=0; i<lines.length; i++) {
            if (lines[i][6] == 1) { //draw if visible
                context.beginPath();
                context.moveTo(lines[i][0], lines[i][1]);
                context.lineTo(lines[i][2], lines[i][3]);
                context.stroke();
             }
        }
         for (var i=0; i<circles.length; i++) {
            if (circles[i][3] == 1) { //draw if visible
                context.beginPath();
                context.arc(circles[i][0], circles[i][1], circles[i][2], 0, 2*Math.PI);
                context.fillStyle = 'white';
                context.fill();
                context.font = (circles[i][2] / 2) + 'px Arial';
                context.fillStyle = 'black';
                context.fillText(i,circles[i][0],circles[i][1]);
                context.stroke();
            }
        }
    }

    function updateLines(moving_circle) {
        for (var i=0; i<lines.length; i++) {
            if (lines[i][4] == moving_circle) {  //ingoing
                lines[i][0] = circles[moving_circle][0];
                lines[i][1] = circles[moving_circle][1];
            }
            if (lines[i][5] == moving_circle) { //outgoing
                lines[i][2] = circles[moving_circle][0];
                lines[i][3] = circles[moving_circle][1];
            }
        }

    }


    function restore() {
        for (var i=0; i<lines.length; i++) { //make visible
            lines[i][6] = 1;
        }
        for (var i=0; i<circles.length; i++) {
            circles[i][3] = 1;
        }
        reDraw();
    }


    function Animate() {

        function animationLoop() {
            cur_frac -= FRAC_STEP;
            if (stop == 1) {
                clearInterval(animation);
            }
            if (cur_frac <= 0) {
                getNext();
            } else {
                normalizeLine();
                //console.log(cur_frac);
                reDraw();
            }
//            if (i>=2) {
//                clearInterval(animation)
//            }
        }

        var animation = setInterval(function(){ animationLoop() }, DELAY);
    }

    function restoreLines() {
            var j;
            for (var i=1; i<euler_path.length; i++) {
                j = getLine(euler_path[i-1], euler_path[i]);
                lines[j][0] = initial_x1[i-1];
                lines[j][1] = initial_y1[i-1];
            }

    }

    function normalizeLine() {
            var x2 = lines[j][2];
            var y2 = lines[j][3];
            lines[j][0] = x2 + (diff_x * cur_frac);
            lines[j][1] = y2 + (diff_y * cur_frac);
    }

    function getNext() {
        if (i >= euler_path.length) {
            stop = 1;
        } else {
            vertex_from = euler_path[i-1];
            vertex_to = euler_path[i];
            j = getLine(vertex_from, vertex_to);
            diff_x = initial_x1[i-1] - lines[j][2];
            diff_y = initial_y1[i-1] - lines[j][3];
            i = i + 1;
            cur_frac = 1;
        }
    }

    function getLine(in_vertex, out_vertex) {
        for (var i=0; i<lines.length; i++) {
            if (lines[i][4] == in_vertex && lines[i][5] == out_vertex) {
                return i;
            }
            if (lines[i][4] == out_vertex && lines[i][5] == in_vertex) {
                //change direction, we want always start at in_vertex and end in out_vertex
                lines[i][4] = in_vertex;
                lines[i][5] = out_vertex;
                var temp = lines[i][0] //x_in
                lines[i][0] = lines[i][2]
                lines[i][2] = temp
                temp = lines[i][1] //y_in
                lines[i][1] = lines[i][3]
                lines[i][3] = temp
                return i;
            }
        }
    }

    function initAnimation() {
            var j;
            for (var i=1; i<euler_path.length; i++) {
                j = getLine(euler_path[i-1], euler_path[i]);
                initial_x1.push(lines[j][0]);
                initial_y1.push(lines[j][1]);
            }
    }

    function hideEdge(in_vertex, out_vertex) {
            for (var i=0; i<lines.length; i++) {
                if ((lines[i][4] == in_vertex && lines[i][5] == out_vertex) ||
                   (lines[i][4] == out_vertex && lines[i][5] == in_vertex)) {

                    lines[i][6] = 0;
                }
            }
    }

    function appendDescr() {
        var newSpan = $("<span>");
        newSpan.html(i + ". Go from" + euler_path[i-1] + " to " + euler_path[i] + "<br>");
        $("eulerPathDescr").append(newSpan);
    }

    $("#show_euler_path").on('click', function(event) {
        event.preventDefault();
        initAnimation();
        getNext();
        Animate();
    });

    $("#restoreCanvas").on('click', function(event) {
        event.preventDefault();
        restoreLines();
        cur_frac=1;
        i=1;
        stop=0;
        reDraw();
    });

    reDraw();
    canvas.on('mousedown', function(event) {
        event.preventDefault();

        var offset = $("#show_graph").offset();
        var x = event.clientX - offset.left;
        var y = event.clientY - offset.top;
        for (var i=0; i<circles.length; i++) {
            if (inCircle(circles[i], x, y)) {
                moving_circle = i; //move this circle
                dx = x - circles[i][0];
                dy = y - circles[i][1];
                last_x = circles[i][0];
                last_y = circles[i][1];
            }
        }

    });
    canvas.on('mouseup mouseleave', function(event) {
        event.preventDefault();

        if (moving_circle != -1) {
            circles[moving_circle][0] = last_x;
            circles[moving_circle][1] = last_y;
            updateLines(moving_circle);
            reDraw();
        }
        moving_circle = -1;

    });
    canvas.on('mousemove', function(event) {
        event.preventDefault();

         if ((moving_circle != -1) && !overlappingCircles(moving_circle)) {
                last_x = circles[moving_circle][0]
                last_y = circles[moving_circle][1]

                var offset = $("#show_graph").offset();
                var x = event.clientX - offset.left;
                var y = event.clientY - offset.top;

                circles[moving_circle][0] = x - dx;
                circles[moving_circle][1] = y - dy;

                updateLines(moving_circle);
                reDraw();

         }
    });

});