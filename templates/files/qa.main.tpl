<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <link rel="stylesheet" type="text/css" href="style.css">
    <script src="$jqueryFile"></script>
    <script src="toadqa.js"></script>
    <title>TOAD-Qa</title>
  </head>

  <body>
    <header>
      <div id="title">

        <a href="index.html" class="logo">
          <img src="./images/qa/qa_logo.png" class="logo">
        </a>

        <div id="titleTask">$taskName / $subject</div>

      </div>

      <div id="navwrap">
        <div id="nav">
          TOAD MENU
        </div>
      </div>
    </header>

    <div id="wrapper">
      <h1>$taskName</h1>
    
        <div id="timestamp"></div>
     
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
