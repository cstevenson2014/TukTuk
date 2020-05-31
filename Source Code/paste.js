//const { dialog } = require('electron').remote

function pasteVideoLink() {
    const videoURL = clipboard.readText()
  
    //  Check if the link is a valid video URL (works for both playlists and individual videos)
    if(ytpl.validateURL(videoURL)) {
      console.log('Oh wow, its a playlist! Ok, shifting into high gear...')

      dialog.showMessageBoxSync(null, { 
        type: 'info', 
        message: 'This is a playlist. TukTuk assumes you\'re downloading an album so cover art and album name will be retained as defaults for your convenience.'
      })

      //  OK, it's a playlist. Grab playlist array data and store in global var
      ytpl(videoURL, function(err, playlist) {
        if(err) throw err;
        //globalPlaylistArray = JSON.parse(playlist)
        globalPlaylistArray = playlist
        document.getElementById('btnPaste').value = 'Playlist Loaded'
        //console.log('First playlist video is at: ' + globalPlaylistArray['items'][0]['url_simple'])
        populateNextVideoToDownload()
      });
  
  
    }
    else {
      //  Check if the link is a valid video URL
      if (ytdl.validateURL(videoURL)) {
        console.log('Ok, its definitely a YouTube link...')
  
        ytdl.getInfo(videoURL, (err, info) => {
          if (err) throw err;

          // It's a valid youTube link, proceed

          console.log('title:', info.title);

          // Clear out old playlist info, in case any remains
          globalPlaylistArray = ''
          // Set this URL to the global URL variable
          globalVideoURL = videoURL
          // Let user know they've loaded a video, not a playlist. 
          document.getElementById('btnPaste').value = 'Video Loaded'
  
          // Parse title to extract artist and title information
  
          var splitTitle = info.title.split('-')
          var artist = splitTitle[0].trim()
          arrayOfTitleFluff.forEach(element => { artist = artist.replace(element, '') }); 
  
  
          // DEBUG #####################
          //console.log('Generating placeholder download queue')
          //addDownloadToQueue('LSDJFLKS', 'Get Lucky', 'Daft Punk', 'https://upload.wikimedia.org/wikipedia/en/a/a7/Random_Access_Memories.jpg')
  
  
          if(splitTitle[1] != null) {
            var title = splitTitle[1].trim()
            arrayOfTitleFluff.forEach(element => { title = title.replace(element, '') }); 
          }
          else { title = artist }
  
          title = title.trim()
          artist = artist.trim()
  
          if(title != '') { document.getElementById("textInputTitle").value = title }
          if(artist != '') { document.getElementById("textInputArtist").value = artist }
        });
      }
      else { 
        // Link didn't match video or playlist format
        dialog.showMessageBoxSync(null, { 
          type: 'error', 
          message: 'Invalid Link\n\nCopy a YouTube link to your clipboard, then click the "Paste Link" button.'
        })

      }
    }


  }