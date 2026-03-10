export default {
  async fetch(request) {
    const url = new URL(request.url);

    // Servir archivo ads.txt
    if (url.pathname === '/ads.txt') {
      return new Response('google.com, pub-7917471830627014, DIRECT, f08c47fec0942fa0', {
        headers: {
          'content-type': 'text/plain',
          'cache-control': 'public, max-age=3600',
        },
      });
    }

    // Para cualquier otra ruta, pasar al origen (WordPress)
    return fetch(request);
  },
};
