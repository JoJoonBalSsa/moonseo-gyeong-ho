let listenerAdded = false;

function addListener() {
  if (!listenerAdded) {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.message === "confirm_download") {
        const userConfirmed = confirm("이 파일을 다운로드하시겠습니까?");
        sendResponse({ userConfirmed: userConfirmed });
      }
      return true;
    });
    listenerAdded = true;
  }
}

addListener();