function calculate_total(item_cell, total_cell) {
    // Creates a sum over all `item_cell` values and adds it to the
    // `total_cell`

    var total = 0;
    $(item_cell).each(function() {
        total += parseFloat($(this).html());
    });
    $(total_cell).html(total);
}

$(document).ready(function() {
    calculate_total('.costsTime', '.costsTimeTotal');
    calculate_total('.costsCosts', '.costsCostsTotal');
});
