const { remote, ipcRenderer } = require('electron')




function searchArt() {
  var textArtist = document.getElementById("textInputArtist").value;
  var textAlbum = document.getElementById("textInputAlbum").value;

  if(textArtist == '' && textAlbum == '') {
    dialog.showMessageBoxSync(null, { 
      type: 'error', 
      message: 'You must enter artist and/or album information before searching for cover art.'
    })
    return
  }
  
  document.getElementById('coverArt').src = ipcRenderer.sendSync('get_globalCoverLoading')

  var opts = {
    searchTerm: 'album cover' + textArtist + ' ' + textAlbum,
    queryStringAddition: '&tbs=iar:s'
  };
  
  console.log('searching for cover art for: ' + textArtist + '/' + textAlbum)

  gis(opts, logResults);

  function logResults(error, results) {
    if (error) {
      console.log(error);
    }
    else {
      console.log('obtained image search results, validating initial results...')

      searchResultsJSON = results

      // validate first few URLs to make process a bit smoother for user

      for (i=0; i < 20; i++){
        fetch(searchResultsJSON[i].url, { method: 'HEAD' })
        .then(res => {
          if (!res.ok) {
            searchResultsJSON.splice(i, 1)
            if(i != 0) {i--}
          }
        }).catch(err => console.log('Error:', err));
      }
      displaySpecificCoverArt(0)
    }
  }

}

function displayNextCover() {
  if (searchResultsJSON != '') {displaySpecificCoverArt(currentlyShownCoverArt() + 1)}
  else {console.log('no image results obtained, cannot display')}
}

function displayPrevCover() {
  if (searchResultsJSON != '') {displaySpecificCoverArt(currentlyShownCoverArt() - 1)}
  else {console.log('no image results obtained, cannot display')}
}

function clearCover() {
  console.log('Clearing image searches')
  searchResultsJSON = ''
  var album_cover_index = document.getElementById('coverArtIndex')

  document.getElementById('coverArt').src = gobalCoverDefault
  album_cover_index.textContent = 'No cover art will be used'

}

function displaySpecificCoverArt(i) {
  var album_cover = document.getElementById('coverArt')
  var album_cover_index = document.getElementById('coverArtIndex')

  console.log('Trying to show art at index ' + i)

  if(i==-1) {
    album_cover.src = ipcRenderer.sendSync('get_globalCoverDefault')
    console.log('Setting cover to default image')
  }

  fetch(searchResultsJSON[i].url, { method: 'HEAD' })
  .then(res => {
    if (res.ok) {
      album_cover.src = searchResultsJSON[i].url
      album_cover_index.textContent = searchResultsJSON[i].width + ' x ' + searchResultsJSON[i].height
      console.log('showing art at index ' + i)
      return 0
    } else {
      searchResultsJSON.splice(i, 1)
      album_cover_index.textContent = i + ' of ' + searchResultsJSON.length
      console.log('Failed to get art at index ' + i + ', removed offending entry')
      return 1
    }
  }).catch(err => console.log('Error:', err));
  return 2
}

function currentlyShownCoverArt() {
  var album_cover = document.getElementById('coverArt')
  for (var i = 0; i < searchResultsJSON.length; i++) {
    if (album_cover.src == searchResultsJSON[i].url) {return i;}
  }
  return -1
}