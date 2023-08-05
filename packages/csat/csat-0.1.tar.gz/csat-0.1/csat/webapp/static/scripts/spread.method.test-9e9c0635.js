var onmessage;

onmessage = function(event) {
  postMessage(event.data);
  return postMessage('bum');
};
