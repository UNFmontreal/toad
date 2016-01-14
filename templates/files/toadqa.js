
$( document ).ready( function() {

    $( '#nav' ).load( 'menu.html' );

    $( "#hide-versions-href" ).hide();

    if ( $( "applications" ).length == 0) {
        $( "#show-versions-href" ).hide();
        }
    else{
        var $lastApplicationTag = $("application:last");
        var $timestamp = $lastApplicationTag.attr("timestamp");
        var $formatTimestamp = $timestamp.substr(0,4)+"-"+$timestamp.substr(4,2)+"-"+$timestamp.substr(6,2)+" "+$timestamp.substr(8,2)+":"+$timestamp.substr(10,2);
        /*
        var $now = new Date();
        var $formatDateNow = $now.getFullYear()+"-"+("0" + ($now.getMonth() + 1)).slice(-2) + "-" +("0" + $now.getDate()).slice(-2) +" "+ $now.getHours() + ":" + $now.getMinutes();
        $("#timestamp").html("<strong>Toad launch at:</strong> "+$formatTimestamp+"<br /><strong>This task finish at: </strong>"+$formatDateNow);
        */
        $("#timestamp").html("<strong>Toad launch at:</strong> "+$formatTimestamp);
        $("versions").html($lastApplicationTag);
        $("versions").hide();
        $("#show-versions-href" ).show();
        }

    $("#show-versions-href" ).click(function( event ) {
        $("versions").show();
        $( this ).hide();
        $("#hide-versions-href" ).show();
        });

    $("#hide-versions-href" ).click(function( event ) {
        $("versions").hide();
        $("#show-versions-href" ).show();
        $(this).hide();
        });
    });
