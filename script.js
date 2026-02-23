const questionBank = [
  // 5. sınıf
  { grade: 5, course: "Türkçe", term: 1, examNo: 1, outcome: { code: "T.5.3.1", text: "Okuduğu metnin ana fikrini belirler." }, question: "Okuduğunuz metinden yola çıkarak ana fikri 2-3 cümle ile yazınız." },
  { grade: 5, course: "Türkçe", term: 1, examNo: 2, outcome: { code: "T.5.4.2", text: "Yazılarında uygun geçiş ve bağlantı ifadelerini kullanır." }, question: "\"Ancak, bununla birlikte, sonuç olarak\" ifadelerini kullanarak kısa bir paragraf yazınız." },
  { grade: 5, course: "Matematik", term: 1, examNo: 1, outcome: { code: "M.5.1.2", text: "Doğal sayılarla dört işlem yapar." }, question: "2 438 + 1 275 - 963 işlemini yaparak sonucu adım adım gösteriniz." },
  { grade: 5, course: "Matematik", term: 2, examNo: 2, outcome: { code: "M.5.2.4", text: "Kesirlerle toplama ve çıkarma işlemlerini yapar." }, question: "3/4 + 1/8 - 1/2 işlemini ortak payda kullanarak çözünüz." },
  { grade: 5, course: "Fen Bilimleri", term: 2, examNo: 1, outcome: { code: "F.5.6.1", text: "Işığın yayılma özelliklerini açıklar." }, question: "Işığın doğrusal yolla yayıldığını günlük hayattan iki örnekle açıklayınız." },
  { grade: 5, course: "Sosyal Bilgiler", term: 1, examNo: 2, outcome: { code: "SB.5.2.3", text: "Yaşadığı çevredeki doğal unsurları tanır." }, question: "Yaşadığınız çevrede bulunan üç doğal unsuru yazıp bunların yaşamımıza etkisini açıklayınız." },

  // 6. sınıf
  { grade: 6, course: "Türkçe", term: 2, examNo: 1, outcome: { code: "T.6.3.5", text: "Metindeki yardımcı fikirleri belirler." }, question: "Verilen metindeki yardımcı fikirleri maddeler hâlinde yazınız." },
  { grade: 6, course: "Matematik", term: 1, examNo: 2, outcome: { code: "M.6.1.4", text: "Oran kavramını açıklar ve oran yazar." }, question: "12 kız ve 18 erkek öğrencinin bulunduğu sınıf için kız/erkek ve erkek/toplam oranlarını bulunuz." },
  { grade: 6, course: "Matematik", term: 2, examNo: 1, outcome: { code: "M.6.3.2", text: "Alan ölçme birimlerini kullanır." }, question: "Kenar uzunlukları 8 cm ve 5 cm olan dikdörtgenin alanını hesaplayıp işlem basamaklarını yazınız." },
  { grade: 6, course: "Fen Bilimleri", term: 1, examNo: 1, outcome: { code: "F.6.2.3", text: "Destek ve hareket sistemine ait yapıları açıklar." }, question: "Kas ve kemiklerin birlikte çalışmasını örnek vererek açıklayınız." },
  { grade: 6, course: "Sosyal Bilgiler", term: 2, examNo: 2, outcome: { code: "SB.6.5.1", text: "Ülkemizin kaynakları ile ekonomik faaliyetlerini ilişkilendirir." }, question: "Tarım, sanayi ve hizmet sektörlerinden birer örnek vererek bulundukları bölgeyle ilişkisini açıklayınız." },

  // 7. sınıf
  { grade: 7, course: "Türkçe", term: 1, examNo: 1, outcome: { code: "T.7.3.8", text: "Metinde kullanılan düşünceyi geliştirme yollarını belirler." }, question: "Tanımlama ve örneklendirme yöntemlerini kullanarak çevre bilinci konusunda bir paragraf yazınız." },
  { grade: 7, course: "Matematik", term: 1, examNo: 2, outcome: { code: "M.7.1.3", text: "Rasyonel sayılarla işlemler yapar." }, question: "(-3/5) + (7/10) - (1/2) işlemini çözünüz." },
  { grade: 7, course: "Matematik", term: 2, examNo: 1, outcome: { code: "M.7.3.1", text: "Doğrusal denklemleri çözer." }, question: "3x - 7 = 2x + 5 denklemini çözüp kontrol ediniz." },
  { grade: 7, course: "Fen Bilimleri", term: 2, examNo: 2, outcome: { code: "F.7.6.4", text: "Enerji dönüşümlerini açıklar." }, question: "Bir hidroelektrik santralinde gerçekleşen enerji dönüşümlerini sırasıyla yazınız." },
  { grade: 7, course: "Sosyal Bilgiler", term: 1, examNo: 1, outcome: { code: "SB.7.3.2", text: "Osmanlı Devleti'nin fetih siyasetini açıklar." }, question: "Osmanlı Devleti'nin fetih siyasetinde iskân uygulamasının amaçlarını açıklayınız." },

  // 8. sınıf
  { grade: 8, course: "Türkçe", term: 1, examNo: 2, outcome: { code: "T.8.3.12", text: "Metindeki anlatım biçimlerini ayırt eder." }, question: "Açıklayıcı ve tartışmacı anlatım farkını örneklerle açıklayınız." },
  { grade: 8, course: "Matematik", term: 1, examNo: 1, outcome: { code: "M.8.1.1", text: "Çarpanlar ve katlar ile ilgili problemler çözer." }, question: "84 sayısının asal çarpanlarını bulup EBOB-EKOK ilişkisini kısaca açıklayınız." },
  { grade: 8, course: "Matematik", term: 2, examNo: 2, outcome: { code: "M.8.4.3", text: "Eğim kavramını açıklar ve uygular." }, question: "(2,3) ve (6,11) noktalarından geçen doğrunun eğimini hesaplayınız." },
  { grade: 8, course: "Fen Bilimleri", term: 1, examNo: 1, outcome: { code: "F.8.3.2", text: "Basıncı etkileyen değişkenleri açıklar." }, question: "Katı basıncını etkileyen değişkenleri deney örneğiyle açıklayınız." },
  { grade: 8, course: "T.C. İnkılap Tarihi", term: 2, examNo: 1, outcome: { code: "INK.8.4.1", text: "Millî Mücadele'nin hazırlık dönemini analiz eder." }, question: "Amasya Genelgesi'nin Millî Mücadele açısından önemini üç maddeyle yazınız." },
  { grade: 8, course: "İngilizce", term: 2, examNo: 2, outcome: { code: "ENG.8.7.1", text: "Expresses obligations using should/must." }, question: "School rules hakkında en az 5 cümlelik bir metin yazınız ve should/must yapılarını kullanınız." }
];

