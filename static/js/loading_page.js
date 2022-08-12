$(document).ready(
  function () {
	setTimeout(
    function(){
      getDataset();
      setTimeout(checkDataset, 1500); 
    }, 1500);
});

/*
- Start data processing. 
- Periodically query results.
- If failed, display failure. 
- If successful, produce download links. 
*/

function getDataset(){
    var url = window.location.href;
    var res = url.split("/");
    var form_hash = res[res.length - 1]; 
    console.log("sending post request for form", form_hash);
    var server_url = document.getElementById("query_link").getAttribute("href"); 
    $.post(server_url, form_hash);
}

function updateLinks(form_hash) {
    console.log($("#results_link"));
    var results_url = document.getElementById("results_link").getAttribute("href"); 
    var download_url = document.getElementById("download_link").getAttribute("href"); 
    $("#results_link")[0].href = results_url + form_hash; 
    $("#download_link")[0].href = download_url + form_hash; 
    console.log($("#results_links")); 
    $("#results_links").removeAttr("hidden"); 
    $(".loader").hide();
}

function checkDataset() {
    var url = window.location.href;
    var res = url.split("/");
    var form_hash = res[res.length - 1]; 
    console.log("checking progress on", form_hash);
    var server_url = document.getElementById("query_link").getAttribute("href"); 

    $.post(server_url+'_check', form_hash, function(data, status) {
      console.log("recieved", data, status);
      if(status === "error" || status === "timeout" || data === "JOB FAILED") {
        console.log("Generation failed.");
      } else if (data === "DATA PROCESSING") {
        console.log("Data still processing. Trying again in 10s");
        setTimeout(checkDataset, 10000);
      } else if (data == "DATA READY"){
        console.log("Data is prepared");
        updateLinks(form_hash); 
      }
    });
}; 
