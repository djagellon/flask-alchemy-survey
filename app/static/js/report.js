$(function() {
    console.log("report.js has loaded : ")

    var path = this.location.pathname.split('/')
    var module = path[path.length -1]

    $('#dt').DataTable( {
        ajax: {
            url: 'http://localhost:5000/api/report/' + module,
            dataSrc: ''
        },
        columns: [
            { data: 'label' },
            { data: 'output.question' },
            { data: 'answer' },
            { data: 'output.short'},
            { data: 'output.action'},
            { data: 'id', visible: false}
        ],
        paging: false,
        order: [[0, "asc"]],
        // ordering: false,
        
    } );

    // fetch('http://localhost:5000/api/report/all').then( x => {
    //     console.log("X: ", x.text());
    //     return x;
    // });
});