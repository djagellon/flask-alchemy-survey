$(function() {

    async function getShortOutput(modal, label) {
        let output_url = `/api/report/short/${modal}/${label}`;
        let response = await fetch(output_url);
        let data = await response.json();

        return data;
    }

    $("#shortModal").on("show.bs.modal", event => {
        let target = $(event.relatedTarget);
        let answer = target.data('answer');
        let $modal_body = $(this).find('.modal-body');
        let $more_link = $(this).find('.more-link');

        getShortOutput('asset', answer).then(output => {
            $modal_body.text(output);
            $more_link[0].href = `/report/full/asset/${answer}`;
        });

    });
});