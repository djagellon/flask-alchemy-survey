$(function() {

    async function toggleAction(module, action) {
        let complete_url = `/api/reports/complete/${module}/${action}`;
        let response = await fetch(complete_url);
        let data = await response.json();

        return data;
    }

    function getModule() {
        let path = window.location.pathname;
        return path.split('/').slice(-1)[0];
    }

    function toggleButtonClass($button, mark) {
        if (mark) {
            $button.removeClass('btn-warning')
            .addClass('btn-success').text('Complete');
        } else {
            $button.removeClass('btn-success')
            .addClass('btn-warning').text('Inomplete');
        }
    }

    $("button.mark-complete").on("click", event => {
        let $this = $(event.currentTarget);
        let modal = $this.parents('.panel')[0];
        let status = $this.data('status');
        let action = $(modal).data('answer');
        let survey_module = getModule();

        toggleAction(survey_module, action).then(res => {
            if (res.success) {
                toggleButtonClass($this, res.complete);
            } else {
                throw res.error;
            }
        }).catch(err => {
            alert('Ooops! Something went wrong: ' + err)
        });

        event.stopPropagation();
        event.preventDefault();

    });

});