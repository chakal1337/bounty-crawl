<?php
 $db = new mysqli("localhost", "root", "root", "bountycrawl");
?>
<!DOCTYPE html>
<html>
<head>
 <title>BountyCrawl</title>
 <meta name="viewport" content="width=device-width, initial-scale=1">
 <script src="https://code.jquery.com/jquery-3.6.1.js"></script> 
 <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>
 <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">
 <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.1/css/jquery.dataTables.css"> 
 <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.13.1/js/jquery.dataTables.js"></script>
</head>
<body>
<div class="container">
 <div class="my-5">
 <form method="post" action="">
  <input type="text" name="search" placeholder="search term">
  <input type="submit" name="submit" value="Search">
  <input type="submit" name="submit" value="Extended Search">
 </form>
 </div>
<div class="my-5">
<?php
 if(isset($_POST['search']) && isset($_POST['submit']) && $_POST['submit'] == "Search") {
  $search = $db->real_escape_string($_POST['search']);
  $res = $db->query("select * from urls where url like '%{$search}%' order by rand() limit 200");
  if($res->num_rows) {
   echo("<table id='mytable' class='display'><thead><tr><th>url</th></tr></thead><tbody>");
   while($r = $res->fetch_object()) {
    $r->url = htmlentities($r->url);
    print("<tr><td>{$r->url}</td></tr>");
   }
   echo("</tbody></table>");
  }
 } else if(isset($_POST['search']) && isset($_POST['submit'])) {
  $search = $db->real_escape_string($_POST['search']);
  $res = $db->query("select * from urls left join domains on domains.id=urls.did where url like '%{$search}%' order by rand() limit 200");
  if($res->num_rows) {
   echo("<table id='mytable' class='display'><thead><tr>");
   print("<th>url</th><th>program</th>");
   print("<th>domain</th><th>last seen</th>");
   print("</tr><thead><tbody>");
   while($r = $res->fetch_object()) {
    $r->url = htmlentities($r->url);
    $r->program = htmlentities($r->program);
    $r->lastseen = htmlentities($r->lastseen);
    $r-
    print("<tr>");
    print("<td>{$r->url}</td><td>{$r->program}</td>");
    print("<td>{$r->name}</td><td>{$r->lastseen}</td>");
    print("</tr>");
   }
   echo("</tbody></table>");
  }
 }
?>
</div>
</div>
<script>
 $(document).ready( function () {
  $('#mytable').DataTable();
 } );
</script>
</body>
</html>
