$(function() {

    async function getShortOutput(modal, label) {
        let output_url = `/api/report/short/${modal}/${label}`;
        let response = await fetch(output_url);
        let data = await response.json();

        return data;
    }

    async function markComplete(module, action) {
        let complete_url = `/api/report/complete/${module}/${action}`;
        let response = await fetch(complete_url);
        let data = await response.json();

        return data;
    }

    function getModule() {
        let path = window.location.pathname;
        return path.split('/').slice(-1)[0];
    }

    $("button.mark-complete").on("click", event => {
        let $this = $(event.currentTarget);
        let modal = $this.parents('a')[0];
        let status = $this.data('status');
        let action = $(modal).data('answer');
        let survey_module = getModule();

        if (status !== 'True') {
            markComplete(survey_module, action).then(res => {
                if (res.success) {
                    $this.removeClass('btn-warning').addClass('btn-success');
                    $this.text('Complete');
                }
            });
        }

        event.stopPropagation();
        event.preventDefault();

    });

    $("#shortModal").on("show.bs.modal", event => {
        let target = $(event.relatedTarget);
        let answer = target.data('answer');
        let $modal_body = $(this).find('.modal-body');
        let $more_link = $(this).find('.more-link');
        let survey_module = getModule();

        getShortOutput(survey_module, answer).then(output => {
            $modal_body.text(output);
            $more_link[0].href = `/report/full/${survey_module}/${answer}`;
        });

    });
});