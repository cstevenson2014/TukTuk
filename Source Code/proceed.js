

function downloadVideoToAudio(videoURL, expectedFileSizeKB, title, artist, album, coverURL, tempID){

  let stream = ytdl(videoURL, { quality: 'highestaudio' });

  ffmpeg(stream)
    .audioBitrate(128)
    .save('./tmp/' + tempID + '/songFile.mp3')
    .on('progress', p => {
      if(p.targetSize < expectedFileSizeKB) { 
        var ratio = p.targetSize / expectedFileSizeKB * 100;
        console.log(tempID + ' - ' + ratio + '% complete' )
        reportProgress(tempID, ratio)
      }
      else { reportProgress(tempID, -1)}
    })
    .on('end', () => {
      console.log(tempID + ' - ' +'Video downloaded to an audio file');
      tagSong('./tmp/' + tempID + '/songFile.mp3', './tmp/' + tempID + '/' + artist + ' - ' + title + '.mp3', title, artist, album, coverURL, tempID)
      reportProgress(tempID, -1)
    }
  );
}

function tagSong(sourcePath, destinationPath, title, artist, album, coverURL, tempID){

  const songBuffer = fs.readFileSync(sourcePath);
  var coverBuffer = ''

  if(coverURL != null){ 
    const download = (url, path, callback) => {
      request.head(url, (err, res, body) => {
        request(url)
          .pipe(fs.createWriteStream(path))
          .on('close', callback)
      })
    }
    
    download(coverURL, './tmp/' + tempID + '/cover.' + coverURL.slice(coverURL.length - 3), () => {
      console.log(tempID + ' - ' +'Done!')
      const coverBuffer = fs.readFileSync( './tmp/' + tempID + '/cover.' + coverURL.slice(coverURL.length - 3));
      tagSongWithMetaData(title, artist, album, true, coverBuffer, songBuffer, destinationPath, tempID)
    })
  }
  else {
    tagSongWithMetaData(title, artist, album, false, null, songBuffer, destinationPath, tempID)
  }

}

function tagSongWithMetaData(title, artist, album, useArt, coverArtBuffer, songFileBuffer, destinationFilePath, tempID) {
  console.log(tempID + ' - ' + 'Tagging: ' + title + ' | ' + artist + ' | ' + album + ' Art: ' + useArt)
  const writer = new ID3Writer(songFileBuffer);

  writer.setFrame('TIT2', title)
        .setFrame('TPE1', [artist])
        .setFrame('TALB', album);
        if(useArt){ writer.setFrame('APIC', { type: 3, data: coverArtBuffer, description: 'Cover Art' }); }
  writer.addTag();
  const taggedSongBuffer = Buffer.from(writer.arrayBuffer);
  fs.writeFileSync(destinationFilePath, taggedSongBuffer);
  fs.rename(destinationFilePath, globalOutputDirectory + '/' + title + ' - ' + artist + '.mp3', () => {
    console.log(tempID + ' - ' + 'Song tagged and moved to output')
    removeDownloadFromQueue(tempID)
  })
  

}



function proceedWithOneSong() {

  var videoURL = globalVideoURL
  var title = document.getElementById("textInputTitle").value;
  var artist = document.getElementById("textInputArtist").value;
  var album = document.getElementById("textInputAlbum").value;
  var coverURL = document.getElementById('coverArt').src;
  var tempID = generateID(10);

  if (!fs.existsSync(String(globalOutputDirectory))) {
    dialog.showMessageBoxSync(null, { 
      type: 'error', 
      message: 'Set an output folder before proceeding'
    })
    return 1
  }

  ytdl.getInfo(videoURL, (err, info) => {
    if (err) throw err;
    
    var expectedFileSizeKB = 0
    document.getElementById('coverArtIndex').textContent = ''

    if(coverURL == gobalCoverDefault){coverURL = null}
    console.log(tempID + ' - ' + 'Starting to download/tag the song...')

    if (!fs.existsSync('./tmp')){ fs.mkdirSync('./tmp'); }
    if (!fs.existsSync('./tmp/' + tempID)){ fs.mkdirSync('./tmp/' + tempID); }

    expectedFileSizeKB = info.length_seconds * 128 / 8;
    downloadVideoToAudio(videoURL, expectedFileSizeKB, title, artist, album, coverURL, tempID);
    addDownloadToQueue(tempID, title, artist, coverURL)
    reportProgress(tempID, 0)

    // Ok, we've started the video being downloaded, now if there's a playlist, prepare next video

    try {
      if(globalPlaylistArray['items'][0] != undefined) {
        //  There's a next playlist video, so prepare it
        populateNextVideoToDownload();
      }
      else {
        globalPlaylistArray = '';
        document.getElementById('btnPaste').value = 'Paste YouTube Link';
        resetGUI();
      }
    }
    catch(e) { console.log(e) }

  });
}



function populateNextVideoToDownload() {
  console.log('loading next video in playlist')

  globalVideoURL = globalPlaylistArray['items'][0]['url_simple']

  console.log('URL: ' + globalVideoURL)

  ytdl.getInfo(globalVideoURL, (err, info) => {
    if (err) throw err;
    console.log('title:', info.title);

    // Parse title to extract artist and title information

    var splitTitle = info.title.split('-')
    var artist = splitTitle[0].trim()
    arrayOfTitleFluff.forEach(element => { artist = artist.replace(element, '') }); 

    if(splitTitle[1] != null) {
      var title = splitTitle[1].trim()
      arrayOfTitleFluff.forEach(element => { title = title.replace(element, '') }); 
    }
    else { title = artist }

    title = title.trim()
    artist = artist.trim()

    if(title != '') { document.getElementById("textInputTitle").value = title }
    if(artist != '') { document.getElementById("textInputArtist").value = artist }

    globalPlaylistArray['items'].splice(0, 1)
  });


}



function generateID(length) {
  var result           = '';
  var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  var charactersLength = characters.length;
  for ( var i = 0; i < length; i++ ) {
     result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }
  return result;
}