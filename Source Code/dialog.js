const { dialog } = require('electron').remote


function chooseOutputFolder() {


  globalOutputDirectory = store.get('outputFolder')
  console.log('Original output directory: ' + String(globalOutputDirectory))

  const options = {
      title: 'Choose a folder to save music to',
      defaultPath: String(globalOutputDirectory),
      buttonLabel: 'Choose Folder',
      message: 'Choose TukTuk\'s output folder',
      properties: ['openDirectory']
    };
  const selectedPaths = dialog.showOpenDialogSync(null, options);
  console.log( 'User selected: ' + selectedPaths);

  if (selectedPaths != undefined) {
      console.log('New Path Saved')
      globalOutputDirectory = selectedPaths
      store.set('outputFolder', selectedPaths);
  }
}

function showWelcomeMessage() {
  const options = {
    title: 'Welcome',
    type: 'none',
    message: 'Welcome to TukTuk!\n\nThis program downloads music from YouTube and saves it to a directory of your choice. TukTuk tries to extract Title/Artist information from the title - Album name is on you.\n\nPress "O" to search for cover art, use "<" and ">" to select a cover you like, or "X" to not use any cover art.\n\nClick Proceed to download and tag the song.'
  };
dialog.showMessageBoxSync(null, options);  
store.set('welcomed', true)
}