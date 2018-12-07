$(function() {

    async function updatePreference() {
        let update_url = `/api/user/toggle_pref/admin_controls`;
        let response = await fetch(update_url);
        let data = await response.json();

        return data;
    }

    $("#toggle_admin_controls").on("click", event => {
        updatePreference().then(output => {
            location.reload();
        });

    });
});