const gradeSelect = document.getElementById("grade");
const courseSelect = document.getElementById("course");
const termSelect = document.getElementById("term");
const examNoSelect = document.getElementById("examNo");
const questionCountInput = document.getElementById("questionCount");
const kazanımlarContainer = document.getElementById("kazanımlar");
const createExamBtn = document.getElementById("createExam");
const toggleAllBtn = document.getElementById("toggleAll");

const examPaper = document.getElementById("examPaper");
const emptyState = document.getElementById("emptyState");
const actions = document.getElementById("actions");
const printBtn = document.getElementById("printBtn");
const downloadBtn = document.getElementById("downloadBtn");

function unique(list) {
  return [...new Set(list)];
}

function shuffle(arr) {
  return [...arr].sort(() => Math.random() - 0.5);
}

function initFilters() {
  const grades = unique(questionBank.map((q) => q.grade)).sort((a, b) => a - b);
  grades.forEach((grade) => {
    const option = document.createElement("option");
    option.value = String(grade);
    option.textContent = `${grade}. Sınıf`;
    gradeSelect.appendChild(option);
  });

  refreshCourses();
}

function refreshCourses() {
  const grade = Number(gradeSelect.value);
  const courses = unique(questionBank.filter((q) => q.grade === grade).map((q) => q.course)).sort();

  courseSelect.innerHTML = "";
  courses.forEach((course) => {
    const option = document.createElement("option");
    option.value = course;
    option.textContent = course;
    courseSelect.appendChild(option);
  });

  refreshKazanımlar();
}

