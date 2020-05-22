var selectedcol = [];

$(document).on('click', 'a', function () {
    $('#type').html("Graph Options for type " + this.id.toUpperCase());
    $('#graphselector').show();
});

$('#graphtype').on('click', function () {
    $('#graphselector').hide();
})

$('th').on('click', function () {
    var $currentTable = $(this).closest('table');
    var index = $(this).index();
    if (selectedcol.includes($(this).html())) {
        $currentTable.find('tr').each(function () {
            $(this).find('th').eq(index).removeClass('selected');
            $(this).find('td').eq(index - 1).removeClass('selected');
        });
        selectedcol = selectedcol.filter(f => f !== $(this).html());
    } else {
        $currentTable.find('tr').each(function () {
            $(this).find('th').eq(index).addClass('selected');
            $(this).find('td').eq(index - 1).addClass('selected');
        });
        selectedcol.push($(this).html());
    }
});