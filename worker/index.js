var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// worker/plagiarism-detector.js
function generateNGrams(text, n = 3) {
  const words = text.toLowerCase().replace(/[^a-záéíóúñü\s]/g, "").split(/\s+/).filter((w) => w.length > 2);
  const ngrams = [];
  for (let i = 0; i <= words.length - n; i++) {
    ngrams.push(words.slice(i, i + n).join(" "));
  }
  return ngrams;
}
__name(generateNGrams, "generateNGrams");
function cosineSimilarity(ngrams1, ngrams2) {
  const set1 = new Set(ngrams1);
  const set2 = new Set(ngrams2);
  const intersection = new Set([...set1].filter((x) => set2.has(x)));
  const union = /* @__PURE__ */ new Set([...set1, ...set2]);
  if (set1.size === 0 || set2.size === 0) return 0;
  return intersection.size / Math.sqrt(set1.size * set2.size);
}
__name(cosineSimilarity, "cosineSimilarity");
function extractKeyPhrases(text, maxPhrases = 18) {
  const cleanText = text.replace(/\s+/g, " ").trim();
  const sentences = cleanText.split(/[.!?]+/).filter((s) => s.trim().length > 60);
  if (sentences.length === 0) return [];
  const allFragments = [];
  const fullSentences = sentences.filter((s) => {
    const wordCount = s.split(/\s+/).length;
    return wordCount >= 10 && wordCount <= 30;
  }).map((s) => ({ phrase: s.trim(), type: "full", size: s.split(/\s+/).length }));
  allFragments.push(...fullSentences);
  const longSentences = sentences.filter((s) => s.split(/\s+/).length > 30);
  longSentences.forEach((s) => {
    const words = s.split(/\s+/);
    const mid = Math.floor(words.length / 2);
    allFragments.push({
      phrase: words.slice(0, mid).join(" ").trim(),
      type: "fragment",
      size: mid
    });
    allFragments.push({
      phrase: words.slice(mid).join(" ").trim(),
      type: "fragment",
      size: words.length - mid
    });
  });
  const scoredFragments = allFragments.map((frag) => {
    const words = frag.phrase.toLowerCase().split(/\s+/);
    const uniqueWords = new Set(words);
    const diversity = uniqueWords.size / words.length;
    const hasProperNouns = /[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+/.test(frag.phrase);
    const hasQuotes = /["«»'']/.test(frag.phrase);
    let score = diversity;
    if (hasProperNouns) score += 0.3;
    if (hasQuotes) score += 0.2;
    if (frag.type === "full") score += 0.1;
    return { ...frag, score };
  });
  return scoredFragments.sort((a, b) => b.score - a.score).slice(0, maxPhrases).map((f) => f.phrase);
}
__name(extractKeyPhrases, "extractKeyPhrases");
async function searchPhrase(phrase, apiKey, cseId) {
  const url = `https://www.googleapis.com/customsearch/v1?key=${apiKey}&cx=${cseId}&q=${encodeURIComponent('"' + phrase + '"')}&num=3`;
  try {
    const response = await fetch(url);
    const data = await response.json();
    if (data.items && data.items.length > 0) {
      const phraseNGrams = generateNGrams(phrase);
      const results = data.items.map((item) => {
        const snippetNGrams = generateNGrams(item.snippet);
        const similarity = cosineSimilarity(phraseNGrams, snippetNGrams);
        return {
          title: item.title,
          link: item.link,
          snippet: item.snippet,
          semanticSimilarity: similarity
        };
      });
      return {
        found: true,
        results,
        maxSimilarity: Math.max(...results.map((r) => r.semanticSimilarity))
      };
    }
    return { found: false, results: [], maxSimilarity: 0 };
  } catch (error) {
    console.error("Error searching:", error);
    return { found: false, results: [], maxSimilarity: 0 };
  }
}
__name(searchPhrase, "searchPhrase");
async function detectPlagiarism(text, env) {
  const apiKey = env && env.GOOGLE_API_KEY;
  const cseId = env && env.GOOGLE_SEARCH_ENGINE_ID;
  if (!apiKey || !cseId) {
    console.error("[Ecd\xF3tica] GOOGLE_API_KEY o GOOGLE_SEARCH_ENGINE_ID no configurados en el Worker.");
    return {
      originalidad: 100,
      plagio: 0,
      estado: "Sin verificar",
      coincidencias: [],
      fragmentos_analizados: 0,
      fragmentos_con_plagio: 0,
      version: "3.0-fase1",
      error: "Credenciales de Google no configuradas"
    };
  }
  try {
    const phrases = extractKeyPhrases(text, 18);
    if (phrases.length === 0) {
      return {
        originalidad: 100,
        plagio: 0,
        estado: "Aprobado",
        coincidencias: [],
        fragmentos_analizados: 0,
        fragmentos_con_plagio: 0,
        version: "3.0-fase1"
      };
    }
    console.log(`[Ecd\xF3tica v3.0] Analizando ${phrases.length} fragmentos...`);
    const searchPromises = phrases.map(async (phrase, index) => {
      await new Promise((r) => setTimeout(r, index * 180));
      const result = await searchPhrase(phrase, apiKey, cseId);
      return {
        fragmento: phrase.substring(0, 150) + "...",
        encontrado: result.found,
        similitud_semantica: result.maxSimilarity,
        fuentes: result.found ? result.results : []
      };
    });
    const searchResults = await Promise.all(searchPromises);
    const fragmentsWithMatches = searchResults.filter((r) => r.encontrado);
    const matchCount = fragmentsWithMatches.length;
    const totalPhrases = phrases.length;
    let weightedScore = 0;
    fragmentsWithMatches.forEach((match) => {
      if (match.similitud_semantica > 0.7) weightedScore += 1;
      else if (match.similitud_semantica > 0.5) weightedScore += 0.7;
      else if (match.similitud_semantica > 0.3) weightedScore += 0.4;
      else weightedScore += 0.2;
    });
    const adjustedMatchRatio = weightedScore / totalPhrases;
    const plagioPercentage = Math.min(100, Math.round(adjustedMatchRatio * 90));
    const originalidadPercentage = Math.max(0, Math.round(100 - adjustedMatchRatio * 85));
    console.log(`[Ecd\xF3tica v3.0] Matches: ${matchCount}/${totalPhrases}, Score: ${weightedScore.toFixed(2)}, Originalidad: ${originalidadPercentage}%`);
    const coincidencias = fragmentsWithMatches.filter((m) => m.similitud_semantica > 0.3).map((match, index) => {
      return {
        numero: index + 1,
        fragmento: match.fragmento,
        similitud: Math.round(match.similitud_semantica * 100),
        tipo: match.similitud_semantica > 0.7 ? "Alta" : match.similitud_semantica > 0.5 ? "Media" : "Baja",
        fuentes: match.fuentes.slice(0, 2).map((f) => ({
          titulo: f.title,
          url: f.link,
          extracto: f.snippet.substring(0, 200),
          similitud_semantica: Math.round(f.semanticSimilarity * 100)
        }))
      };
    }).sort((a, b) => b.similitud - a.similitud);
    let estado;
    if (originalidadPercentage >= 90) estado = "Aprobado";
    else if (originalidadPercentage >= 75) estado = "Revisi\xF3n menor";
    else if (originalidadPercentage >= 60) estado = "Sospechoso";
    else estado = "Plagio detectado";
    return {
      originalidad: originalidadPercentage,
      plagio: plagioPercentage,
      estado,
      coincidencias,
      fragmentos_analizados: totalPhrases,
      fragmentos_con_plagio: matchCount,
      coincidencias_significativas: coincidencias.length,
      version: "3.0-fase1",
      mejoras: [
        "An\xE1lisis sem\xE1ntico con n-gramas",
        "Detecci\xF3n de sin\xF3nimos b\xE1sica",
        "18 fragmentos (antes 8)",
        "Scoring ponderado por similitud"
      ]
    };
  } catch (error) {
    console.error("[Ecd\xF3tica v3.0] Error en detecci\xF3n:", error);
    return {
      originalidad: 95,
      plagio: 5,
      estado: "Error en verificaci\xF3n",
      coincidencias: [],
      fragmentos_analizados: 0,
      fragmentos_con_plagio: 0,
      version: "3.0-fase1",
      error: error.message
    };
  }
}
__name(detectPlagiarism, "detectPlagiarism");

// worker/index.js
var index_default = {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    };
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }
    if (url.pathname === "/health" || url.pathname === "/") {
      return new Response(JSON.stringify({
        status: "healthy",
        service: "Ecdotica API",
        version: "3.1.0",
        timestamp: (/* @__PURE__ */ new Date()).toISOString()
      }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    }
    if (url.pathname === "/api/v1/manuscripts/upload" && request.method === "POST") {
      try {
        const formData = await request.formData();
        const file = formData.get("file");
        if (!file) {
          return new Response(JSON.stringify({ error: "No file provided" }), {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" }
          });
        }
        const fn = file.name ? file.name.toLowerCase() : "";
        if (fn.endsWith(".pdf")) {
          return new Response(JSON.stringify({
            error: "PDF_NOT_SUPPORTED",
            message: "El Worker no procesa PDFs. Usa POST /api/v1/manuscripts/upload en api.ecdotica.com (API Python) para archivos PDF.",
            fallback_endpoint: "https://api.ecdotica.com/api/v1/manuscripts/upload"
          }), {
            status: 415,
            headers: { ...corsHeaders, "Content-Type": "application/json" }
          });
        }
        const content = await file.text();
        const analysis = await analyzeManuscript(content, env);
        return new Response(JSON.stringify(analysis), {
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      } catch (error) {
        return new Response(JSON.stringify({
          error: "Error processing file",
          details: error.message
        }), {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }
    }
    if (url.pathname === "/api/v1/manuscripts/submit" && request.method === "POST") {
      try {
        const data = await request.json();
        const text = data.text || data.content;
        if (!text) {
          return new Response(JSON.stringify({ error: "No text provided" }), {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" }
          });
        }
        const analysis = await analyzeManuscript(text, env);
        return new Response(JSON.stringify(analysis), {
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      } catch (error) {
        return new Response(JSON.stringify({
          error: "Error processing text",
          details: error.message
        }), {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }
    }
    return new Response("Not Found", { status: 404 });
  }
};
async function analyzeManuscript(text, env) {
  const cleanText = text.replace(/\s+/g, " ").trim();
  const words = cleanText.split(/\s+/).filter((w) => w.length > 0);
  const wordCount = words.length;
  const sentences = cleanText.split(/[.!?]+/).filter((s) => s.trim().length > 0);
  const sentenceCount = sentences.length;
  const paragraphs = cleanText.split(/\n\n+/).filter((p) => p.trim().length > 0);
  const paragraphCount = Math.max(paragraphs.length, Math.floor(sentenceCount / 5));
  const lowercaseWords = words.map((w) => w.toLowerCase().replace(/[^a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1\u00fc]/gi, ""));
  const uniqueWords = new Set(lowercaseWords.filter((w) => w.length > 0));
  const vocabularyDiversity = uniqueWords.size / wordCount * 100;
  const ttr = uniqueWords.size / wordCount;
  const wordFreq = {};
  lowercaseWords.forEach((w) => {
    if (w.length > 3) {
      wordFreq[w] = (wordFreq[w] || 0) + 1;
    }
  });
  const topWords = Object.entries(wordFreq).sort((a, b) => b[1] - a[1]).slice(0, 10).map(([word, count]) => ({ palabra: word, frecuencia: count }));
  const repetitiveWords = topWords.filter((w) => w.frecuencia / wordCount > 0.02);
  const adjetivos = words.filter(
    (w) => /(?:os[oa]|iv[oa]|bl[ea]|nt[ea]|d[oa])$/i.test(w) || /(?:ante|ente|ible|able)$/i.test(w)
  );
  const adjectiveRatio = adjetivos.length / wordCount * 100;
  const adverbiosMente = words.filter((w) => /mente$/i.test(w));
  const adverbRatio = adverbiosMente.length / wordCount * 100;
  const dialogLines = cleanText.match(/["](.*?)["]/g) || [];
  const dialogRatio = dialogLines.join(" ").split(/\s+/).length / wordCount * 100;
  const paragraphLengths = paragraphs.map((p) => p.split(/\s+/).length);
  const avgParagraphLength = paragraphLengths.reduce((a, b) => a + b, 0) / paragraphCount;
  const longParagraphs = paragraphLengths.filter((l) => l > 250).length;
  const sentenceLengths = sentences.map((s) => s.split(/\s+/).length);
  const sentenceLengthVariance = calculateVariance(sentenceLengths);
  const semicolonCount = (cleanText.match(/;/g) || []).length;
  const ellipsisCount = (cleanText.match(/\.\.\.+/g) || []).length;
  const dashCount = (cleanText.match(/[\u2014\u2013]/g) || []).length;
  const complexWords = words.filter((w) => countSyllables(w) > 3);
  const complexWordRatio = complexWords.length / wordCount * 100;
  const avgWordsPerSentence = wordCount / sentenceCount;
  const avgSyllablesPerWord = words.reduce((sum, w) => sum + countSyllables(w), 0) / wordCount;
  const fleschScore = 206.835 - 1.015 * avgWordsPerSentence - 60 * avgSyllablesPerWord;
  let readingLevel;
  if (fleschScore >= 90) readingLevel = "Muy facil (5to grado)";
  else if (fleschScore >= 80) readingLevel = "Facil (6to grado)";
  else if (fleschScore >= 70) readingLevel = "Bastante facil (7mo grado)";
  else if (fleschScore >= 60) readingLevel = "Normal (8vo-9no grado)";
  else if (fleschScore >= 50) readingLevel = "Bastante dificil (10mo-12vo grado)";
  else if (fleschScore >= 30) readingLevel = "Dificil (Universidad)";
  else readingLevel = "Muy dificil (Posgrado)";
  const connectiveWords = [
    "sin embargo",
    "no obstante",
    "ademas",
    "por lo tanto",
    "en consecuencia",
    "asimismo",
    "por otro lado",
    "en primer lugar",
    "finalmente",
    "en resumen",
    "por ejemplo",
    "es decir",
    "en otras palabras",
    "aunque",
    "mientras que"
  ];
  const connectivesFound = connectiveWords.filter((c) => cleanText.toLowerCase().includes(c)).length;
  const connectiveRatio = connectivesFound / paragraphCount * 100;
  const pastTenseWords = words.filter((w) => /(?:aba|aban|ia|ian|o|aron)$/i.test(w));
  const presentTenseWords = words.filter((w) => /(?:o|as|a|amos|ais|an)$/i.test(w) && !/(?:aba|aban)$/i.test(w));
  const verbRatio = {
    pasado: pastTenseWords.length / wordCount * 100,
    presente: presentTenseWords.length / wordCount * 100
  };
  const properNouns = [];
  const textWords = cleanText.split(/\s+/);
  for (let i = 1; i < textWords.length - 1; i++) {
    const word = textWords[i];
    if (/^[A-Z\u00c1\u00c9\u00cd\u00d3\u00da][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1]+$/.test(word) && textWords[i - 1].slice(-1) !== ".") {
      properNouns.push(word);
    }
  }
  const uniqueProperNouns = [...new Set(properNouns)];
  let qualityScore = 30;
  if (wordCount >= 8e4) qualityScore += 15;
  else if (wordCount >= 5e4) qualityScore += 12;
  else if (wordCount >= 3e4) qualityScore += 8;
  else if (wordCount >= 1e4) qualityScore += 4;
  else if (wordCount < 3e3) qualityScore -= 25;
  else if (wordCount < 5e3) qualityScore -= 15;
  else if (wordCount < 8e3) qualityScore -= 8;
  if (avgWordsPerSentence >= 12 && avgWordsPerSentence <= 22) qualityScore += 8;
  else if (avgWordsPerSentence >= 10 && avgWordsPerSentence <= 25) qualityScore += 4;
  else if (avgWordsPerSentence < 8) qualityScore -= 10;
  else if (avgWordsPerSentence > 35) qualityScore -= 12;
  else if (avgWordsPerSentence > 28) qualityScore -= 6;
  const avgSentencesPerParagraph = sentenceCount / paragraphCount;
  if (avgSentencesPerParagraph >= 3 && avgSentencesPerParagraph <= 6) qualityScore += 8;
  else if (avgSentencesPerParagraph >= 2 && avgSentencesPerParagraph <= 8) qualityScore += 4;
  else if (avgSentencesPerParagraph < 2) qualityScore -= 8;
  else if (avgSentencesPerParagraph > 12) qualityScore -= 10;
  if (vocabularyDiversity > 50) qualityScore += 12;
  else if (vocabularyDiversity > 40) qualityScore += 8;
  else if (vocabularyDiversity > 35) qualityScore += 4;
  else if (vocabularyDiversity < 20) qualityScore -= 15;
  else if (vocabularyDiversity < 25) qualityScore -= 10;
  else if (vocabularyDiversity < 30) qualityScore -= 5;
  if (ttr > 0.55) qualityScore += 5;
  else if (ttr > 0.45) qualityScore += 2;
  else if (ttr < 0.25) qualityScore -= 8;
  if (fleschScore >= 40 && fleschScore <= 65) qualityScore += 8;
  else if (fleschScore >= 35 && fleschScore <= 70) qualityScore += 4;
  else if (fleschScore > 85) qualityScore -= 5;
  else if (fleschScore < 20) qualityScore -= 12;
  else if (fleschScore < 30) qualityScore -= 6;
  if (repetitiveWords.length > 5) qualityScore -= 15;
  else if (repetitiveWords.length > 3) qualityScore -= 10;
  else if (repetitiveWords.length > 1) qualityScore -= 5;
  if (connectiveRatio >= 35) qualityScore += 10;
  else if (connectiveRatio >= 25) qualityScore += 6;
  else if (connectiveRatio >= 15) qualityScore += 3;
  else if (connectiveRatio < 8) qualityScore -= 12;
  else if (connectiveRatio < 12) qualityScore -= 6;
  if (sentenceLengthVariance > 30) qualityScore += 6;
  else if (sentenceLengthVariance > 20) qualityScore += 4;
  else if (sentenceLengthVariance < 8) qualityScore -= 10;
  else if (sentenceLengthVariance < 12) qualityScore -= 5;
  if (dialogRatio > 15 && dialogRatio < 35) qualityScore += 5;
  else if (dialogRatio > 10 && dialogRatio < 40) qualityScore += 2;
  else if (dialogRatio > 55) qualityScore -= 5;
  if (adjectiveRatio >= 8 && adjectiveRatio <= 14) qualityScore += 5;
  else if (adjectiveRatio < 4) qualityScore -= 5;
  else if (adjectiveRatio > 22) qualityScore -= 8;
  if (adverbRatio > 8) qualityScore -= 10;
  else if (adverbRatio > 5) qualityScore -= 5;
  else if (adverbRatio < 2) qualityScore += 3;
  if (complexWordRatio >= 15 && complexWordRatio <= 25) qualityScore += 5;
  else if (complexWordRatio > 35) qualityScore -= 12;
  else if (complexWordRatio > 30) qualityScore -= 6;
  else if (complexWordRatio < 8) qualityScore -= 5;
  qualityScore = Math.max(0, Math.min(100, qualityScore));
  let plagiarismResult;
  try {
    plagiarismResult = await detectPlagiarism(text, env);
  } catch (error) {
    console.error("Error en detecci\xF3n de plagio:", error);
    plagiarismResult = {
      originalidad: 100,
      plagio: 0,
      estado: "Sin verificar",
      coincidencias: [],
      fragmentos_analizados: 0,
      fragmentos_con_plagio: 0,
      version: "3.0-fase1",
      error: error.message
    };
  }
  const issues = [];
  if (wordCount < 3e3) issues.push("Manuscrito muy corto (menos de 3,000 palabras) - insuficiente para publicacion");
  else if (wordCount < 8e3) issues.push("Manuscrito corto - considere expandir");
  if (wordCount > 15e4) issues.push("Manuscrito muy extenso - considere dividir en volumenes");
  if (avgWordsPerSentence < 8) issues.push("Oraciones demasiado cortas - estilo fragmentado");
  if (avgWordsPerSentence > 35) issues.push("Oraciones excesivamente largas - dificultan lectura");
  if (vocabularyDiversity < 25) issues.push("CRITICO: Vocabulario muy limitado - diversifique el lexico");
  else if (vocabularyDiversity < 30) issues.push("Vocabulario limitado - mejore diversidad lexica");
  if (repetitiveWords.length > 2) {
    issues.push("Palabras repetitivas: " + repetitiveWords.map((w) => w.palabra).join(", "));
  }
  if (paragraphCount < 10 && wordCount > 5e3) issues.push("Texto necesita mejor division en parrafos");
  if (longParagraphs > paragraphCount * 0.2) issues.push("Demasiados parrafos excesivamente largos");
  if (fleschScore < 25) issues.push("CRITICO: Texto demasiado complejo - simplificar lenguaje");
  if (complexWordRatio > 35) issues.push("Exceso de palabras complejas - revisar accesibilidad");
  if (adverbRatio > 6) issues.push("Uso excesivo de adverbios en -mente");
  if (adjectiveRatio < 4) issues.push("Texto plano - agregar mas descripciones");
  if (adjectiveRatio > 20) issues.push("Demasiados adjetivos - simplificar prosa");
  if (connectiveRatio < 10) issues.push("CRITICO: Falta cohesion - agregar conectores entre ideas");
  if (sentenceLengthVariance < 10) issues.push("Oraciones muy uniformes - variar el ritmo");
  let editorialStatus;
  let recommendation;
  if (qualityScore >= 75 && wordCount >= 4e4 && issues.length <= 1) {
    editorialStatus = "ACCEPTED";
    recommendation = "Manuscrito de alta calidad editorial. Recomendado para publicacion con edicion ligera de estilo.";
  } else if (qualityScore >= 65 && wordCount >= 3e4 && issues.length <= 2) {
    editorialStatus = "ACCEPTED_WITH_REVISIONS";
    recommendation = "Manuscrito aceptado condicionalmente. Requiere revisiones menores antes de publicacion.";
  } else if (qualityScore >= 55 && wordCount >= 2e4 && issues.length <= 4) {
    editorialStatus = "REVIEW_NEEDED";
    recommendation = "Manuscrito con potencial. Requiere revision editorial moderada y ajustes estructurales.";
  } else if (qualityScore >= 40 && wordCount >= 1e4) {
    editorialStatus = "MAJOR_REVISION";
    recommendation = "Requiere reescritura sustancial. Revise los problemas detectados y vuelva a enviar.";
  } else {
    editorialStatus = "REJECTED";
    recommendation = "No alcanza estandares editoriales minimos. Se recomienda reescritura completa con atencion a los problemas criticos.";
  }
  return {
    statistics: {
      words: wordCount,
      sentences: sentenceCount,
      paragraphs: paragraphCount,
      avg_words_per_sentence: parseFloat(avgWordsPerSentence.toFixed(1)),
      avg_sentences_per_paragraph: parseFloat(avgSentencesPerParagraph.toFixed(1)),
      avg_word_length: parseFloat((words.reduce((s, w) => s + w.length, 0) / wordCount).toFixed(1)),
      avg_paragraph_length: parseFloat(avgParagraphLength.toFixed(1))
    },
    style_analysis: {
      vocabulary_diversity: parseFloat(vocabularyDiversity.toFixed(1)),
      type_token_ratio: parseFloat((ttr * 100).toFixed(1)),
      adjective_ratio: parseFloat(adjectiveRatio.toFixed(1)),
      adverb_ratio: parseFloat(adverbRatio.toFixed(1)),
      top_words: topWords.slice(0, 10),
      repetitive_words: repetitiveWords.length
    },
    readability: {
      flesch_score: parseFloat(fleschScore.toFixed(1)),
      reading_level: readingLevel,
      complex_words_ratio: parseFloat(complexWordRatio.toFixed(1)),
      avg_syllables_per_word: parseFloat(avgSyllablesPerWord.toFixed(1))
    },
    narrative_structure: {
      dialog_ratio: parseFloat(dialogRatio.toFixed(1)),
      sentence_length_variance: parseFloat(sentenceLengthVariance.toFixed(1)),
      long_paragraphs: longParagraphs,
      punctuation: {
        semicolons: semicolonCount,
        ellipsis: ellipsisCount,
        dashes: dashCount
      }
    },
    coherence: {
      connective_ratio: parseFloat(connectiveRatio.toFixed(1)),
      connectives_found: connectivesFound,
      verb_tense_distribution: {
        past_tense_ratio: parseFloat(verbRatio.pasado.toFixed(1)),
        present_tense_ratio: parseFloat(verbRatio.presente.toFixed(1))
      }
    },
    content_analysis: {
      proper_nouns_detected: uniqueProperNouns.length,
      estimated_characters: uniqueProperNouns.length > 5 ? Math.min(uniqueProperNouns.length, 50) : 0,
      sample_names: uniqueProperNouns.slice(0, 5)
    },
    quality_score: Math.round(qualityScore),
    plagiarism: plagiarismResult,
    editorial_status: editorialStatus,
    recommendation,
    issues,
    metadata: {
      analysis_date: (/* @__PURE__ */ new Date()).toISOString(),
      analyzer_version: "3.1.0",
      analysis_depth: "professional",
      scoring_model: "strict_editorial"
    }
  };
}
__name(analyzeManuscript, "analyzeManuscript");
function countSyllables(word) {
  word = word.toLowerCase();
  const vowels = "aeiou\xE1\xE0\xE4\xE9\xE8\xEB\xED\xEC\xEF\xF3\xF2\xF6\xFA\xF9\xFC";
  let count = 0;
  let prevWasVowel = false;
  for (let i = 0; i < word.length; i++) {
    const isVowel = vowels.includes(word[i]);
    if (isVowel && !prevWasVowel) {
      count++;
    }
    prevWasVowel = isVowel;
  }
  return Math.max(1, count);
}
__name(countSyllables, "countSyllables");
function calculateVariance(numbers) {
  if (numbers.length === 0) return 0;
  const mean = numbers.reduce((a, b) => a + b, 0) / numbers.length;
  const squareDiffs = numbers.map((n) => Math.pow(n - mean, 2));
  const avgSquareDiff = squareDiffs.reduce((a, b) => a + b, 0) / numbers.length;
  return Math.sqrt(avgSquareDiff);
}
__name(calculateVariance, "calculateVariance");
export {
  index_default as default
};
//# sourceMappingURL=index.js.map
