<html>
  <head>
    <title>Media DB</title>

    <script type="text/javascript" src="/js/jquery-1.5.1.min.js" />
    <script type="text/javascript" src="/js/uploadify/swfobject.js"></script>
    <script type="text/javascript" src="/js/uploadify/jquery.uploadify.v2.1.0.min.js"></script>

  </head>
  <body>
      <center>
      <form method="post" action="/add_image" enctype="multipart/form-data">
          <table>
              <caption>Upload Image</caption>
              <tbody>
                  <tr><td>Image Title</td><td><input type="text" name="title" /></td></tr>
                  <tr><td>Image Description</td><td><textarea name="description" rows="10" cols="20"></textarea></td></tr>
                  <tr><td>Image</td><td><input type="file" name="source" /></td></tr>
                  <tr><td></td><td><input type="submit" value="upload" /></td>
              </tbody>
          </table>
      </form>

           <br><br>
      <form method="post" action="/add_video" enctype="multipart/form-data">
          <table>
              <caption>Upload Video</caption>
                <tr><td>Video Title</td><td><input type="text" /></td></tr>
                <tr><td>Video Description</td><td><textarea name="description" rows="10" cols="20"></textarea></td></tr>
                <tr><td>Video</td><td><input type="file" name="source" /></td></tr>
                <tr><td></td><td><input type="submit" value="upload" /></td>
          </table>
      </form>


        <br><br>
      <table>          
        <caption>Images</caption>
        <thead><tr><td>id</td><td>thumbnail</td><td>filename</td><td>title</td><td>description</td><td>dimension</td><td>format</td></tr></thead>
        %for image in context['images']:
        <tr><td>{{image.id}}</td><td><img src="/get_image_thumbnail_source?image_id={{image.id}}"</td><td>{{image.filename}}</td>
            <td>{{image.title}}</td><td>{{image.description}}</td><td>({{image.width}}, {{image.height}})</td>
            <td>{{image.format}}</td><td><a href="/get_image_source?image_id={{image.id}}">download</a></td></tr>
        %end
      </table>



      </center>
  </body>
</html>
