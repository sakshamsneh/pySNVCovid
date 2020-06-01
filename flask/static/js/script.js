$('#csvfile').on('change', function () {
    var fileName = $(this).val().replace('C:\\fakepath\\', " ");
    $(this).next('.custom-file-label').html(fileName);
})


$('#graphtype').on('dblclick', function () {
    $('#graphselector').hide();
});

$('.graphitem').on('click', function () {
    $('#type').html("Graph Options for type " + this.id.toUpperCase());
    if (this.id != 'pie')
        $('#selcolumn').attr('multiple', 'true');
    else
        $('#selcolumn').removeAttr('multiple');
    $('#graphselector').show();
});

function startmodal(collist) {
    $('#selcolval').find('option').remove();
    $.each(collist, function (_, text) {
        $('#selcolval').append($('<option></option>').val(text).html(text))
    });
    $('#selectmodal').modal('show');
}

var $currentTable = null;
var index = null;
var selectedcol = [];
var $column = null;
$.ajax({
    traditional: true
})

// var $selectedvalues = null;

$('#savesel').on('click', function () {
    var $selectedvalues = $('#selcolval').val();
    if ($selectedvalues.length != 0) {
        $('#selectmodal').modal('hide');
        // pass selectedvalues to /api/column, get updated table, add color to it
        $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/api/columnvalues',
            data: JSON.stringify({ column: $column, values: $selectedvalues }),
            success: function (_) {
                $currentTable.find('tr').each(function () {
                    $(this).find('th').eq(index).addClass('selected');
                    $(this).find('td').eq(index - 1).addClass('selected');
                });
                selectedcol.push($column);
            },
            contentType: "application/json",
            dataType: 'json'
        });
    } else {
        $('.toast').toast('show');
    }
})

$('th').on('click', function () {
    $currentTable = $(this).closest('table');
    index = $(this).index();
    var col = $(this).html();
    if (selectedcol.includes(col)) {
        // pass selectedcol to /api/column, get original table, remove color to it
        $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/api/columnvalues',
            data: JSON.stringify({ column: selectedcol }),
            success: function (_) {
                $currentTable.find('tr').each(function () {
                    $(this).find('th').eq(index).removeClass('selected');
                    $(this).find('td').eq(index - 1).removeClass('selected');
                });
                selectedcol = selectedcol.filter(f => f !== col);
            },
            contentType: "application/json",
            dataType: 'json'
        });
    } else {
        $column = $(this).html();
        $.getJSON($SCRIPT_ROOT + '/api/column', {
            column: $column,
        }, function (data) {
            startmodal(data.collist);
        });
    }
});

function show_graph(data) {
    const myChart = document.getElementById('myChart');
    var ctx = myChart.getContext('2d');
    $('#chart').css("height", '90vh');
    Chart.defaults.global.defaultFontColor = 'white';
    var dispChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
            datasets: [1, 2, 3].map(function (i) {
                return {
                    label: 'Dataset ' + i,
                    data: [0, 0, 0, 0, 0, 0, 0].map(Math.random),
                    fill: false
                };
            })
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: { beginAtZero: true },
                    gridLines: { color: 'rgba(255, 255, 255, 0.7)' }
                }],
                xAxes: [{ gridLines: { color: 'rgba(255, 255, 255, 0.3)' } }]
            },
            responsive: true,
            maintainAspectRatio: false,
            plugins: { colorschemes: { scheme: 'tableau.Classic10' } }
        }
    });
    myChart.scrollIntoView();
}

$('#genbtn').on('click', function () {
    var $columnselected = $('#selcolumn').val();
    console.log($columnselected);
    $.getJSON($SCRIPT_ROOT + '/api/graph', {
        graph_fields: JSON.stringify($columnselected),
    }, function (data) {
        console.log(data);
        show_graph(data);
    });
});

var position = $(window).scrollTop();
$(window).scroll(function () {
    var scroll = $(window).scrollTop();
    if (scroll <= position)
        $(window).scrollTop(0);
    position = scroll;
});

// $('#selcolumn').change(function () {
//     // console.log(this.value);
//     $selectedvalues.push(this.value);
// })