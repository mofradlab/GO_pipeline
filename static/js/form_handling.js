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
    loading_page_url = loading_page_url + string_hash; 
    $.post(save_form_url, form_entries, function(data, status){
        var download_page_link = document.getElementById("download_page_link"); 
        download_page_link.href = loading_page_url; 
        $("#download_section").removeAttr("hidden"); 
        window.open(loading_page_url, '_blank');
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

// ('EXP', 'IDA', 'IPI', 'IMP', 'IGI', 'IEP', 'TAS', 'IC')
// ('EXP', 'IDA', 'IPI', 'IMP', 'IGI', 'IEP', 'TAS', 'IC', 'HTP', 'HDA', 'HMP', 'HGI', 'HEP', 'IBA', 'IBD', 'IKR', 'IRD', 'ISS', 'ISO', 'ISA', 'ISM', 'IGC', 'RCA')
// ('ISO', 'IGI', 'ISA', 'IGC', 'IEP', 'RCA', 'HTP', 'HDA', 'HGI', 'IKR', 'TAS', 'HEP', 'ND', 'IBA', 'IBD', 'IMP', 'EXP', 'IDA', 'IC', 'ISM', 'ISS', 'NAS', 'IRD', 'IEA', 'IPI', 'HMP')



window.addEventListener( "load", function () {

    // Access the form element...
    var preset_exp = document.getElementById( "preset_exp" );
    var preset_niea = document.getElementById( "preset_niea" );
    var preset_all = document.getElementById( "preset_all" );
    var preset_elements = [preset_exp, preset_niea, preset_all];
    var preset_selections = [['EXP', 'IDA', 'IPI', 'IMP', 'IGI', 'IEP', 'TAS', 'IC'],
    ['EXP', 'IDA', 'IPI', 'IMP', 'IGI', 'IEP', 'TAS', 'IC', 'HTP', 'HDA', 'HMP', 'HGI', 
    'HEP', 'IBA', 'IBD', 'IKR', 'IRD', 'ISS', 'ISO', 'ISA', 'ISM', 'IGC', 'RCA'],
    ['ISO', 'IGI', 'ISA', 'IGC', 'IEP', 'RCA', 'HTP', 'HDA', 'HGI', 'IKR', 'TAS', 
    'HEP', 'ND', 'IBA', 'IBD', 'IMP', 'EXP', 'IDA', 'IC', 'ISM', 
    'ISS', 'NAS', 'IRD', 'IEA', 'IPI', 'HMP']];

    var checkbox_elements = document.getElementsByClassName("e_code");
    var checkbox_map = {};
    for (var i = 0; i < checkbox_elements.length; i++) {
        checkbox_map[checkbox_elements[i].id] = checkbox_elements[i]; 
    }

    function update_checkboxes() {
        for (var i = 0; i < checkbox_elements.length; i++) {
            checkbox_elements[i].checked = false; 
        }
        for (var i = preset_elements.length-1; i >= 0; i--) {
            if(preset_elements[i].checked) {
                to_check = preset_selections[i]; 
                for (var i = 0; i < to_check.length; i++) {
                    var check_id = to_check[i]; 
                    checkbox_map[check_id].checked = true; 
                }
                break; 
            }
        }
    }

    for (var i = 0; i < preset_elements.length; i++) {
        preset_elements[i].addEventListener('change', update_checkboxes); 
    }        
} );