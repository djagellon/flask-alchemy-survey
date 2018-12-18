$(function() {

    async function toggleAction(module, answer, action) {
        let complete_url = `/api/reports/complete/${module}/${answer}/${action}`;
        let response = await fetch(complete_url);
        let data = await response.json();

        return data;
    }

    async function getOutput(module, type, label, action) {
        let output_url = `/api/reports/output/${type}/${label}/${action}`;
        let response = await fetch(output_url);
        let data = await response.json();

        return data;
    }

    async function getScore(module) {
        let output_url = `/api/reports/score/${module} `;
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

    function updateScore(survey_module) {
        let $score = $('.grade-badge');

        getScore(survey_module).then(res => {

            $score.removeClass(function(i, className) {
                return (className.match(/(^|\s)score-\S+/g) || []).join(' ')
            });

            $score.addClass('score-' + res.grade)

            $score.prop('Counter', $score.text()).animate({
                Counter: res.score
            }, {
                duration: 500,
                easing: 'swing',
                step: function (now) {
                    $score.text(now.toFixed(1));
                }
            });
        });
    }

    $("a.mark-complete").on("click", event => {
        let $this = $(event.currentTarget);
        let answer = $this.data('answer');
        let action = $this.data('action');
        let survey_module = getModule();

        toggleAction(survey_module, answer, action).then(res => {
            if (res.success) {
                toggleButtonClass($this, res.complete);
                updateScore(survey_module);
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
        let download = $target.data('download');
        let $this = $(event.currentTarget)
        let $modal_body = $this.find('.modal-body');
        let survey_module = getModule();

        $this.find('.action_title').text(type);

        if (download) {
            $this.find('.download-link a').show().attr('href', download);
        } else {
            $this.find('.download-link a').hide().attr('href', '');
        }

        getOutput(survey_module, type, answer, action).then(output => {
            $modal_body.text(output);
        });
    });

    $("#videoModal").on("show.bs.modal", event => {
        let action = $(event.relatedTarget).data('action');
        $(event.currentTarget).find('iframe').attr('src', action);
    });
});