jQuery(function ($) {
    var input_id, elem, parent;
    input_id = '#' + '{{ id }}';
    elem = $(input_id);
    parent = elem.parent();

    if (!parent.hasClass('input-append')) {
        parent.addClass('input-append')
    }

    if (!parent.hasClass('date')) {
        parent.addClass('date')
    }

    elem.after('<span class="add-on"><i data-time-icon="icon-time" data-date-icon="icon-calendar"></i></span>');

    parent.datetimepicker({
        format : '{{ format }}',
        trigger : '{{ trigger }}',
        maskInput : '{{ mask_input }}',

        pick12HourFormat :{{ pick_12_hour_format }},
        pickSeconds : {{ pick_seconds }},
        pickDate : {{ pick_date }},

        startDate : '{{ startDate }}',
        endDate : '{{ endDate }}'
    });
});