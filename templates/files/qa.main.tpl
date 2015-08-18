<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <style>
            body{
                background-color:#C7D3DC;
                color:#252525;
                font-family:Arial, Helvetica, sans-serif;
                text-align: center;}
            nav li{
                display: inline-block;
                margin-right: 15px;}
            table{
                background-color:white;
                text-align:center;
                margin-left:auto;
                margin-right:auto;}
            .large_view{
                width:80vw;}
        </style>
        <title>TOAD-Qa</title>
    </head>

    <body>
        <header>
            <div id="logo_titre">
                <a href="index.html"><h1>Toad-Qa</h1></a>
                <h2>Subject : $subject</h2>
            </div>
            <nav>
                <ul>
                    $menuHtml
                </ul>
            </nav>
        </header>
        <h1>$taskInfo</h1>
        <section id="results">
$parseHtmlTables
        </section>

        <footer></footer>
    </body>
</html>
