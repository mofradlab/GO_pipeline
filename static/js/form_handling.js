document.getElementById('dataset_form').onsubmit = function(event) {
    event.preventDefault();
    var form_content_id = document.getElementById("form_content_id");
    var dataset_form = document.getElementById("dataset_form");
    //Construct form hash code and add to form. 
    var inputs = dataset_form.elements;
    form_string = "";
    // Iterate over the form controls
    for (i = 0; i < inputs.length; i++) {
        form_string = form_string + inputs[i].outerHTML;
    }
    string_hash = cyrb53(form_string);
    console.log("form hash", string_hash);
    form_content_id.value = string_hash;
    var form_entries = Object.fromEntries(new FormData(dataset_form));
    console.log("form entries", form_entries); 

    $.post("/~llp/flask/save_form", form_entries, function(data, status){
        window.open("/~llp/flask/loading_page/" + string_hash, '_blank');
      });
    return false; 
};


function get_results_path() {
    var dataset_form = document.getElementById("dataset_form");
    var inputs = dataset_form.elements;
    form_string = "";
    // Iterate over the form controls
    for (i = 0; i < inputs.length; i++) {
        form_string = form_string + inputs[i].outerHTML;
    }
    console.log(form_string);
    string_hash = cyrb53(form_string);
    console.log("string hash", string_hash);
    return '/~llp/flask/results/' + string_hash;
}

const cyrb53 = function(str, seed = 0) {
    let h1 = 0xdeadbeef ^ seed, h2 = 0x41c6ce57 ^ seed;
    for (let i = 0, ch; i < str.length; i++) {
        ch = str.charCodeAt(i);
        h1 = Math.imul(h1 ^ ch, 2654435761);
        h2 = Math.imul(h2 ^ ch, 1597334677);
    }
    h1 = Math.imul(h1 ^ (h1>>>16), 2246822507) ^ Math.imul(h2 ^ (h2>>>13), 3266489909);
    h2 = Math.imul(h2 ^ (h2>>>16), 2246822507) ^ Math.imul(h1 ^ (h1>>>13), 3266489909);
    return 4294967296 * (2097151 & h2) + (h1>>>0);
};

// document.getElementById("form_submit").addEventListener("click", generateFormCode);

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