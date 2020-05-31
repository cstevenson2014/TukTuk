



function reportProgress(id, progress) {

  if (progress == -1) { document.getElementById(id + 'progress').removeAttribute("value") }
  else {document.getElementById(id + 'progress').value = progress}
}



function addDownloadToQueue(tempID, title, artist, coverArtURL) {
  var newDiv = document.createElement("div");          
  var parentDiv = document.getElementById("downloadQueueContainer");
  console.log(tempID + ' - ' + 'Adding queue node')
  newDiv.setAttribute("ID", tempID)
  newDiv.setAttribute("Class", "pendingDownload")
  newDiv.innerHTML = '<img src=\"' + coverArtURL + '\" class=\"downloadQueueImage\"> ' 
    + title + ' - ' + artist
    + '<br><progress ID=\"' + tempID + 'progress\" max=\"100\" class=\"pendingDownloadProgress\"></progress>'
  parentDiv.appendChild(newDiv);          
}

function removeDownloadFromQueue(tempID) {
  var newDiv = document.getElementById(tempID);
  console.log(tempID + ' - ' + 'Removing node');
  newDiv.parentNode.removeChild(newDiv); 
}