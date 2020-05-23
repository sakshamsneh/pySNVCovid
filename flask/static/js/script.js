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

$('#savesel').on('click', function () {
    var selectedvalues = $('#selcolval').val();
    if (selectedvalues.length != 0) {
        $('#selectmodal').modal('hide');
        // pass selectedvalues to /api/column, get updated table, add color to it
        $currentTable.find('tr').each(function () {
            $(this).find('th').eq(index).addClass('selected');
            $(this).find('td').eq(index - 1).addClass('selected');
        });
        selectedcol.push($column);
    } else {
        $('.toast').toast('show');
    }
})

$('th').on('click', function () {
    $currentTable = $(this).closest('table');
    index = $(this).index();
    if (selectedcol.includes($(this).html())) {
        // pass selectedcol to /api/column, get original table, remove color to it
        $currentTable.find('tr').each(function () {
            $(this).find('th').eq(index).removeClass('selected');
            $(this).find('td').eq(index - 1).removeClass('selected');
        });
        selectedcol = selectedcol.filter(f => f !== $(this).html());
    } else {
        $column = $(this).html();
        $.getJSON($SCRIPT_ROOT + '/api/column', {
            column: $column,
        }, function (data) {
            startmodal(data.collist);
        });
    }
});