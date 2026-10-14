/* Service Worker: 接收 push 事件并展示通知 */
self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('push', (event) => {
  let data = { title: '收到推送', body: '(空 payload)', url: '/' };
  try {
    if (event.data) data = { ...data, ...event.data.json() };
  } catch {
    if (event.data) data.body = event.data.text();
  }

  const options = {
    body: data.body,
    icon: '/icons/icon-192.png',
    badge: '/icons/favicon-64.png',
    tag: data.tag || 'web-push-demo',
    data: { url: data.url || '/', receivedAt: new Date().toISOString(), raw: data },
  };

  event.waitUntil(
    Promise.all([
      self.registration.showNotification(data.title, options),
      notifyClients({ type: 'push-received', payload: data }),
    ])
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const target = event.notification.data?.url || '/';
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((list) => {
      for (const client of list) {
        if ('focus' in client) {
          client.navigate(target).catch(() => {});
          return client.focus();
        }
      }
      return self.clients.openWindow(target);
    })
  );
});

self.addEventListener('pushsubscriptionchange', (event) => {
  event.waitUntil(
    notifyClients({
      type: 'subscription-change',
      oldSubscription: event.oldSubscription ? event.oldSubscription.toJSON() : null,
    })
  );
});

async function notifyClients(message) {
  const list = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
  for (const client of list) client.postMessage(message);
}
