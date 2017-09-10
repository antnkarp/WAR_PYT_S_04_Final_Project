


$(function(){
    function reDrawCircle(x, y) {
        context2.clearRect(0, 0, 500, 500);
        context2.beginPath();
        context2.arc(x, y, circle_radius, 0, 2*Math.PI);
        context2.stroke();
    }


    function showShortestGame(result) {
        var i = 0;
        var s_g_vertex = result.s_g_vertex;
        var s_g_moves_pixels = result.s_g_moves_pixels;
        var s_g_descr = result.s_g_descr;
        var stop = 0;

        if (s_g_vertex[0] != 0) { //initial drawing
                reDrawCircle(s_g_moves_pixels[0][0], s_g_moves_pixels[0][1]);
        }
        var x1;
        var y1;
        var x2;
        var y2;

        var cur_x; //cur_x is a float
        var cur_y; //cur_y is a float
        var diff_x;
        var diff_y;
        var sign_x;
        var sign_y;

        var steps = 100;
        var total_time = 1000;
        var delay = Math.floor(total_time / steps);

        var dx; //dx is a float
        var dy; //dy is a float

        function getNext() {
            if (s_g_moves_pixels[i] === [-1]) {
                console.log(i)
                i = i+1;
            } else if ( i>=s_g_moves_pixels.length-1) {
                stop = 1;
            } else {
                console.log(i)
                x1 = s_g_moves_pixels[i][0];
                y1 = s_g_moves_pixels[i][1];
                x2 = s_g_moves_pixels[i+1][0];
                y2 = s_g_moves_pixels[i+1][1];
                cur_x = x1;
                cur_y = y1;
                diff_x = x2 - x1;
                diff_y = y2 - y1;
                if (diff_x > 0) {
                   sign_x = 1;
                } else if (diff_x < 0) {
                   sign_x = -1;
                }
                if (diff_y > 0) {
                   sign_y = 1;
                } else if (diff_y < 0) {
                   sign_y = -1;
                }
                dx = diff_x / steps;
                dy = diff_y / steps;
                appendDescr();
                i = i + 1;
            }

        }
        function appendDescr() {
            var newSpan = $("<span>");
            newSpan.html(result.s_g_descr[i]+"<br>");
            $("#shortestGameDescr").append(newSpan);
        }
        getNext();
        getNext();
        function animationLoop() {
            reDrawCircle(Math.floor(cur_x), Math.floor(cur_y));
            cur_x += dx;
            cur_y += dy;
            if ( (x2 - cur_x)*sign_x < 0 || (y2-cur_y)*sign_y < 0) {
                    getNext();
            }
            if (stop === 1) {
                clearInterval(transition);
                reDrawCircle(x2, y2);
                appendDescr();
            }

        }
        var transition = setInterval(function(){ animationLoop() }, delay);

    }

    function clearDescr() {

    }



    function showError(result) {

    }

    var canvas = document.getElementById("show_board");
    var context = canvas.getContext("2d");
    var canvas2 = document.getElementById("solution");
    var context2 = canvas2.getContext("2d");


    var done = true;

    context2.lineWidth = circle_border;
    context2.strokeStyle = circle_color;

    for (var i=0; i<rectangles.length; i++) { //fields
        context.fillStyle = rectangles[i][4];
        context.fillRect(rectangles[i][0], rectangles[i][1], rectangles[i][2], rectangles[i][3]);

    }
    for (var i=0; i<lines.length; i++) { //transfers
        context.beginPath();
        context.strokeStyle = lines[i][4];
        context.lineWidth = lines[i][5];
        context.moveTo (lines[i][0], lines[i][1]);
        context.lineTo (lines[i][2], lines[i][3]);
        context.stroke();
    }
    context.lineWidth = 1;

    for (var i=0; i<rectangles.length; i++) { //labels
        context.font = rectangles[i][7] + ' px Arial';
        context.fillStyle = rectangles[i][8];
        context.fillText(i+1,rectangles[i][5],rectangles[i][6]);
    }
    $("#linkShowShortestGame").on('click', function(event) {
        $("#formShowShortestGame").toggle();
    });
    $("#formShowShortestGame").toggle(); //hide

    $("#formShowShortestGame").on('submit', function(event) {
        event.preventDefault();
        $("#shortestGameDescr").empty();
        $.ajax({
            url: url,
            data: $("#formShowShortestGame").serialize(),
            type: "POST",
            dataType: "json"
        }).done(function(result) {

            if (result['error'] == 0) {
                showShortestGame(result);

            } else {
                showError(result);
            }
        });
    });
    $("#linkGraphStructure").on('click', function(event) {
        $("#divGraphStructure").toggle();
    });
    $("#divGraphStructure").toggle(); // hide

});
//});