var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// worker/ecdoticon.js
function log(level, event, data = {}, requestId = null) {
  const logEntry = {
    timestamp: (/* @__PURE__ */ new Date()).toISOString(),
    level,
    event,
    requestId: requestId || crypto.randomUUID(),
    ...data
  };
  console.log(JSON.stringify(logEntry));
}
__name(log, "log");
async function callOpenAIWithTimeout(env, messages, timeoutMs = 25e3, { max_tokens = 1200, temperature = 0.1 } = {}) {
  const startTime = Date.now();
  const requestId = crypto.randomUUID();
  log("info", "openai_request_start", {
    messageCount: messages.length,
    timeout: timeoutMs
  }, requestId);
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${env.OPENAI_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: env.OPENAI_MODEL || "gpt-4o-mini",
        messages,
        max_tokens,
        temperature
      }),
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    const duration = Date.now() - startTime;
    if (!response.ok) {
      const error = await response.text();
      log("error", "openai_api_error", { status: response.status, error, duration }, requestId);
      throw new Error(`OpenAI API error: ${response.status} ${error}`);
    }
    const data = await response.json();
    log("info", "openai_request_success", { duration, tokensUsed: data.usage?.total_tokens }, requestId);
    return data;
  } catch (error) {
    clearTimeout(timeoutId);
    const duration = Date.now() - startTime;
    if (error.name === "AbortError") {
      log("error", "openai_timeout", { duration, timeout: timeoutMs }, requestId);
      throw new Error(`timeout`);
    }
    log("error", "openai_request_failed", { error: error.message, duration }, requestId);
    throw error;
  }
}
__name(callOpenAIWithTimeout, "callOpenAIWithTimeout");
var CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
  "Vary": "Origin"
};
var JSONH = { "Content-Type": "application/json", ...CORS };
var TXTH = { "Content-Type": "text/plain; charset=utf-8", ...CORS };
var CSSH = { "Content-Type": "text/css; charset=utf-8", ...CORS };
function json(b, s = 200) {
  return new Response(JSON.stringify(b), { status: s, headers: JSONH });
}
__name(json, "json");
function css(t, s = 200) {
  return new Response(t, { status: s, headers: CSSH });
}
__name(css, "css");
var GREETING = /^(hola|buenas|buenos dias|buenos días|buenas tardes|buenas noches|saludos|qué tal|que tal|ayuda|help)\b/i;
var deburrMap = { "\xE1": "a", "\xE9": "e", "\xED": "i", "\xF3": "o", "\xFA": "u", "\xF1": "n", "\xFC": "u" };
function deburr(s = "") {
  return s.replace(/[áéíóúñü]/gi, (ch) => deburrMap[ch.toLowerCase()] || ch);
}
__name(deburr, "deburr");
function norm(s = "") {
  return deburr(String(s || "").toLowerCase()).replace(/['''´`"]/g, "").replace(/[–—-]/g, " ").replace(/[^\p{L}\p{N}]+/gu, " ").replace(/\s+/g, " ").trim();
}
__name(norm, "norm");
function cleanHTML(t = "") {
  return String(t || "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
}
__name(cleanHTML, "cleanHTML");
function dedupeByUrl(list = []) {
  const seen = /* @__PURE__ */ new Set();
  const out = [];
  for (const d of list) {
    const u = d?.url || "";
    if (u && !seen.has(u)) {
      seen.add(u);
      out.push(d);
    }
  }
  return out;
}
__name(dedupeByUrl, "dedupeByUrl");
async function searchEcdotica(query) {
  const base = "https://ecdotica.com/wp-json/ecdoticon/v1/search";
  const url = `${base}?query=${encodeURIComponent(query)}&per_page=12`;
  try {
    const r = await fetch(url, { cf: { cacheTtl: 300 } });
    if (!r.ok) return [];
    const payload = await r.json();
    const items = payload.results || [];
    return items.map((it) => ({
      title: cleanHTML(it.title || ""),
      url: it.url,
      text: cleanHTML(it.excerpt || "")
    }));
  } catch {
    return [];
  }
}
__name(searchEcdotica, "searchEcdotica");
async function wikiSummary(title) {
  const u = `https://es.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`;
  try {
    const r = await fetch(u, { cf: { cacheTtl: 600 } });
    if (!r.ok) return null;
    const j = await r.json();
    if (!j?.extract || j?.type === "disambiguation") return null;
    return {
      title: `Wikipedia: ${j.title || title}`,
      url: `https://es.wikipedia.org/wiki/${encodeURIComponent(j.title || title)}`,
      text: cleanHTML(j.extract).slice(0, 650)
    };
  } catch {
    return null;
  }
}
__name(wikiSummary, "wikiSummary");
async function searchWikipedia(query) {
  let doc = await wikiSummary(query);
  if (doc) return doc;
  try {
    const u = `https://es.wikipedia.org/w/api.php?action=opensearch&format=json&limit=1&search=${encodeURIComponent(query)}`;
    const r = await fetch(u, { cf: { cacheTtl: 600 } });
    if (!r.ok) return null;
    const data = await r.json();
    const title = Array.isArray(data) && data[1] && data[1][0];
    if (title) return await wikiSummary(title);
  } catch {
  }
  return null;
}
__name(searchWikipedia, "searchWikipedia");
var DEFAULT_WIKI_WHITELIST = [
  "jaime saenz",
  "alcides arguedas",
  "augusto cespedes",
  "augusto c\xE9spedes",
  "yolanda bedregal",
  "oscar cerruto",
  "\xF3scar cerruto",
  "nataniel aguirre",
  "adela zamudio",
  "jesus urzagasti",
  "jes\xFAs urzagasti",
  "ricardo jaimes freyre",
  "franz tamayo",
  "hilda mundy",
  "virginia estenssoro",
  "arturo borda",
  "antonio diaz villamil",
  "antonio d\xEDaz villamil",
  "jesus lara",
  "jes\xFAs lara",
  "jaime mendoza",
  "marcelo quiroga santa cruz",
  "pedro shimose",
  "blanca wiethuchter",
  "blanca wieth\xFCchter",
  "roberto echazu",
  "roberto echaz\xFA",
  "edmundo camargo",
  "oscar alfaro",
  "\xF3scar alfaro",
  "maria josefa mujia",
  "mar\xEDa josefa muj\xEDa",
  "alcira cardona",
  "edmundo paz soldan",
  "edmundo paz sold\xE1n",
  "liliana colanzi",
  "giovanna rivero",
  "rodrigo hasbun",
  "rodrigo hasb\xFAn",
  "maximiliano barrientos",
  "magela baudoin",
  "wilmer urrelo",
  "sebastian antezana",
  "sebasti\xE1n antezana",
  "homero carvalho",
  "camila urioste",
  "gaby vallejo",
  "el cuervo",
  "editorial el cuervo",
  "editorial 3600",
  "3600",
  "mantis",
  "mantis narrativa",
  "gente comun",
  "gente com\xFAn",
  "dum dum"
];
function getWikiWhitelist(env) {
  const raw = (env.WIKI_WHITELIST || "").trim();
  const add = raw ? raw.split(",").map((s) => norm(s)).filter(Boolean) : [];
  const base = DEFAULT_WIKI_WHITELIST.slice();
  for (const t of add) {
    if (!base.includes(t)) base.push(t);
  }
  return new Set(base);
}
__name(getWikiWhitelist, "getWikiWhitelist");
function isWikipediaAllowed({ env, query, hit }) {
  if (String(env.ALLOW_WIKIPEDIA || "").toLowerCase() !== "true") return false;
  if (hit?.wiki) {
    if (hit.wiki.allow === true) return true;
    if (hit.wiki.allow === false) return false;
  }
  const wl = getWikiWhitelist(env);
  const qn = norm(query);
  if (hit) {
    if (wl.has(norm(hit.id))) return true;
    for (const a of hit.aliases || []) {
      if (wl.has(norm(a))) return true;
    }
  }
  for (const token of wl) {
    if (qn.includes(token)) return true;
  }
  return false;
}
__name(isWikipediaAllowed, "isWikipediaAllowed");
var CANON = [
  {
    id: "marcelo_paz_soldan",
    aliases: ["marcelo paz soldan", "marcelo paz sold\xE1n", "marcelo", "director nuevo milenio", "editorial nuevo milenio", "ecd\xF3tica", "ecdotica"],
    bio: "Editor y director de Editorial Nuevo Milenio; impulsa Ecd\xF3tica como plataforma cr\xEDtica y docente.",
    guide: "Nota editorial: Marcelo Paz Sold\xE1n es editor boliviano y director de Nuevo Milenio. Promueve Ecd\xF3tica y recursos para estudiantes, con \xE9nfasis en literatura boliviana contempor\xE1nea.",
    ctx: [
      { title: "Perfil de autor \u2013 Ecd\xF3tica", url: "https://ecdotica.com/author/marcelo-paz-soldan/", text: "Art\xEDculos, rese\xF1as e entrevistas firmadas." },
      { title: "Cartograf\xEDa literaria boliviana (2000\u20132025)", url: "https://ecdotica.com/cartografia-literaria-boliviana-2000-2025/", text: "Panorama did\xE1ctico con ejes y enlaces." },
      { title: "Inicio \u2013 Ecd\xF3tica", url: "https://ecdotica.com/", text: "Portal de recursos y notas." }
    ],
    strict: true,
    wiki: { allow: false }
  },
  {
    id: "edmundo_paz_soldan",
    aliases: ["edmundo paz soldan", "edmundo paz sold\xE1n", "\xE1rea protegida", "area protegida", "los dias de la peste", "los d\xEDas de la peste", "norte"],
    bio: "Narrador boliviano (1967). Ciudad, tecnolog\xEDa, memoria, pol\xEDtica.",
    ctx: [
      { title: "\xC1rea protegida \u2013 Ecd\xF3tica", url: "https://ecdotica.com/area-protegida-de-edmundo-paz-soldan/", text: "Apocalipsis medioambiental; comunidad y creencias." },
      { title: "Edmundo Paz Sold\xE1n en Ecd\xF3tica", url: "https://ecdotica.com/?s=Edmundo%20Paz%20Sold%C3%A1n", text: "Resultados del autor." }
    ],
    wiki: { allow: true }
  },
  {
    id: "hermanos_loayza",
    aliases: ["hermanos loayza", "los hermanos loayza", "diego loayza", "\xE1lvaro loayza", "alvaro loayza", "de kenchas, perdularios y otros malvivientes", "kenchas", "\xBFdonde carajos esta litovchenko", "donde carajos esta litovchenko", "litovchenko"],
    bio: "\xC1lvaro y Diego Loayza: narrativa urbana pace\xF1a; humor negro, jerga y pulso policial.",
    guide: "Nota editorial: 'De kenchas\u2026' (El Cuervo, 2013) se volvi\xF3 de culto por su o\xEDdo callejero. En 2025 publican con Nuevo Milenio '\xBFD\xF3nde carajos est\xE1 Litovchenko?' (thriller noventero).",
    ctx: [
      { title: "Presentaci\xF3n de '\xBFD\xF3nde carajos est\xE1 Litovchenko?' \u2013 Ecd\xF3tica", url: "https://ecdotica.com/presentacion-de-donde-carajos-esta-litovchenko-en-la-paz/", text: "Nota de presentaci\xF3n (Nuevo Milenio, 2025)." },
      { title: "Ficha 'De kenchas\u2026' \u2013 El Cuervo", url: "https://www.editorialelcuervo.com/libro-de-kenchas-perdularios-y-otros-malvivientes/", text: "Ficha editorial (2013)." }
    ],
    strict: true,
    wiki: { allow: false }
  },
  {
    id: "liliana_colanzi",
    aliases: ["liliana colanzi", "colanzi", "ustedes brillan en lo oscuro", "vacaciones permanentes", "la ola", "nuestro mundo muerto"],
    bio: "Cuentista boliviana; ciencia/mito/territorio; editora (Dum Dum).",
    guide: "Obra en cuento: 'Vacaciones permanentes' (2010), 'La ola' (2014), 'Nuestro mundo muerto' (2016) y 'Ustedes brillan en lo oscuro' (2022, Premio Ribera del Duero). No ha publicado novela.",
    ctx: [
      { title: "Entrevista/Perfil \u2013 Ecd\xF3tica", url: "https://ecdotica.com/liliana-colanzi-usar-la-rabia-y-el-dolor-para-crear-pensar-cuestionar-y-transgredir/", text: "Entrevista y claves po\xE9ticas." },
      { title: "'Nuestro mundo muerto' \u2013 Ecd\xF3tica", url: "https://ecdotica.com/liliana-colanzi-nuestro-mundo-muerto-y-apuntes-para-un-perfil/", text: "Recepci\xF3n y perfil." },
      { title: "'Ustedes brillan en lo oscuro' \u2013 Ecd\xF3tica", url: "https://ecdotica.com/ustedes-brillan-en-lo-oscuro-de-liliana-colanzi-5/", text: "Lecturas del libro premiado." }
    ],
    strict: true,
    wiki: { allow: false }
  },
  {
    id: "ricardo_torrejon",
    aliases: ["ricardo torrej\xF3n", "ricardo torrej\xF3n morales", "ricardo torrej\xF3n m", "ricardo torrej\xF3n tarija", "ricardo torrej\xF3n tarije\xF1o", "lo que esta en el mundo bajo el cielo", "lo que est\xE1 en el mundo, bajo el cielo"],
    bio: "Autor tarije\xF1o de no ficci\xF3n; lectura del Seminario 18 de Lacan.",
    guide: "Libro: 'Lo que est\xE1 en el mundo, bajo el cielo' (ensayo; aproximaci\xF3n al Seminario 18 de Jacques Lacan). L\xEDnea de trabajo: lectura lacaniana y reflexi\xF3n cultural.",
    ctx: [
      { title: "Presentaci\xF3n / Cobertura \u2013 Ecd\xF3tica", url: "https://ecdotica.com/?s=Ricardo%20Torrej%C3%B3n", text: "Entradas relacionadas al autor y su libro en Ecd\xF3tica." },
      { title: "No ficci\xF3n \u2013 Ecd\xF3tica", url: "https://ecdotica.com/category/no-ficcion/", text: "Secci\xF3n con notas/ensayos vinculados." }
    ],
    strict: true,
    wiki: { allow: false }
  },
  {
    id: "giovanna_rivero",
    aliases: ["giovanna rivero", "rivero", "98 segundos sin sombra", "para comerte mejor", "las camaleonas", "tierra fresca de su tumba", "ni\xF1as y detectives"],
    bio: "Cuentista y novelista boliviana (1972); realismo g\xF3tico, ciencia ficci\xF3n, terror.",
    guide: "Obra destacada: '98 segundos sin sombra' (2014), 'Para comerte mejor' (2015, Premio Dante Alighieri), 'Tierra fresca de su tumba' (2020). Cofundadora de Mantis Narrativa con Magela Baudoin. Seleccionada Bogot\xE1 39 (2011).",
    ctx: [
      { title: "Giovanna Rivero en Ecd\xF3tica", url: "https://ecdotica.com/?s=Giovanna%20Rivero", text: "Art\xEDculos y rese\xF1as sobre la autora." },
      { title: "Para comerte mejor \u2013 refs", url: "https://ecdotica.com/?s=Para%20comerte%20mejor", text: "Libro de cuentos premiado." }
    ],
    strict: false,
    wiki: { allow: true }
  },
  {
    id: "rodrigo_hasbun",
    aliases: ["rodrigo hasb\xFAn", "rodrigo hasbun", "hasb\xFAn", "hasbun", "los afectos", "el lugar del cuerpo", "los a\xF1os invisibles"],
    bio: "Narrador boliviano (1981); memoria familiar, exilio, identidad.",
    guide: "Obras: 'Los afectos' (2015, traducida a 10 idiomas), 'El lugar del cuerpo' (2007), 'Los a\xF1os invisibles' (2020). Seleccionado Granta 22 mejores escritores j\xF3venes en espa\xF1ol (2010) y Bogot\xE1 39 (2007).",
    ctx: [
      { title: "Rodrigo Hasb\xFAn en Ecd\xF3tica", url: "https://ecdotica.com/?s=Rodrigo%20Hasb%C3%BAn", text: "Entradas relacionadas." },
      { title: "Los afectos \u2013 referencias", url: "https://ecdotica.com/?s=Los%20afectos", text: "Recepci\xF3n cr\xEDtica." }
    ],
    strict: false,
    wiki: { allow: true }
  },
  {
    id: "maximiliano_barrientos",
    aliases: ["maximiliano barrientos", "barrientos", "en el cuerpo una voz", "miles de ojos", "hoteles", "fotos tuyas cuando empiezas a envejecer", "diario"],
    bio: "Narrador boliviano (1979); terror, ciencia ficci\xF3n, weird fiction.",
    guide: "Obras: 'En el cuerpo una voz' (2017), 'Miles de ojos' (2021), 'Diario' (2009, Premio Nacional). Fusiona horror corporal con atm\xF3sferas lovecraftianas.",
    ctx: [
      { title: "Maximiliano Barrientos en Ecd\xF3tica", url: "https://ecdotica.com/?s=Maximiliano%20Barrientos", text: "Art\xEDculos y cr\xEDticas." }
    ],
    strict: false,
    wiki: { allow: true }
  },
  {
    id: "wilmer_urrelo",
    aliases: ["wilmer urrelo", "urrelo", "fantasmas asesinos", "hablar con los perros", "mundo negro", "el chicuelo dice"],
    bio: "Narrador boliviano (1975); narrativa urbana, lucha libre, exploraci\xF3n de ciudad.",
    guide: "Obras: 'Fantasmas asesinos' (2006, IX Premio Nacional de Novela), 'Hablar con los perros' (2011, Premio Anna Seghers 2012), 'Mundo negro' (2000). Padece desmielinizaci\xF3n desde 2012.",
    ctx: [
      { title: "Wilmer Urrelo en Ecd\xF3tica", url: "https://ecdotica.com/?s=Wilmer%20Urrelo", text: "Notas y entrevistas." }
    ],
    strict: false,
    wiki: { allow: true }
  },
  {
    id: "magela_baudoin",
    aliases: ["magela baudoin", "baudoin", "la composici\xF3n de la sal", "la composicion de la sal", "el sonido de la h", "mujeres de costado", "solo vuelo en tu ca\xEDda", "solo vuelo en tu caida"],
    bio: "Escritora y periodista boliviana (1973); cofundadora de Mantis Narrativa.",
    guide: "Obras: 'La composici\xF3n de la sal' (2014, Premio Hispanoamericano de Cuento Gabriel Garc\xEDa M\xE1rquez 2015), 'El sonido de la H' (2014, Premio Nacional de Novela), 'Vendr\xE1 la muerte y tendr\xE1 tus ojos' (2023). Cofund\xF3 Mantis Narrativa con Giovanna Rivero.",
    ctx: [
      { title: "Magela Baudoin en Ecd\xF3tica", url: "https://ecdotica.com/?s=Magela%20Baudoin", text: "Rese\xF1as y art\xEDculos." }
    ],
    strict: false,
    wiki: { allow: true }
  },
  {
    id: "sebastian_antezana",
    aliases: ["sebasti\xE1n antezana", "sebastian antezana", "antezana", "la toma del manuscrito", "el amor seg\xFAn", "el amor segun", "iluminaci\xF3n", "iluminacion"],
    bio: "Narrador boliviano (1982); experimentaci\xF3n formal, metaficci\xF3n.",
    guide: "Obras: 'La toma del manuscrito' (2008, X Premio Nacional de Novela), 'El amor seg\xFAn' (2011), 'Iluminaci\xF3n' (2017, cuentos). Nieto de Marcelo Quiroga Santa Cruz. Doctor por Cornell University.",
    ctx: [
      { title: "Sebasti\xE1n Antezana en Ecd\xF3tica", url: "https://ecdotica.com/?s=Sebasti%C3%A1n%20Antezana", text: "Entradas relacionadas." }
    ],
    strict: false,
    wiki: { allow: true }
  },
  {
    id: "homero_carvalho",
    aliases: ["homero carvalho", "carvalho", "homero carvalho oliva", "ucron\xEDas", "ucronias", "el vals de los reptiles"],
    bio: "Narrador boliviano (1957); ciencia ficci\xF3n, historia alternativa.",
    guide: "Obras: 'Ucron\xEDas' (historia alternativa), 'El vals de los reptiles'. Especializado en literatura fant\xE1stica y ciencia ficci\xF3n boliviana.",
    ctx: [
      { title: "Homero Carvalho en Ecd\xF3tica", url: "https://ecdotica.com/?s=Homero%20Carvalho", text: "Art\xEDculos relacionados." }
    ],
    strict: false,
    wiki: { allow: true }
  },
  {
    id: "camila_urioste",
    aliases: ["camila urioste", "urioste", "diario de alicia", "las vueltas de la vida", "el otro lado del arco\xEDris", "el otro lado del arcoiris"],
    bio: "Escritora boliviana (1984); narrativa contempor\xE1nea, adaptaciones.",
    guide: "Obras: 'Diario de Alicia' (adaptada a serie), 'Las vueltas de la vida', 'El otro lado del arco\xEDris'. Reconocida por narrativa accesible y temas contempor\xE1neos.",
    ctx: [
      { title: "Camila Urioste en Ecd\xF3tica", url: "https://ecdotica.com/?s=Camila%20Urioste", text: "Notas sobre la autora." }
    ],
    strict: false,
    wiki: { allow: true }
  },
  {
    id: "gaby_vallejo",
    aliases: ["gaby vallejo", "vallejo canedo", "gaby vallejo canedo", "hijo de opa", "el otro lado del silencio"],
    bio: "Escritora y docente boliviana (1941-2024); literatura infantil y juvenil.",
    guide: "Obras: 'Hijo de Opa' (Premio Nacional de Literatura Infantil y Juvenil 1977), 'El otro lado del silencio'. Pionera de la literatura infantil en Bolivia. Falleci\xF3 en enero 2024.",
    ctx: [
      { title: "Gaby Vallejo en Ecd\xF3tica", url: "https://ecdotica.com/?s=Gaby%20Vallejo", text: "Notas y homenajes." }
    ],
    strict: false,
    wiki: { allow: true }
  },
  {
    id: "jaime_saenz",
    aliases: ["jaime saenz", "s\xE1enz", "saenz", "felipe delgado"],
    bio: "Poeta y narrador boliviano (1921-1986). Nocturnidad, ciudad, experiencia l\xEDmite.",
    ctx: [
      { title: "Jaime Saenz en Ecd\xF3tica", url: "https://ecdotica.com/?s=Jaime%20Saenz", text: "Entrevistas y cr\xEDticas." },
      { title: "Felipe Delgado \u2013 referencias", url: "https://ecdotica.com/?s=Felipe%20Delgado", text: "Lecturas y rese\xF1as." }
    ],
    wiki: { allow: true }
  },
  {
    id: "alcides_arguedas",
    aliases: ["alcides arguedas", "raza de bronce", "pueblo enfermo"],
    bio: "Narrador y ensayista boliviano (1879-1946). Indianismo y cr\xEDtica social.",
    ctx: [
      { title: "Alcides Arguedas en Ecd\xF3tica", url: "https://ecdotica.com/?s=Alcides%20Arguedas", text: "Notas y referencias." },
      { title: "Raza de bronce \u2013 refs.", url: "https://ecdotica.com/?s=Raza%20de%20bronce", text: "Recepci\xF3n y estudios." }
    ],
    wiki: { allow: true }
  },
  {
    id: "yolanda_bedregal",
    aliases: ["yolanda bedregal", "bajo el oscuro sol", "yolanda de bolivia"],
    bio: "Poeta y narradora boliviana (1913-1999); voz femenina emblem\xE1tica.",
    ctx: [
      { title: "Yolanda Bedregal en Ecd\xF3tica", url: "https://ecdotica.com/?s=Yolanda%20Bedregal", text: "Rese\xF1as y evocaciones." },
      { title: "Bajo el oscuro sol", url: "https://ecdotica.com/?s=Bajo%20el%20oscuro%20sol", text: "Menciones al t\xEDtulo." }
    ],
    wiki: { allow: true }
  },
  {
    id: "oscar_cerruto",
    aliases: ["\xF3scar cerruto", "oscar cerruto", "aluvi\xF3n de fuego", "aluvion de fuego"],
    bio: "Poeta y narrador boliviano (1912-1981); modernidad y ciudad.",
    ctx: [
      { title: "\xD3scar Cerruto en Ecd\xF3tica", url: "https://ecdotica.com/?s=%C3%93scar%20Cerruto", text: "Entradas y estudios." },
      { title: "Aluvi\xF3n de fuego \u2013 refs.", url: "https://ecdotica.com/?s=Aluvi%C3%B3n%20de%20fuego", text: "Cr\xEDtica y recepci\xF3n." }
    ],
    wiki: { allow: true }
  },
  {
    id: "jesus_urzagasti",
    aliases: ["jes\xFAs urzagasti", "jesus urzagasti", "urzagasti", "tirinea", "en el pa\xEDs del silencio"],
    bio: "Poeta y narrador boliviano (1941-2013). Chaco, memoria, experimentaci\xF3n.",
    guide: "Obras: 'Tirinea' (1969), 'En el pa\xEDs del silencio' (1987), 'Yerubia' (1978). Poeta del Gran Chaco; lenguaje experimental y memoria del territorio.",
    ctx: [
      { title: "Jes\xFAs Urzagasti en Ecd\xF3tica", url: "https://ecdotica.com/jesus-urzagasti-entre-suenos-y-palabras/", text: "Perfil biogr\xE1fico y obra." },
      { title: "Urzagasti \u2013 b\xFAsqueda", url: "https://ecdotica.com/?s=Urzagasti", text: "Entradas relacionadas." }
    ],
    wiki: { allow: true }
  },
  {
    id: "pedro_shimose",
    aliases: ["pedro shimose", "shimose", "quiero escribir pero me sale espuma", "poemas para un pueblo"],
    bio: "Poeta boliviano (1940-2016). Compromiso social, exilio, melancol\xEDa.",
    guide: "Obras: 'Quiero escribir, pero me sale espuma' (1972), 'Poemas para un pueblo' (1968). Poeta del exilio y la memoria colectiva; Premio Casa de las Am\xE9ricas.",
    ctx: [
      { title: "Pedro Shimose en Ecd\xF3tica", url: "https://ecdotica.com/?s=Pedro%20Shimose", text: "Notas y referencias." }
    ],
    wiki: { allow: true }
  },
  {
    id: "blanca_wiethuchter",
    aliases: ["blanca wieth\xFCchter", "blanca wiethuchter", "wieth\xFCchter", "wiethuchter", "luminar", "\xEDtaca"],
    bio: "Poeta boliviana (1947-2004). Experimentaci\xF3n, hermetismo, mito.",
    guide: "Obras: '\xCDtaca' (1972), 'Luminar' (1975), 'Madera viva' (1982). Voz fundamental de la poes\xEDa boliviana contempor\xE1nea; exploraciones del lenguaje y lo m\xEDtico.",
    ctx: [
      { title: "Blanca Wieth\xFCchter en Ecd\xF3tica", url: "https://ecdotica.com/?s=Blanca%20Wieth\xFCchter", text: "Art\xEDculos y estudios." }
    ],
    wiki: { allow: true }
  },
  {
    id: "editorial_el_cuervo",
    aliases: ["el cuervo", "editorial el cuervo"],
    bio: "Sello de narrativa contempor\xE1nea boliviana.",
    ctx: [
      { title: "El Cuervo \u2013 en Ecd\xF3tica", url: "https://ecdotica.com/?s=El%20Cuervo", text: "Notas sobre t\xEDtulos y autores." }
    ],
    wiki: { allow: true }
  },
  {
    id: "editorial_3600",
    aliases: ["3600", "editorial 3600", "plural 3600"],
    bio: "Sello pace\xF1o de narrativa y ensayo.",
    ctx: [
      { title: "3600 \u2013 en Ecd\xF3tica", url: "https://ecdotica.com/?s=3600", text: "Menciones y rese\xF1as." }
    ],
    wiki: { allow: true }
  },
  {
    id: "mantis_narrativa",
    aliases: ["mantis", "mantis narrativa", "editorial mantis"],
    bio: "Editorial fundada por Giovanna Rivero y Magela Baudoin; especializada en escritoras hispanoamericanas.",
    guide: "Mantis Narrativa: proyecto editorial cofundado por Giovanna Rivero y Magela Baudoin. Cat\xE1logo enfocado en voces femeninas de Latinoam\xE9rica.",
    ctx: [
      { title: "Mantis \u2013 en Ecd\xF3tica", url: "https://ecdotica.com/?s=Mantis", text: "Notas vinculadas." }
    ],
    wiki: { allow: true }
  },
  // ── EXPANSIÓN CANÓN: clásicos y contemporáneos ──
  {
    id: "adela_zamudio",
    aliases: ["adela zamudio", "zamudio", "noche de bodas", "ensayos po\xE9ticos", "ensayos poeticos", "nacer hombre"],
    bio: "Poeta y narradora boliviana (1854\u20131928); pionera del feminismo literario en Bolivia.",
    guide: "Conocida como 'Soledad'. Obras: 'Ensayos po\xE9ticos' (1887), 'Leyendas' (1900), 'Noche de bodas' (1951, p\xF3stumo). Su poema 'Nacer hombre' es hito del feminismo hispanoamericano. Fue maestra en Cochabamba. El 11 de octubre (su cumplea\xF1os) es el D\xEDa de la Mujer en Bolivia.",
    ctx: [
      { title: "Adela Zamudio en Ecd\xF3tica", url: "https://ecdotica.com/?s=Adela%20Zamudio", text: "Art\xEDculos y referencias sobre la autora." },
      { title: "Poes\xEDa boliviana \u2013 Ecd\xF3tica", url: "https://ecdotica.com/category/poesia/", text: "Secci\xF3n de poes\xEDa en el portal." }
    ],
    wiki: { allow: true }
  },
  {
    id: "franz_tamayo",
    aliases: ["franz tamayo", "tamayo", "proezas de booz", "scherzos", "epigramas griegos", "creaci\xF3n de la pedagog\xEDa nacional", "creacion de la pedagogia nacional"],
    bio: "Poeta, fil\xF3sofo y pol\xEDtico boliviano (1879\u20131956); voz filos\xF3fica mayor de la literatura boliviana.",
    guide: "Obras: 'Scherzos' (1910), 'Proezas de Booz' (1917), 'Epigramas griegos' (1945). Ensayo: 'Creaci\xF3n de la pedagog\xEDa nacional' (1910). Pensamiento original influido por Nietzsche y las culturas andinas. Tambi\xE9n candidato presidencial.",
    ctx: [
      { title: "Franz Tamayo en Ecd\xF3tica", url: "https://ecdotica.com/?s=Franz%20Tamayo", text: "Notas y referencias sobre el autor." }
    ],
    wiki: { allow: true }
  },
  {
    id: "nataniel_aguirre",
    aliases: ["nataniel aguirre", "aguirre", "juan de la rosa", "memorias del \xFAltimo soldado", "memorias del ultimo soldado"],
    bio: "Narrador y pol\xEDtico boliviano (1843\u20131888); autor de la novela fundacional de la literatura boliviana.",
    guide: "Obra principal: 'Juan de la Rosa: Memorias del \xFAltimo soldado de la Independencia' (1885), considerada la primera gran novela boliviana. Ambientada en la guerra de independencia; mezcla historia y ficci\xF3n con visi\xF3n rom\xE1ntica y patri\xF3tica.",
    ctx: [
      { title: "Nataniel Aguirre en Ecd\xF3tica", url: "https://ecdotica.com/?s=Nataniel%20Aguirre", text: "Referencias sobre el autor." },
      { title: "Juan de la Rosa \u2013 refs.", url: "https://ecdotica.com/?s=Juan%20de%20la%20Rosa", text: "Estudios y menciones a la novela fundacional." }
    ],
    wiki: { allow: true }
  },
  {
    id: "ricardo_jaimes_freyre",
    aliases: ["ricardo jaimes freyre", "jaimes freyre", "castalia b\xE1rbara", "castalia barbara", "los sue\xF1os son vida", "leyes de la versificaci\xF3n castellana"],
    bio: "Poeta boliviano (1868\u20131933); figura central del modernismo hispanoamericano.",
    guide: "Obras: 'Castalia b\xE1rbara' (1899), 'Los sue\xF1os son vida' (1917), 'Leyes de la versificaci\xF3n castellana' (1912). Cofund\xF3 con Rub\xE9n Dar\xEDo la Revista de Am\xE9rica (Buenos Aires, 1894). Renov\xF3 la m\xE9trica castellana con inspiraci\xF3n en mitolog\xEDa n\xF3rdica.",
    ctx: [
      { title: "Ricardo Jaimes Freyre en Ecd\xF3tica", url: "https://ecdotica.com/?s=Jaimes%20Freyre", text: "Art\xEDculos y estudios sobre el modernista boliviano." }
    ],
    wiki: { allow: true }
  },
  {
    id: "oscar_alfaro",
    aliases: ["\xF3scar alfaro", "oscar alfaro", "alfaro tarije\xF1o", "alfabeto de las estrellas", "rondas para ni\xF1os", "rondas para ninos"],
    bio: "Poeta boliviano (1921\u20131963); pionero de la literatura infantil en Bolivia.",
    guide: "Obras: 'Alfabeto de las estrellas' (1953), 'Rondas para ni\xF1os'. Considerado el m\xE1s importante poeta infantil boliviano. Nacido en Tarija. Muri\xF3 a los 41 a\xF1os; su obra sigue siendo referencia en educaci\xF3n primaria.",
    ctx: [
      { title: "\xD3scar Alfaro en Ecd\xF3tica", url: "https://ecdotica.com/?s=%C3%93scar%20Alfaro", text: "Referencias sobre el poeta tarije\xF1o." }
    ],
    wiki: { allow: true }
  },
  {
    id: "nestor_taboada_teran",
    aliases: ["n\xE9stor taboada ter\xE1n", "nestor taboada teran", "taboada ter\xE1n", "taboada teran", "el precio del esta\xF1o", "el precio del estano", "manchay puytu", "manchaypuytu", "angelina yupanqui"],
    bio: "Narrador boliviano (1929\u20132014); narrativa minera, ind\xEDgena y social.",
    guide: "Obras: 'Angelina Yupanqui' (1955), 'El precio del esta\xF1o' (1960), 'Manchay Puytu: el amor que quiso ocultar la iglesia' (1977). Explor\xF3 la identidad ind\xEDgena y la historia minera. Continuador del indigenismo social boliviano.",
    ctx: [
      { title: "N\xE9stor Taboada Ter\xE1n en Ecd\xF3tica", url: "https://ecdotica.com/?s=Taboada%20Ter%C3%A1n", text: "Notas y referencias sobre el autor." }
    ],
    wiki: { allow: true }
  },
  {
    id: "gonzalo_lema",
    aliases: ["gonzalo lema", "lema", "chungar\xE1", "chungara", "la mudanza del cangrejo"],
    bio: "Narrador boliviano (1959); narrativa urbana cochabambina, policial y humor negro.",
    guide: "Obras: 'La mudanza del cangrejo' (1993), 'Chungar\xE1' (2008). Uno de los narradores m\xE1s importantes de Cochabamba; mezcla policial con humor y reflexi\xF3n social. Tambi\xE9n periodista y columnista.",
    ctx: [
      { title: "Gonzalo Lema en Ecd\xF3tica", url: "https://ecdotica.com/?s=Gonzalo%20Lema", text: "Art\xEDculos y referencias sobre el autor." }
    ],
    wiki: { allow: true }
  },
  {
    id: "ramon_rocha_monroy",
    aliases: ["ram\xF3n rocha monroy", "ramon rocha monroy", "rocha monroy", "el run-run de la calavera", "el runrun de la calavera", "potos\xED 1600", "potosi 1600", "la ex"],
    bio: "Narrador y periodista boliviano (1950); historia colonial, humor y denuncia social.",
    guide: "Obras: 'El run-run de la calavera' (2003), 'Potos\xED 1600' (2008), 'La ex' (2012). Voz fundamental de Cochabamba; mezcla historia, humor negro y cr\xF3nica social. Tambi\xE9n columnista de larga trayectoria.",
    ctx: [
      { title: "Ram\xF3n Rocha Monroy en Ecd\xF3tica", url: "https://ecdotica.com/?s=Rocha%20Monroy", text: "Notas y referencias sobre el narrador cochabambino." }
    ],
    wiki: { allow: true }
  },
  {
    id: "juan_de_recacoechea",
    aliases: ["juan de recacoechea", "recacoechea", "american visa", "american v\xEDsa", "el inmortal de tiahuanacu"],
    bio: "Narrador boliviano (1942\u20132019); pionero de la novela negra boliviana.",
    guide: "Obra principal: 'American Visa' (1994), traducida a varios idiomas y adaptada al cine boliviano (dir. Juan Carlos Valdivia, 2005). Tambi\xE9n escribi\xF3 'El inmortal de Tiahuanacu' (2003). Considerado fundador del thriller boliviano contempor\xE1neo.",
    ctx: [
      { title: "Juan de Recacoechea en Ecd\xF3tica", url: "https://ecdotica.com/?s=Recacoechea", text: "Referencias sobre el autor y American Visa." },
      { title: "American Visa \u2013 refs.", url: "https://ecdotica.com/?s=American%20Visa", text: "Menciones a la novela y su adaptaci\xF3n cinematogr\xE1fica." }
    ],
    wiki: { allow: true }
  },
  {
    id: "editorial_plural",
    aliases: ["plural", "editorial plural", "plural editores"],
    bio: "Sello editorial pace\xF1o; ciencias sociales, ensayo, historia y narrativa boliviana.",
    guide: "Editorial Plural: uno de los sellos editoriales m\xE1s importantes de Bolivia, con sede en La Paz. Especializado en ciencias sociales, historia, ensayo y narrativa boliviana.",
    ctx: [
      { title: "Editorial Plural en Ecd\xF3tica", url: "https://ecdotica.com/?s=Plural", text: "T\xEDtulos y menciones de la editorial." }
    ],
    wiki: { allow: true }
  }
];
function disambiguatePazSoldan(query) {
  const q = norm(query);
  if (!/\bpaz\s+soldan\b/.test(q) && !/\bpaz\s+soldán\b/.test(q)) return null;
  if (/\bmarcelo\b/.test(q)) return "marcelo_paz_soldan";
  if (/\bedmundo\b/.test(q)) return "edmundo_paz_soldan";
  return null;
}
__name(disambiguatePazSoldan, "disambiguatePazSoldan");
function findCanonByBestAlias(query) {
  const qn = norm(query);
  let best = null;
  for (const item of CANON) {
    for (const a of item.aliases || []) {
      const an = norm(a);
      if (an && qn.includes(an)) {
        if (!best || an.length > best.alias.length) best = { item, alias: an };
      }
    }
  }
  return best ? best.item : null;
}
__name(findCanonByBestAlias, "findCanonByBestAlias");
function findCanon(query) {
  const dis = disambiguatePazSoldan(query);
  if (dis) return CANON.find((x) => x.id === dis) || null;
  return findCanonByBestAlias(query);
}
__name(findCanon, "findCanon");
function splitSents(t) {
  return String(t || "").split(/(?<=[.!?])\s+/);
}
__name(splitSents, "splitSents");
var GUARDS = {
  liliana_colanzi: {
    ban: [
      /las cosas que perdimos en el fuego/i,
      /p[aá]jaros en la boca/i
    ],
    replace: [
      { pattern: /\bnovela(s)?\b/gi, with: "libro$1 de cuentos" }
    ]
  },
  ricardo_torrejon: {
    ban: [
      /\bnacido en la paz\b/i,
      /\bpoeta(s)?\b/i,
      /\bpoes[ií]a\b/i
    ],
    replace: [
      { pattern: /\bnovela(s)?\b/gi, with: "ensayo(s)" }
    ]
  },
  nestor_taboada_teran: {
    ban: [],
    replace: [
      { pattern: /\(1929[–—-]1989\)/g, with: "(1929\u20132014)" },
      { pattern: /\b1929[–—-]1989\b/g, with: "1929\u20132014" }
    ]
  },
  nataniel_aguirre: {
    ban: [],
    replace: [
      { pattern: /\(1832[–—-]1888\)/g, with: "(1843\u20131888)" },
      { pattern: /\b1832[–—-]1888\b/g, with: "1843\u20131888" }
    ]
  },
  oscar_alfaro: {
    ban: [],
    replace: [
      { pattern: /\(1921[–—-]1962\)/g, with: "(1921\u20131963)" },
      { pattern: /\b1921[–—-]1962\b/g, with: "1921\u20131963" }
    ]
  },
  juan_de_recacoechea: {
    ban: [],
    replace: [
      { pattern: /\(1948[–—-]2019\)/g, with: "(1942\u20132019)" },
      { pattern: /\b1948[–—-]2019\b/g, with: "1942\u20132019" }
    ]
  },
  ricardo_jaimes_freyre: {
    ban: [],
    replace: [
      { pattern: /[Nn]aci[oó] en La Paz/g, with: "Naci\xF3 en Tacna" }
    ]
  },
  ramon_rocha_monroy: {
    ban: [],
    replace: [
      { pattern: /Rocha Monrroy/g, with: "Rocha Monroy" }
    ]
  }
};
function sanitizeAnswer(ans, hit) {
  if (!hit || !GUARDS[hit.id]) return ans;
  const g = GUARDS[hit.id];
  let sents = splitSents(ans).filter((s) => !g.ban.some((re) => re.test(s)));
  let out = sents.join(" ");
  for (const r of g.replace || []) {
    out = out.replace(r.pattern, r.with);
  }
  return out;
}
__name(sanitizeAnswer, "sanitizeAnswer");
function buildSystemPrompt({ mode = "hybrid", student = false, depth = "profundo" } = {}) {
  const base = [
    "Eres Ecdotic\xF3n, asistente editorial de Nuevo Milenio (Bolivia).",
    "Tono: profesional, preciso y did\xE1ctico; \xFAtil para estudiantes y docentes.",
    mode === "strict" ? "REGLA: responde SOLO con hechos del CONTEXTO. Si falta un dato, di: 'No tengo evidencia en el cat\xE1logo'." : mode === "hybrid" ? "REGLA: prioriza el CONTEXTO (Ecd\xF3tica/Wikipedia si autorizada). Si falta un dato b\xE1sico, puedes aportar s\xEDntesis general breve expl\xEDcita como '(s\xEDntesis general)'. Evita especular." : "REGLA: puedes responder con conocimiento general cuando sea pertinente, evitando afirmaciones dudosas.",
    "Incluye 1\u20133 enlaces del CONTEXTO (Ecd\xF3tica o Wikipedia) al final."
  ];
  if (student) base.push("Cuando proceda, a\xF1ade 1\u20132 actividades breves para aula (no m\xE1s de 2 l\xEDneas).");
  if (depth === "profundo") base.push("Extensi\xF3n objetivo: 150\u2013240 palabras; estructura en 2\u20134 p\xE1rrafos o vi\xF1etas.");
  if (depth === "medio") base.push("Extensi\xF3n objetivo: 90\u2013140 palabras.");
  if (depth === "breve") base.push("Extensi\xF3n objetivo: 50\u201380 palabras.");
  return base.join(" ");
}
__name(buildSystemPrompt, "buildSystemPrompt");
async function answerWithContext(env, { query, docs, mode = "hybrid", student = false, depth = "profundo", history = [], hit = null }) {
  if ((!docs || docs.length === 0) && mode !== "strict" && isWikipediaAllowed({ env, query, hit })) {
    const wikiDoc = await searchWikipedia(query);
    if (wikiDoc) docs = [wikiDoc];
  }
  if ((!docs || docs.length === 0) && mode === "strict") {
    const link = `<a href="https://ecdotica.com/?s=${encodeURIComponent(query)}">Ver resultados en Ecd\xF3tica</a>`;
    return json({ answer: `No tengo evidencia en el cat\xE1logo para responder con precisi\xF3n. ${link}` });
  }
  if (!docs || docs.length === 0) docs = [];
  const contexto = docs.map((d, i) => `[${i + 1}] ${d.title}
URL: ${d.url}
Fragmento: ${d.text}`).join("\n\n");
  const messages = [];
  messages.push({ role: "system", content: buildSystemPrompt({ mode, student, depth }) });
  if (contexto) messages.push({ role: "system", content: "CONTEXTO (usar prioritariamente):\n\n" + contexto });
  if (Array.isArray(history) && history.length) {
    for (const m of history) {
      if (m && typeof m.content === "string" && (m.role === "user" || m.role === "assistant")) {
        messages.push({ role: m.role, content: m.content });
      }
    }
  }
  messages.push({ role: "user", content: `Pregunta: ${query}` });
  let data;
  try {
    data = await callOpenAIWithTimeout(env, messages, 25e3, { max_tokens: 1200, temperature: 0.1 });
  } catch (e) {
    if (e.message === "timeout") {
      return json({ answer: "(El servicio tard\xF3 demasiado en responder. Intenta con una pregunta m\xE1s breve.)" }, 504);
    }
    if (e.message?.includes("429")) {
      return json({ answer: "(El servicio est\xE1 experimentando alta demanda. Por favor intenta en 1-2 minutos.)" }, 429);
    }
    if (e.message?.includes("400")) {
      return json({ answer: "(Consulta demasiado extensa. Intenta con una pregunta m\xE1s concisa.)" }, 400);
    }
    console.error("Error OpenAI:", e.message);
    return json({ answer: "(Error temporal al contactar el servicio. Intenta nuevamente en unos segundos.)" }, 502);
  }
  let answer = data?.choices?.[0]?.message?.content ?? "(sin respuesta)";
  answer = sanitizeAnswer(answer, hit);
  return json({ answer, reply: answer });
}
__name(answerWithContext, "answerWithContext");
function bienvenida() {
  const msg = `Soy Ecdotic\xF3n. Te ayudo con autores, obras, corrientes y contexto hist\xF3rico. Prueba: "Giovanna Rivero", "Rodrigo Hasb\xFAn", "Magela Baudoin", "Sebasti\xE1n Antezana", "Hermanos Loayza", "Liliana Colanzi". Visita el <a href="https://ecdotica.com">cat\xE1logo</a>.`;
  return json({ answer: msg, reply: msg });
}
__name(bienvenida, "bienvenida");
function buildWidgetCSS(theme = "auto") {
  const t = String(theme || "auto").toLowerCase();
  const base = `
/* Ecdotic\xF3n: CSS m\xF3vil con m\xE1xima especificidad y contraste */
.ecdoticon,
.ecdoticon *,
.ecdoticon *::before,
.ecdoticon *::after {
  box-sizing: border-box;
  color: var(--ecd-fg) !important;
}

.ecdoticon {
  --ecd-bg: #ffffff;
  --ecd-fg: #222222;
  --ecd-accent: #0b57d0;
  background: var(--ecd-bg) !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  line-height: 1.6;
  padding: 16px;
}

.ecdoticon.ecd-theme-dark {
  --ecd-bg: #181818;
  --ecd-fg: #f0f0f0;
  --ecd-accent: #ffd166;
}

@media (max-width: 768px) {
  .ecdoticon {
    font-size: 16px !important;
    padding: 14px !important;
  }
  
  .ecdoticon .bubble,
  .ecdoticon .message {
    background: #f7f7f7 !important;
    color: var(--ecd-fg) !important;
    padding: 12px 14px !important;
    border-radius: 10px !important;
    margin: 8px 0 !important;
    line-height: 1.5 !important;
  }
  
  .ecdoticon.ecd-theme-dark .bubble,
  .ecdoticon.ecd-theme-dark .message {
    background: #252525 !important;
  }
  
  .ecdoticon input,
  .ecdoticon textarea,
  .ecdoticon button {
    background: #ffffff !important;
    color: #222222 !important;
    border: 2px solid #dddddd !important;
    padding: 12px !important;
    font-size: 16px !important;
    border-radius: 8px !important;
    -webkit-appearance: none;
    appearance: none;
  }
  
  .ecdoticon.ecd-theme-dark input,
  .ecdoticon.ecd-theme-dark textarea,
  .ecdoticon.ecd-theme-dark button {
    background: #1e1e1e !important;
    color: #f0f0f0 !important;
    border: 2px solid #444444 !important;
  }
  
  .ecdoticon ::placeholder {
    color: #666666 !important;
    opacity: 1 !important;
  }
  
  .ecdoticon.ecd-theme-dark ::placeholder {
    color: #aaaaaa !important;
  }
  
  .ecdoticon a {
    color: var(--ecd-accent) !important;
    text-decoration: underline !important;
    font-weight: 500 !important;
  }
  
  .ecdoticon a:visited {
    color: var(--ecd-accent) !important;
  }
}

@media (min-width: 769px) {
  .ecdoticon {
    padding: 20px !important;
    font-size: 15px;
  }
  
  .ecdoticon .bubble {
    background: #f9f9f9 !important;
    padding: 14px 18px !important;
    border-radius: 10px !important;
  }
  
  .ecdoticon.ecd-theme-dark .bubble {
    background: #252525 !important;
  }
  
  .ecdoticon input,
  .ecdoticon textarea,
  .ecdoticon button {
    background: #ffffff !important;
    color: #222222 !important;
    border: 1px solid #cccccc !important;
    padding: 10px 14px !important;
    font-size: 15px !important;
    border-radius: 6px !important;
  }
  
  .ecdoticon.ecd-theme-dark input,
  .ecdoticon.ecd-theme-dark textarea,
  .ecdoticon.ecd-theme-dark button {
    background: #1e1e1e !important;
    color: #f0f0f0 !important;
    border: 1px solid #444444 !important;
  }
}
`;
  if (t === "auto") {
    return base + `
@media (prefers-color-scheme: dark) {
  .ecdoticon {
    --ecd-bg: #181818;
    --ecd-fg: #f0f0f0;
    --ecd-accent: #ffd166;
  }
  .ecdoticon .bubble {
    background: #252525 !important;
  }
  .ecdoticon input,
  .ecdoticon textarea,
  .ecdoticon button {
    background: #1e1e1e !important;
    color: #f0f0f0 !important;
    border-color: #444444 !important;
  }
}
`;
  }
  if (t === "light") {
    return base + `
.ecdoticon {
  --ecd-bg: #ffffff !important;
  --ecd-fg: #222222 !important;
  --ecd-accent: #0b57d0 !important;
}
.ecdoticon .bubble {
  background: #f7f7f7 !important;
}
.ecdoticon input,
.ecdoticon textarea,
.ecdoticon button {
  background: #ffffff !important;
  color: #222222 !important;
  border-color: #dddddd !important;
}
`;
  }
  if (t === "dark") {
    return base + `
.ecdoticon {
  --ecd-bg: #181818 !important;
  --ecd-fg: #f0f0f0 !important;
  --ecd-accent: #ffd166 !important;
}
.ecdoticon .bubble {
  background: #252525 !important;
}
.ecdoticon input,
.ecdoticon textarea,
.ecdoticon button {
  background: #1e1e1e !important;
  color: #f0f0f0 !important;
  border-color: #444444 !important;
}
`;
  }
  return base;
}
__name(buildWidgetCSS, "buildWidgetCSS");
var ecdoticon_default = {
  async fetch(req, env) {
    if (!("ALLOW_WIKIPEDIA" in env)) env.ALLOW_WIKIPEDIA = "true";
    const url = new URL(req.url);
    const p = url.pathname;
    if (req.method === "OPTIONS") return new Response(null, { headers: CORS });
    if (req.method === "POST" && req.headers.get("content-length") > 2e4) {
      return json({ answer: "(Consulta demasiado larga. M\xE1ximo 20KB.)" }, 413);
    }
    if (p === "/health") {
      const health = {
        status: "ok",
        version: "1.1.0",
        timestamp: (/* @__PURE__ */ new Date()).toISOString(),
        uptime: Date.now(),
        checks: {
          openai: !!env.OPENAI_API_KEY,
          environment: !!env
        },
        endpoints: {
          health: "/health",
          chat: "/api/ecdoticon/chat",
          widget: "/api/ecdoticon/widget.css",
          diagnostic: "/diag/openai"
        }
      };
      log("info", "health_check", { status: "ok" });
      return json(health);
    }
    if (p === "/diag/openai") {
      if (!env.OPENAI_API_KEY) return json({ ok: false, error: "OPENAI_API_KEY missing" }, 500);
      return json({
        ok: true,
        model: env.OPENAI_MODEL || "gpt-4o-mini",
        allow_wikipedia: String(env.ALLOW_WIKIPEDIA || "").toLowerCase() === "true",
        wiki_whitelist_size: getWikiWhitelist(env).size
      });
    }
    if (p === "/api/ecdoticon/widget.css") {
      const theme = url.searchParams.get("theme") || "auto";
      return css(buildWidgetCSS(theme));
    }
    if ((p === "/api/ecdoticon/chat" || p === "/chat") && (req.method === "GET" || req.method === "POST")) {
      let q = "";
      let mode = "hybrid";
      let depth = "profundo";
      let student = false;
      let hist = [];
      let max_docs = 12;
      if (req.method === "GET") {
        q = url.searchParams.get("q") || "";
        mode = url.searchParams.get("mode") || mode;
        depth = url.searchParams.get("depth") || depth;
        student = (url.searchParams.get("student") || "false") === "true";
        max_docs = Math.max(1, Math.min(15, parseInt(url.searchParams.get("max_docs") || "12", 10)));
        try {
          hist = JSON.parse(url.searchParams.get("history") || "[]");
        } catch {
          hist = [];
        }
      } else {
        try {
          const body = await req.json();
          q = body?.query || body?.message || "";
          mode = body?.mode || mode;
          depth = body?.depth || depth;
          student = !!body?.student;
          hist = Array.isArray(body?.history) ? body.history : [];
          max_docs = Math.max(1, Math.min(15, parseInt(body?.max_docs || 12, 10)));
        } catch {
          return json({ answer: "(Error en el servidor: body inv\xE1lido)" }, 500);
        }
      }
      const hit = findCanon(q);
      if (!q || !hit && (GREETING.test(q) || q.trim().split(/\s+/).length < 2)) return bienvenida();
      let docs = [];
      if (hit) {
        if (hit.guide) {
          docs.push({ title: "Nota editorial", url: hit.ctx?.[0]?.url || "https://ecdotica.com/", text: hit.guide });
        }
        if (Array.isArray(hit.ctx)) docs = docs.concat(hit.ctx);
      }
      const extra = await searchEcdotica(q);
      docs = dedupeByUrl([...docs, ...extra]).slice(0, max_docs);
      const effMode = hit && hit.strict ? "strict" : mode;
      return await answerWithContext(env, { query: q, docs, mode: effMode, student, depth, history: hist, hit });
    }
    if (p === "/") {
      log("info", "root_endpoint_accessed", {});
      return json({
        service: "Ecdoticon API",
        version: "1.1.0",
        description: "An\xE1lisis inteligente de manuscritos con AI",
        status: "operational",
        endpoints: {
          health: "/health",
          chat: {
            path: "/api/ecdoticon/chat",
            methods: ["GET", "POST"],
            params: ["q", "mode", "depth", "student", "history"]
          },
          widget: "/api/ecdoticon/widget.css",
          diagnostic: "/diag/openai"
        },
        documentation: "https://ecdotica.com/docs"
      });
    }
    return json({ error: "Not found" }, 404);
  }
};
export {
  ecdoticon_default as default
};
//# sourceMappingURL=ecdoticon.js.map
