<head>
    <title>Media DB</title>

    <script type="text/javascript" src="/js/jquery-1.5.1.min.js" />
    <script type="text/javascript" src="/js/uploadify/swfobject.js"></script>
    <script type="text/javascript" src="/js/uploadify/jquery.uploadify.v2.1.0.min.js"></script>

  </head>
  <body>
      <center>

      <script type="text/javascript">


        function display_search_images(data)
        {
            $('tbody', '#search_keyword_images').html('')
            for (index = 0; index < data.images.length; index++)
                {
                    var new_row =
                     "<tr><td>"+ data.images[index].id +"</td>" +
                     "<td><img src='/get_image_thumbnail_source?image_id="+ data.images[index].id +"' /></td>" +
                     "<td>"+ data.images[index].filename +"</td>" +
                     "<td>"+ data.images[index].title +"</td>" +
                     "<td>"+ data.images[index].description +"</td>" +
                     "<td><a href='/get_image_source?image_id=" + data.images[index].id + "'>download</a></td></tr>"
                    $('tbody', '#search_keyword_images').append(new_row)
                }
        }

        function display_search_videos(data)
        {
            $('tbody', '#search_keyword_videos').html('');
            if (data.videos != undefined)
            {                
                for (index = 0; index < data.videos.length; index++)
                 {
                    var new_row = "<tr><td>" + data.videos[index].id + "</td>" +
                                  "<td>" + data.videos[index].filename + "</td>" +
                                  "<td>" + data.videos[index].length + "s</td>" +
                                  "<td>" + data.videos[index].codec + "</td>" +
                                  "<td><a href='/get_video_source?video_id=" + data.videos[index].id + "'>download</a></td></tr>"
                    $('tbody', '#search_keyword_videos').append(new_row);


                 }
            }

        }
        

        function search_keywords()
        {            
            var jqxhr = $.get("/search_by_keyword?keyword=" + $('#keyword').val(),
                function(data)
                {
                    if (data.exception != undefined)
                        alert(data.exception);
                    else
                    {
                        if (data.images.length == 0 && data.videos.length == 0)
                        {
                            alert("Nothing found!");
                        }
                        else
                        {                                                                                    
                            display_search_videos(data);
                            display_search_images(data);                            
                        }

                    }
                });
        }


      </script>

    <table>
        <tr><td>
          <form id="file_upload_form" method="post" action="/search_by_keyword_image" enctype="multipart/form-data">
          Keywords <input type="text" name="keyword" id="keyword" />
          Max Edit Dist <input type="text" name="max_edit_distance"  size="2"/>
         </td>

         <td><input type="range" /></td>

         <td>

        Image: <input type="file" name="source" />
        <input type="submit" value="search" />
        </form>
        <iframe id="upload_target" name="upload_target" src="" style="display:none;"></iframe>      

      </td></tr>
    </table>

      <script type="text/javascript">
        function init() {
                document.getElementById('file_upload_form').onsubmit=function() {
                    document.getElementById('file_upload_form').target = 'upload_target'; //'upload_target' is the name of the iframe
                }
            }
            window.onload=init;

            $("#upload_target").load(function (){
                    var retval = $(frames['upload_target'].document).text();
                    if (retval != null)
                    {
                        try
                        {
                            var obj = jQuery.parseJSON(retval);
                            display_search_videos(obj);
                            display_search_images(obj);
                                
                        }catch(err){}
                    }
            });
        </script>
      <br><br>

      <table id="search_keyword_images" width="500px">
        <caption>Search Results Images</caption>
        <tbody></tbody>
      </table>

      <br><br>

          <table id="search_keyword_videos" width="500px">
              <caption>Search Results Videos</caption>
              <tbody></tbody>
          </table>

       <br><br>

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
             