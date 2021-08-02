document.getElementById('dataset_form').onsubmit = function(event) {
    event.preventDefault();
    var form_content_id = document.getElementById("form_content_id");
    form_content_id.value = "UNINITIALIZED";
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
    var save_form_url = document.getElementById("form_submission_link").getAttribute("href"); 
    var loading_page_url = document.getElementById("loading_page_link").getAttribute("href"); 
    $.post(save_form_url, form_entries, function(data, status){
        window.open(loading_page_url + string_hash, '_blank');
      });
    return false; 
};

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