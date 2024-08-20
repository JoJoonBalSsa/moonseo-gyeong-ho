let downloadQueue = [];
let isProcessing = false;
let processedDownloads = new Set();

chrome.downloads.onCreated.addListener((downloadItem) => {
  if (!processedDownloads.has(downloadItem.id)) {
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

    const result = await response.json();
    console.log(result.safe);

    if (result.safe) {
      startDownload(downloadItem);
    } else {
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tabs.length > 0) {
        await chrome.scripting.executeScript({
          target: { tabId: tabs[0].id },
          files: ['content.js']
        });

        const userResponse = await chrome.tabs.sendMessage(tabs[0].id, { message: "confirm_download" });

        if (userResponse.userConfirmed) {
          startDownload(downloadItem);
        } else {
          cancelDownload('사용자가 다운로드를 취소했습니다.');
        }
      } else {
        cancelDownload('활성 탭을 찾을 수 없습니다.');
      }
    }
  } catch (error) {
    console.error('Error checking download safety:', error);
    cancelDownload('다운로드 안전성 확인 중 오류가 발생했습니다.');
  }
}

function startDownload(downloadItem) {
  chrome.downloads.download({
    url: downloadItem.url
  }, (newDownloadId) => {
    console.log("Download started with ID:", newDownloadId);
    processedDownloads.add(newDownloadId);
  });
}

function cancelDownload(message) {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'images/icon-48.png',
    title: '다운로드 취소됨',
    message: message
  });
}