$(function() {

    async function toggleAction(module, action) {
        let complete_url = `/api/reports/complete/${module}/${action}`;
        let response = await fetch(complete_url);
        let data = await response.json();

        return data;
    }

    async function getOutput(module, type, label, action) {
        let output_url = `/api/reports/${type}/${label}/${action}`;
        let response = await fetch(output_url);
        let data = await response.json();

        return data;
    }

    function getModule() {
        let path = window.location.pathname;
        return path.split('/').slice(-1)[0];
    }

    function toggleButtonClass($button, mark) {
        if (mark) {
            $button.find('i')
                .removeClass('fas fa-square')
                .addClass('text-success fas fa-check-square');
            $button.find('.status_text').text('Succesfully completed');
        } else {
            $button.find('i')
                .removeClass('text-success fas fa-check-square')
                .addClass('far fa-square');
            $button.find('.status_text').text('Needs attention');
        }
    }

    $("a.mark-complete").on("click", event => {
        let $this = $(event.currentTarget);
        let modal = $this.parents('.panel')[0];
        let status = $this.data('status');
        let action = $this.data('answer');
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

    $("#outputModal").on("show.bs.modal", event => {
        let $target = $(event.relatedTarget);
        let action = $target.data('action');
        let answer = $target.data('answer');
        let type = $target.data('type');
        let $this = $(event.currentTarget)
        let $modal_body = $this.find('.modal-body');
        let survey_module = getModule();

        $this.find('.action_title').text(type);

        getOutput(survey_module, type, answer, action).then(output => {
            $modal_body.text(output);
        });
    });

    $("#videoModal").on("show.bs.modal", event => {
        let action = $(event.relatedTarget).data('action');
        $(event.currentTarget).find('iframe').attr('src', action);
    });
});