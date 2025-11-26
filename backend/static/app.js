const uploadBtn = document.getElementById("uploadBtn");
const fileInput = document.getElementById("fileInput");
const uploadMsg = document.getElementById("uploadMsg");
const refreshDocs = document.getElementById("refreshDocs");
const docList = document.getElementById("docList");
const askBtn = document.getElementById("askBtn");
const promptEl = document.getElementById("prompt");
const answerEl = document.getElementById("answer");

uploadBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) { uploadMsg.innerText = "Bitte Datei auswählen."; return; }
  const fd = new FormData();
  fd.append("file", file);
  uploadMsg.innerText = "Lade hoch...";
  try {
    const res = await axios.post("/api/upload", fd, { headers: {'Content-Type': 'multipart/form-data'} });
    uploadMsg.innerText = `Hochgeladen: ${res.data.filename}`;
    loadDocs();
  } catch (e) {
    uploadMsg.innerText = "Fehler beim Upload.";
  }
});

refreshDocs.addEventListener("click", loadDocs);

async function loadDocs() {
  docList.innerHTML = "";
  try {
    const res = await axios.get("/api/documents");
    res.data.forEach(d => {
      const li = document.createElement("li");
      li.className = "list-group-item d-flex justify-content-between align-items-start";
      li.innerHTML = `<div><strong>${d.filename}</strong><div class="small text-muted">${d.content.substring(0,200)}${d.content.length>200?"...":""}</div></div>`;
      const del = document.createElement("button");
      del.className = "btn btn-sm btn-outline-danger";
      del.innerText = "Löschen";
      del.onclick = async () => {
        await axios.delete(`/api/documents/${d.id}`);
        loadDocs();
      };
      li.appendChild(del);
      docList.appendChild(li);
    });
  } catch (e) {
    docList.innerHTML = "<li class='list-group-item'>Fehler beim Laden der Dokumente.</li>";
  }
}

askBtn.addEventListener("click", async () => {
  const prompt = promptEl.value.trim();
  if (!prompt) { answerEl.innerText = "Bitte Prompt eingeben."; return; }
  answerEl.innerText = "Generiere...";
  try {
    const form = new FormData();
    form.append("prompt", prompt);
    const res = await axios.post("/api/chat", form);
    answerEl.innerHTML = `<pre style="white-space:pre-wrap">${res.data.answer}</pre>`;
  } catch (e) {
    answerEl.innerText = "Fehler bei der Anfrage.";
  }
});

// initial load
loadDocs();
