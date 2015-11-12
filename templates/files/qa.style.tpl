
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

object{width:80vw;}

/*version.xml*/
toad {padding:10px;}

application {
    display:table;
    padding:5px;
    margin: 0px auto;

}

software {display: table-row; }

name {
    display:inline-block;
    font-weight:bold;
    display: table-cell;
    text-align:right;
}

name:after {
             content: ":";
}


hostname:before {
content: "hostname: ";
        font-weight:bold;
}

toadname:before {
content: "toadname: ";
        font-weight:bold;
}

uname:before {
content: "uname: ";
        font-weight:bold;
}


hostname:after {
    display:block;
        content: "";

}

toadname:after {
    display:block;
        content: "";

}

uname:after {
    display:block;
        content: "";

}

version {
      padding:5px;
      display: table-cell;
      text-align:left;
}

server {
        border: 1px solid;
        margin: 0px auto;
        display: table;
        align: left;
        text-align: left;
        margin-top: 15px;

}
softwares {
        margin: 0px auto;
        display: table;
        align: center;
        margin-top: 15px;
}
