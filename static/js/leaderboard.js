window.addEventListener( "load", function () {
    

    table_params = {"namespace": "molecular_function", "testing_set": "cluster50",
                     "testing_quality":"exp", "page_num":0, 
                     "page_len":10, "sort_col":"max_f1", "desc":"desc"}; 

    var table = document.getElementById("leaderboard_table").getElementsByTagName("TABLE")[0];
    var table_headers = table.rows[0].getElementsByTagName("TH");

    function boldElement(weight, event) {
        event.srcElement.style.fontWeight = weight; 
    }
    function change_table_col(column) {
        table = document.getElementById("leaderboard_table").getElementsByTagName("TABLE")[0];
        col_cell1 = table.rows[0].getElementsByClassName(table_params["sort_col"])[0];
        col_cell1.innerHTML = col_cell1.innerHTML.split(/[\u25B2\u25BC]/i)[0];
        col_cell2 = table.rows[0].getElementsByClassName(column)[0];
        col_cell2.innerHTML = col_cell2.innerHTML.split(/[\u25B2\u25BC]/i)[0]; 

        table_params["sort_col"] = column
        if(table_params["desc"] === "desc") {
            table_params["desc"] = "asc"; 
            col_cell2.innerHTML = col_cell2.innerHTML + " \u25B2";
        } else {
            table_params["desc"] = "desc";
            col_cell2.innerHTML = col_cell2.innerHTML + " \u25BC";
        }
        table = document.getElementById("leaderboard_table").getElementsByTagName("TABLE")[0];
        col_cell = table.rows[0].getElementsByClassName(column);
    }

    function update_table(update_func, event) {
        update_func(); 
        //console.log("new table params", table_params); 
        $.post("/leaderboard_table", table_params, function(data, status){
                //console.log(data); 
                table =document.getElementById("leaderboard_table").getElementsByTagName("TABLE")[0];
                updated_table = $.parseHTML(data)[0].getElementsByTagName("TABLE")[0];
                header_row = table.rows[0];
                updated_table.rows[0].parentNode.replaceChild(header_row, updated_table.rows[0]); 
                table.parentNode.replaceChild(updated_table, table); 
          });
    }
    for (var i = 0; i < table_headers.length; i++) {
        header = table_headers[i]; 
        console.log("header" + header.innerHTML.toLowerCase()); 
        header.addEventListener("click", update_table.bind(null, change_table_col.bind(null, header.className.toLowerCase())));
        //header.addEventListener("mouseover", boldElement.bind(null, 900));
    }
    update_table(x=>0, null); 

    // Access the form element...
    var ns_selector = document.getElementById( "namespace" );
    var ts_selector = document.getElementById( "testing_set" );
    var tq_selector = document.getElementById( "testing_quality" );
    var lb_submit = document.getElementById( "lb_submit" );

    function update_test_set(event) {
        table_params["namespace"] = ns_selector.value;
        table_params["testing_set"] = ts_selector.value;
        table_params["testing_quality"] = tq_selector.value;
    }
        
    lb_submit.addEventListener("click", update_table.bind(null, update_test_set)); 
} );