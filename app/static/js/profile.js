$(function() {

    async function toggleAdmin(user) {
        let update_url = `/api/user/toggle_admin/${user}`;
        let response = await fetch(update_url);
        let data = await response.json();

        return data;
    }

    $("#toggle_admin_user").on("click", event => {
        let user = $(event.currentTarget).data('user');

        toggleAdmin(user).then(output => {
            location.reload();
        });

    });
});