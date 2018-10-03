$(function() {
    // Disables other input field until correct option is selected
    $('.other_open').each((i, el) => {
        console.log("FOUND OTHER", this);

        let $input = $(el).find('input');
        let question_id = $input.attr('id').split('_')[0];
        let $question = $(el).prev('.question' > '#' + question_id);

        $input.prop('disabled', true);

        $question.change((e) => {
            let val = e.target.value;
            let $input = $('#' + val.split('.')[0] + '_other');
            let input_id = $input.attr('id').replace('_', '.');

            $input.prop('disabled', val !== input_id);
        });

    });

});