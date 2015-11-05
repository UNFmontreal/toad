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
                <h1>
                    <a href="index.html"><img src="./images/qa_logo.png"></a>
                </h1>
                <h2>Subject : $subject</h2>
                <div id="timestamp"></div>
            </div>
            <div id="menu">
                <object type="text/html" data="menu.html"></object>
            </div>
        </header>

        <h1>$taskInfo</h1>

        <section id="results">
$parseHtmlTables
        </section>

        <a href="#" id="show-versions-href">Show Software Versions</a>
        <a href="#" id="hide-versions-href">Hide Software Versions</a>

        <versions></versions>

        <div id="dataVersions">
$parseVersionTables
        </div>


        <footer></footer>
    </body>
</html>
<script type = "text/javascript">
    var $lastTimestamp = $("application:last");
    var $timestamp = $lastTimestamp.attr("timestamp");
    var $date = new Date();
    var $currentdate = $date.getFullYear()+"-"+("0" + ($date.getMonth() + 1)).slice(-2) + "-" +("0" + $date.getDate()).slice(-2) +" "+ $date.getHours() + ":" + $date.getMinutes();
    $("#dataVersions").hide();
    $("versions").html($lastTimestamp);
    $("versions").hide();
    $("#hide-versions-href" ).hide()

    if ( $( "applications" ).length == 0) {
        $( "#show-versions-href" ).hide();
    }
    else{
        $("#timestamp").html("<strong>Toad launch at:</strong> "+$timestamp.substr(0,4)+"-"+$timestamp.substr(4,2)+"-"+$timestamp.substr(6,2)+" "+$timestamp.substr(8,2)+":"+$timestamp.substr(10,2)+"<br /><strong>This task finish at: </strong>"+$currentdate);
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