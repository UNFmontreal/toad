<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <link rel="stylesheet" type="text/css" href="style.css">
    <script src ="jquery.js"></script>
    <title>TOAD-Qa</title>
  </head>

  <body>
    <header>
      <div id="title">
         <div id="title">
           <a href="index.html" class="logo">
             <img src="./images/qa_logo.png" class="logo">
           </a>
          
          <h2>Subject : $subject</h2>
            <div id="timestamp"></div>
          </div>
          
          <div id="navwrap">
            <div id="nav">
              TOAD MENU
            </div>
          </div>
    </header>
    <div id="wrapper">  
      <h1>$taskname</h1>
     
      <div class='taskInfo'>$taskInfo</div>

      <section id="results">
        $parseHtmlTables
      </section>

      <a href="#" id="show-versions-href">Show Software Versions</a>
      <a href="#" id="hide-versions-href">Hide Software Versions</a>

      <versions></versions>

      <div hidden id="dataVersions">
	    $parseVersionTables
      </div>

   </div>

    <footer></footer>
  </body>
</html>
<script type = "text/javascript">
	$( document ).ready( function() {
        $( '#nav' ).load( 'menu.html' );
    });
           
    $( "#hide-versions-href" ).hide();

    if ( $( "applications" ).length == 0) {
        $( "#show-versions-href" ).hide();
    }
    else{
        var $lastApplicationTag = $("application:last");
        var $timestamp = $lastApplicationTag.attr("timestamp");
        var $now = new Date();
        var $formatTimestamp = $timestamp.substr(0,4)+"-"+$timestamp.substr(4,2)+"-"+$timestamp.substr(6,2)+" "+$timestamp.substr(8,2)+":"+$timestamp.substr(10,2);
        var $formatDateNow = $now.getFullYear()+"-"+("0" + ($now.getMonth() + 1)).slice(-2) + "-" +("0" + $now.getDate()).slice(-2) +" "+ $now.getHours() + ":" + $now.getMinutes();
        $("#timestamp").html("<strong>Toad launch at:</strong> "+$formatTimestamp+"<br /><strong>This task finish at: </strong>"+$formatDateNow);
        $("versions").html($lastApplicationTag);
        $("versions").hide();
        $("#show-versions-href" ).show()

    }
    $("#show-versions-href" ).click(function( event ) {
      $("versions").show();
      $( this ).hide();
      $("#hide-versions-href" ).show()
    });

    $("#hide-versions-href" ).click(function( event ) {
      $("versions").hide();
      $("#show-versions-href" ).show()
      $(this).hide()
    });
</script>
