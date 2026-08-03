const slide = document.querySelector('.slide');

function fit() {
  const scale = Math.min(innerWidth / 1920, innerHeight / 1080);
  slide.style.setProperty('--scale', String(scale));
}

fit();
addEventListener('resize', fit);

let startX = 0;
const send = deckAction => parent.postMessage({ deckAction }, '*');

addEventListener('keydown', event => {
  const key = event.key.toLowerCase();
  const map = {
    arrowright: 'next', arrowdown: 'next', ' ': 'next', pagedown: 'next',
    arrowleft: 'prev', arrowup: 'prev', pageup: 'prev',
    home: 'first', end: 'last', n: 'notes', f: 'fullscreen'
  };
  if (!map[key]) return;
  event.preventDefault();
  send(map[key]);
});

addEventListener('pointerdown', event => { startX = event.clientX; });
addEventListener('pointerup', event => {
  const delta = event.clientX - startX;
  if (Math.abs(delta) > 70) send(delta < 0 ? 'next' : 'prev');
});
