console.log("doing stuff")
// document.getElementById("file_submit_button").addEventListener("click", sendSequence);

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