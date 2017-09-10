$(function(){

    var canvas = $("#show_graph");
    var context = canvas[0].getContext("2d");

    var moving_circle_dx = 0;
    var moving_circle_dy = 0;

    var moving_circle = -1;
    var last_x = 0;
    var last_y = 0;
    var diff_x;
    var diff_y;
    var cur_frac=1;
    var i=1;
    var j;

    var stop = 0;


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
            context.beginPath();
            context.moveTo(lines[i][0], lines[i][1]);
            context.lineTo(lines[i][2], lines[i][3]);
            context.stroke();
        }

        context.strokeStyle = 'blue';
        for (var i=0; i<flow_lines.length; i++) {
            if (flow_lines[i][6] != -1) {
                context.beginPath();
                context.moveTo(flow_lines[i][0], flow_lines[i][1]);
                context.lineTo(flow_lines[i][2], flow_lines[i][3]);
                context.lineWidth = flow_lines[i][6]
                context.stroke();
            }
        }
        context.strokeStyle = 'black';
        context.lineWidth = 1;

        for (var i=0; i<circles.length; i++) {
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

    function updateArrow(i) {
        //we know that beta is at index i+1, gamma: i+2 (check classes.py)
        //code is repeated, but such reference is easy
        var x1 = lines[i][0];
        var y1 = lines[i][1];
        var x2 = lines[i][2];
        var y2 = lines[i][3];

        var vertex_from = lines[i][4];
        var vertex_to = lines[i][5];
        var dy = y1 - y2;
        var dx = x1 - x2;
        var alpha = Math.atan2(dy, dx);
        var beta = alpha + ANGLE;
        var gamma = alpha - ANGLE;
        var arrow_length = radius_small / 2;
        var beta_dx = arrow_length * Math.cos(beta);
        var beta_dy = arrow_length * Math.sin(beta);
        var gamma_dx = arrow_length * Math.cos(gamma);
        var gamma_dy = arrow_length * Math.sin(gamma);
        var start_x = x2 + radius_small * Math.cos(alpha);
        var start_y = y2 + radius_small * Math.sin(alpha);
        lines[i+1][0] = start_x;
        lines[i+1][1] = start_y;
        lines[i+1][2] = start_x + beta_dx;
        lines[i+1][3] = start_y + beta_dy;

        lines[i+2][0] = start_x;
        lines[i+2][1] = start_y;
        lines[i+2][2] = start_x + gamma_dx;
        lines[i+2][3] = start_y + gamma_dy;


    }

    function updateFlowLine(i, vertex_from, vertex_to) {
        var index;
        for (var j=0; j<flow_lines.length; j++) {
            if (flow_lines[j][4] === vertex_from && flow_lines[j][5] === vertex_to) {
                index = j;
            }
        }
        var x1 = lines[i][0];
        var y1 = lines[i][1];
        var x2 = lines[i][2];
        var y2 = lines[i][3];
        var dy = y1 - y2;
        var dx = x1 - x2;
        var alpha = Math.atan2(dy, dx);
        var start_x = x2 + 2 * radius_small * Math.cos(alpha);
        var start_y = y2 + 2 * radius_small * Math.sin(alpha);
        var end_x = x1 - radius_small * Math.cos(alpha);
        var end_y = y1 - radius_small * Math.sin(alpha);
        flow_lines[index][0] = start_x;
        flow_lines[index][1] = start_y;
        flow_lines[index][2] = end_x;
        flow_lines[index][3] = end_y;
    }

    function updateLines(moving_circle) {
        for (var i=0; i<lines.length; i++) {
            if (lines[i][4] == moving_circle) {  //ingoing
                lines[i][0] = circles[moving_circle][0];
                lines[i][1] = circles[moving_circle][1];
                updateArrow(i);
                updateFlowLine(i, lines[i][4], lines[i][5]);
            }
            if (lines[i][5] == moving_circle) { //outgoing
                lines[i][2] = circles[moving_circle][0];
                lines[i][3] = circles[moving_circle][1];
                updateArrow(i);
                updateFlowLine(i, lines[i][4], lines[i][5]);
            }
        }

    }

//    function appendDescr() {
//        var newSpan = $("<span>");
//        newSpan.html(i + ". Go from" + euler_path[i-1] + " to " + euler_path[i] + "<br>");
//        $("eulerPathDescr").append(newSpan);
//    }



    canvas.on('mousedown', function(event) {
        event.preventDefault();

        var offset = $("#show_graph").offset();
        var x = event.clientX - offset.left;
        var y = event.clientY - offset.top;
        for (var i=0; i<circles.length; i++) {
            if (inCircle(circles[i], x, y)) {
                moving_circle = i; //move this circle
                moving_circle_dx = x - circles[i][0];
                moving_circle_dy = y - circles[i][1];
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

                circles[moving_circle][0] = x - moving_circle_dx;
                circles[moving_circle][1] = y - moving_circle_dy;

                updateLines(moving_circle);
                reDraw();

         }
    });

    function showMaximumFlow(result) {
        for (var i=0; i<flow_lines.length; i++) {
            flow_lines[i][6] = result.flow_lines[i][6]; //hide
        }
        reDraw();
    }


    function showError(result) {

    }

    $("#linkFindMaximumFlow").on('click', function(event) {
        $("#formFindMaximumFlow").toggle();
    });
    $("#formFindMaximumFlow").toggle(); //hide

    $("#formFindMaximumFlow").on('submit', function(event) {
        event.preventDefault();
        $.ajax({
            url: url,
            data: $("#formFindMaximumFlow").serialize(),
            type: "POST",
            dataType: "json"
        }).done(function(result) {
            if (result['error'] == 0) {
                showMaximumFlow(result);

            } else {
                showError(result);
            }
        });
    });
    $("#restoreCanvas").on('click', function(event) {
        for (var i=0; i<flow_lines.length; i++) {
            flow_lines[i][6] = -1; //hide
            reDraw();
        }
    });
    reDraw();
});