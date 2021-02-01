$(document).ready(function () {
    getDataset();
});

function getDataset(){
    var url = window.location.href;
    console.log(url); 
    var res = url.split("/");
    var form_hash = res[res.length - 1]; 

    console.log("sending post request for form", form_hash);
    
    $.post("/~llp/flask/server", form_hash, function() {
        console.log($("#results_link"));
        $("#results_link")[0].href = "/~llp/flask/results/" + form_hash; 
        $("#download_link")[0].href = "/~llp/flask/file_download/" + form_hash; 
        console.log($("#results_links")); 
        $("#results_links").removeAttr("hidden"); 
        $(".loader").hide();
      });
}