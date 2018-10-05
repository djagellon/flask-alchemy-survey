$(function() {
    // Disables other input field until correct option is selected
    $('.other_open').each((i, el) => {
        console.log("FOUND OTHER", this);

        let $input = $(el).find('input');
        let question_id = $input.attr('id').split('_')[0];
        let $question = $(el).prev('.question' > '#' + question_id);

        $input.prop('disabled', true);

        $question.change((e) => {
            let question = event.currentTarget;
            let $other = $(question).find('input[value$=".other"]');
            let val = $other.val();
            let $open_input = $('#' + val.replace('.', '_'));

            $open_input.prop('disabled', !$other.prop('checked'));
        });

    });

});