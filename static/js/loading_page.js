$(document).ready(function () {
	setTimeout(function(){getDataset();}, 1500);
});

function getDataset(){
    var url = window.location.href;
    console.log(url); 
    var res = url.split("/");
    var form_hash = res[res.length - 1]; 

    console.log("sending post request for form", form_hash);
    var server_url = document.getElementById("query_link").getAttribute("href"); 
    var results_url = document.getElementById("results_link").getAttribute("href"); 
    var download_url = document.getElementById("download_link").getAttribute("href"); 
    $.post(server_url, form_hash, function() {
        console.log($("#results_link"));
        $("#results_link")[0].href = results_url + form_hash; 
        $("#download_link")[0].href = download_url + form_hash; 
        console.log($("#results_links")); 
        $("#results_links").removeAttr("hidden"); 
        $(".loader").hide();
      });
}
