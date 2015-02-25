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
        </style>
        <script type="text/javascript" language="javascript" src="qa.js"></script>
        <title>TOAD-Qa</title>
    </head>

    <body>
        <header>
            <div id="logo_titre">
                <img src="frog3.png" alt="Toad logo" id="logo"/>
                <h1>Toad-Qa</h1>
            </div>
            <nav>
                <ul>
                    <li><input type="button" id="preparation" value="preparation" onClick="preparation();" /></li>
                    <li><input type="button" id="parcellation" value="parcellation" onClick="parcellation();" /></li>
                    <li><input type="button" id="eddy" value="eddy" onClick="eddy();" /></li>
                    <li><input type="button" id="denoising" value="denoising" onClick="denoising();" /></li>
                    <li><input type="button" id="preprocessing" value="preprocessing" onClick="preprocessing();" /></li>
                </ul>
            </nav>
        </header>
        
        <section id="results">
        </section>
        
        <footer>
            <!--
            <img src="Thalamus.png" alt="Image not found" onError="this.onerror=null;this.src='Thalamus2.png';" />
            Logo made by <a href="http://www.freepik.com" title="Freepik">Freepik</a> from <a href="http://www.flaticon.com" title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0">CC BY 3.0</a>
            -->
        </footer>
    </body>
</html>
