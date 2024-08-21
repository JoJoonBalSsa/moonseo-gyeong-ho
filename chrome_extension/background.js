let downloadQueue = [];
let isProcessing = false;
let processedDownloads = new Set();

chrome.downloads.onCreated.addListener((downloadItem) => {
  console.log(downloadItem.mime);
  if (!processedDownloads.has(downloadItem.id) && downloadItem.mime == "application/octet-stream") {
  //if (!processedDownloads.has(downloadItem.id) && downloadItem.mime == "application/pdf") {
    console.log(downloadItem.mime);
    chrome.downloads.cancel(downloadItem.id);
    downloadQueue.push(downloadItem);
    processQueue();
  }
});

async function processQueue() {
  if (isProcessing) return;
  isProcessing = true;

  while (downloadQueue.length > 0) {
    const downloadItem = downloadQueue.shift();
    await checkDownloadSafety(downloadItem);
  }

  isProcessing = false;
}

async function checkDownloadSafety(downloadItem) {
  try {
    const response = await fetch('http://15.164.40.221:5000/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: downloadItem.url }),
    });

    notification('진행중', '검증 중 입니다...');

    const result = await response.json();
    console.log(result.safe);
    downloadItem.url = result.url;

    if (result.safe) {
      await fileDownLoad(downloadItem, 'http://15.164.40.221:5000/' + result.path);
      notification('완료', '다운로드 완료!')
    } else {
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tabs.length > 0) {
        await chrome.scripting.executeScript({
          target: { tabId: tabs[0].id },
          files: ['content.js']
        });

        const userResponse = await chrome.tabs.sendMessage(tabs[0].id, { message: "confirm_download" });
        console.log(userResponse.userConfirmed);
        if (userResponse.userConfirmed) {
          await fileDownLoad(downloadItem, 'http://15.164.40.221:5000/' + result.path);
        } else {
          notification('다운로드 취소', '사용자가 다운로드를 취소했습니다.');
        }
      } else {
        notification('재시도 해보세요!', '활성 탭을 찾을 수 없습니다.');
      }
    }
  } catch (error) {
    console.error('Error checking download safety:', error);
    notification('오류 발견', '다운로드 안전성 확인 중 오류가 발생했습니다.');
  }
}

async function fileDownLoad(downloadItem, path) {
  const response = await fetch(path);

  if (response.ok) {
    return new Promise((resolve, reject) => {
      chrome.downloads.download({ url: path }, (downloadId) => {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError.message);
        } else {
          console.log("Download started with ID:", downloadId);
          processedDownloads.add(downloadId);
          resolve();
        }
      });
    });
  } else {
    throw new Error('Error downloading file');
  }
}

function notification(title, message) {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'images/icon-48.png',
    title: title,
    message: message
  });
}