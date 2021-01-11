document.getElementById('dataset_form').onsubmit = function() {
    var form_content_id = document.getElementById("form_content_id");
    console.log(form_content_id.value);
    
    console.log("form content id", form_content_id.value);
    var dataset_form = document.getElementById("dataset_form");
    var inputs = document.getElementById("dataset_form").elements;
    form_string = ""
    // Iterate over the form controls
    for (i = 0; i < inputs.length; i++) {
        form_string = form_string + inputs[i].outerHTML
    }
    console.log(form_string);
    string_hash = cyrb53(form_string)
    console.log("string hash", string_hash)
    form_content_id.value = string_hash;
};

  function get_results_path() {
    var dataset_form = document.getElementById("dataset_form");
    var inputs = document.getElementById("dataset_form").elements;
    form_string = ""
    // Iterate over the form controls
    for (i = 0; i < inputs.length; i++) {
        form_string = form_string + inputs[i].outerHTML
    }
    console.log(form_string);
    string_hash = cyrb53(form_string)
    console.log("string hash", string_hash)
    return '/results/' + string_hash
}

// document.getElementById("form_submit").addEventListener("click", generateFormCode);


// function generateFormCode() {

// }

// document.getElementById("sequence_submit_button").addEventListener("click", function() {
//     var xhttp = new XMLHttpRequest();
//     document.getElementById("sequence_submit_button").value = "Sent Request";
//     xhttp.onreadystatechange = function() {
//         if (this.readyState == 4 && this.status == 200) {
//           document.getElementById("sequence_input").value = this.responseText;
//         }
//       };
//       xhttp.open("GET", "https://www.ocf.berkeley.edu/~llp/flask/", true);
//       xhttp.send();
//   });

// function sendSequence(sequence) {
//     var xhr = new XMLHttpRequest();
//     xhr.open("POST", 'https://www.ocf.berkeley.edu/~llp/flask/', true);

//     //Send the proper header information along with the request
//     xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

//     xhr.onreadystatechange = function() { // Call a function when the state changes.
//         if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
//             document.getElementById("file_submit_button").value = this.responseText;
//         }
//     }
//     console.log(xhr); 
//     xhr.send("foo=bar&lorem=ipsum");
// }