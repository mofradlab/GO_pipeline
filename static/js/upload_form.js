window.addEventListener( "load", function () {
    function sendData() {
      const XHR = new XMLHttpRequest();
      // Bind the FormData object and the form element
      const form = document.getElementById( "upload_form" )
      const FD = new FormData( form );
      $(".loader").show();

      // Define what happens on successful data submission
      XHR.addEventListener( "load", function(event) {
        $("#results").innerHTML = event.target.responseText; 
        $("#results").removeAttr("hidden"); 
        $(".loader").hide();
      } );
      
      // Define what happens in case of error
      XHR.addEventListener( "error", function( event ) {
        alert( 'Oops! Something went wrong.' );
      } );

      // Set up our request
      XHR.open( "POST", "/receive_upload_form" );
      // The data sent is what the user provided in the form
      XHR.send( FD );
    }
    
    // Access the form element...
    const form = document.getElementById( "upload_form" );
  
    // ...and take over its submit event.
    form.addEventListener( "submit", function ( event ) {
      event.preventDefault();

      
  
      sendData();
    } );
  } );