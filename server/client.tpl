<html>
  <head>
    <title>Media DB</title>

    <script type="text/javascript" src="/js/jquery-1.5.1.min.js" />
    <script type="text/javascript" src="/js/uploadify/swfobject.js"></script>
    <script type="text/javascript" src="/js/uploadify/jquery.uploadify.v2.1.0.min.js"></script>

  </head>
  <body>
      <center>

      <form method="get" action="/search_by_keyword" />
        <input type="text" name="keyword" />
        <input type="submit" value="search" />
      </form>

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
        <thead><tr><td>id</td><td>thumbnail</td><td>filename</td><td>title</td><td>description</td><td>dimension</td><td>format</td><td>download</td></tr></thead>
        <tbody>
        %for image in context['images']:
        <tr><td>{{image.id}}</td><td><img src="/get_image_thumbnail_source?image_id={{image.id}}"</td><td>{{image.filename}}</td>
            <td>{{image.title}}</td><td>{{image.description}}</td><td>({{image.width}}, {{image.height}})</td>
            <td>{{image.format}}</td><td><a href="/get_image_source?image_id={{image.id}}">download</a></td></tr>
        %end
        </tbody>
      </table>

      <br><br>
      <table>
          <caption>Videos</caption>
          <thead><tr><td>id</td><td>filename</td><td>length</td><td>dimensions</td><td>fps</td><td>format</td><td>codec</td><td>download</td></tr></thead>
          <tbody>
           %for video in context['videos']:
            <tr><td>{{video.id}}</td><td>{{video.filename}}</td><td>{{video.length}}</td>
                <td>({{video.width}}, {{video.height}})</td><td>{{video.fps}}</td><td>{{video.format}}</td>
                <td>{{video.codec}}</td><td><a href="/get_video_source?video_id={{video.id}}">download</a></td></tr>
            %end
          </tbody>
      </table>


      </center>
  </body>
</html>