function getScopedQuestions() {
  const grade = Number(gradeSelect.value);
  const course = courseSelect.value;
  const term = Number(termSelect.value);
  const examNo = Number(examNoSelect.value);

  const exact = questionBank.filter(
    (q) => q.grade === grade && q.course === course && q.term === term && q.examNo === examNo
  );

  if (exact.length > 0) return exact;

  return questionBank.filter((q) => q.grade === grade && q.course === course);
}

function refreshKazanımlar() {
  const scoped = getScopedQuestions();
  const outcomes = unique(scoped.map((q) => `${q.outcome.code}|${q.outcome.text}`));

  kazanımlarContainer.innerHTML = "";

  if (outcomes.length === 0) {
    kazanımlarContainer.innerHTML = "<p>Bu filtre için soru bulunamadı.</p>";
    return;
  }

  outcomes.forEach((raw, idx) => {
    const [code, text] = raw.split("|");
    const row = document.createElement("label");
    row.className = "kazanım-item";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = code;
    checkbox.checked = idx < Math.min(4, outcomes.length);

    const labelText = document.createElement("span");
    labelText.innerHTML = `<span class="kazanım-code">${code}</span> — ${text}`;

    row.appendChild(checkbox);
    row.appendChild(labelText);
    kazanımlarContainer.appendChild(row);
  });
}

function getSelectedOutcomes() {
  return [...kazanımlarContainer.querySelectorAll("input[type='checkbox']:checked")].map(
    (el) => el.value
  );
}

function generateExam() {
  const grade = Number(gradeSelect.value);
  const course = courseSelect.value;
  const term = Number(termSelect.value);
  const examNo = Number(examNoSelect.value);
  const selectedOutcomes = getSelectedOutcomes();
  const questionCount = Number(questionCountInput.value);

  if (selectedOutcomes.length === 0) {
    alert("Lütfen en az bir kazanım seçiniz.");
    return;
  }

  const filtered = getScopedQuestions().filter((q) => selectedOutcomes.includes(q.outcome.code));

  if (filtered.length === 0) {
    alert("Seçilen kazanımlarda soru bulunamadı. Farklı kazanım/filtre deneyiniz.");
    return;
  }

  const selectedQuestions = shuffle(filtered).slice(0, Math.max(1, Math.min(questionCount, 20)));

  const today = new Date().toLocaleDateString("tr-TR");
  examPaper.innerHTML = `
    <h2 class="exam-title">${grade}. Sınıf ${course} ${term}. Dönem ${examNo}. Yazılı</h2>
    <div class="meta-grid">
      <div><strong>Tarih:</strong> ${today}</div>
      <div><strong>Süre:</strong> 40 Dakika</div>
      <div><strong>Ad Soyad:</strong> ____________________</div>
      <div><strong>Sınıf/No:</strong> ____________________</div>
    </div>
    <p><strong>Kapsanan Kazanımlar:</strong> ${selectedOutcomes.join(", ")}</p>
    <ol class="questions">
      ${selectedQuestions.map((q) => `<li>${q.question}</li>`).join("")}
    </ol>
    <p><strong>Notlandırma:</strong> Her soru eşit puandır.</p>
  `;

  emptyState.classList.add("hidden");
  examPaper.classList.remove("hidden");
  actions.classList.remove("hidden");
}

function downloadExamAsText() {
  if (examPaper.classList.contains("hidden")) return;

  const plainText = examPaper.innerText;
  const blob = new Blob([plainText], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "yazili.txt";
  a.click();

  URL.revokeObjectURL(url);
}

function toggleAllOutcomes() {
  const checkboxes = [...kazanımlarContainer.querySelectorAll("input[type='checkbox']")];
  if (checkboxes.length === 0) return;

  const allChecked = checkboxes.every((cb) => cb.checked);
  checkboxes.forEach((cb) => {
    cb.checked = !allChecked;
  });
}

gradeSelect.addEventListener("change", refreshCourses);
courseSelect.addEventListener("change", refreshKazanımlar);
termSelect.addEventListener("change", refreshKazanımlar);
examNoSelect.addEventListener("change", refreshKazanımlar);
createExamBtn.addEventListener("click", generateExam);
printBtn.addEventListener("click", () => window.print());
downloadBtn.addEventListener("click", downloadExamAsText);
toggleAllBtn.addEventListener("click", toggleAllOutcomes);

initFilters();
