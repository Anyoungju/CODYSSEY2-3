const $ = (selector) => document.querySelector(selector);

function getBlueprintEndpoint() {
  const isGitHubPages = location.hostname.endsWith("github.io");
  const productionUrl = document.querySelector('meta[name="compass-api-url"]')?.content;
  return isGitHubPages && productionUrl ? productionUrl : "/api/blueprint";
}

const demoBlueprint = {
  service_name: "마음 한 칸",
  one_liner: "하루의 감정을 짧게 기록하고, 다음 생각을 여는 질문을 받는 감정 회고 서비스",
  pages: ["오늘의 감정 기록 — 기분과 한 줄 메모 입력", "AI 회고 — 맞춤 질문과 작은 행동 제안", "나의 흐름 — 최근 기록과 감정 변화 확인"],
  ai_feature: {title: "생각을 여는 회고 질문", input: "감정 점수와 오늘 있었던 일", output: "공감 문장, 회고 질문 2개, 작은 행동 1개", user_value: "감정을 판단하지 않고 스스로 정리할 실마리를 얻습니다.", failure_handling: "빈 입력은 즉시 안내하고, API 실패 시 기록은 보존한 채 다시 시도 버튼을 제공합니다."},
  milestones: ["정적 화면과 모바일 레이아웃 완성", "감정 입력·검증·결과 카드 연결", "Python AI API와 오류 UX 구현", "Vercel 배포 후 실제 사용자 3명에게 검증"],
  risks: ["AI 답변을 의료 조언으로 오해하지 않도록 안내", "민감한 감정 기록의 저장 범위 최소화", "API 호출 빈도와 비용 제한"]
};

function setTheme(theme) {
  document.body.classList.toggle("dark", theme === "dark");
  localStorage.setItem("compass-theme", theme);
}

function renderBlueprint(data) {
  $("#result-name").textContent = data.service_name;
  $("#result-summary").textContent = data.one_liner;
  $("#result-pages").replaceChildren(...data.pages.map((item) => Object.assign(document.createElement("li"), {textContent: item})));
  $("#ai-title").textContent = data.ai_feature.title;
  $("#ai-input").textContent = data.ai_feature.input;
  $("#ai-output").textContent = data.ai_feature.output;
  $("#ai-value").textContent = data.ai_feature.user_value;
  $("#ai-failure").textContent = data.ai_feature.failure_handling;
  $("#result-milestones").replaceChildren(...data.milestones.map((item) => Object.assign(document.createElement("li"), {textContent: item})));
  $("#result-risks").replaceChildren(...data.risks.map((item) => Object.assign(document.createElement("li"), {textContent: item})));
  $("#result").hidden = false;
  $("#result").scrollIntoView({behavior: "smooth", block: "start"});
}

async function requestBlueprint(payload) {
  if (new URLSearchParams(location.search).get("demo") === "1") {
    await new Promise((resolve) => setTimeout(resolve, 650));
    return demoBlueprint;
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(getBlueprintEndpoint(), {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload), signal: controller.signal});
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.error || "AI 설계 중 문제가 발생했습니다.");
    return body.blueprint;
  } catch (error) {
    if (error.name === "AbortError") throw new Error("응답 시간이 길어졌어요. 잠시 후 다시 시도해 주세요.");
    throw error;
  } finally { clearTimeout(timer); }
}

document.addEventListener("DOMContentLoaded", () => {
  setTheme(localStorage.getItem("compass-theme") || "light");
  $(".theme-toggle").addEventListener("click", () => setTheme(document.body.classList.contains("dark") ? "light" : "dark"));

  const observer = new IntersectionObserver((entries) => entries.forEach((entry) => entry.isIntersecting && entry.target.classList.add("visible")), {threshold: .12});
  document.querySelectorAll(".reveal").forEach((element) => observer.observe(element));

  const idea = $("#idea");
  idea.addEventListener("input", () => { $("#char-count").textContent = idea.value.length; $("#idea-error").textContent = ""; });

  $("#blueprint-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const status = $("#form-status");
    const button = event.currentTarget.querySelector("button[type=submit]");
    if (!idea.value.trim()) { $("#idea-error").textContent = "아이디어를 한 문장 이상 입력해 주세요."; idea.focus(); return; }
    button.disabled = true; button.classList.add("loading"); status.className = "form-status"; status.textContent = "아이디어의 방향을 읽고 있어요…";
    try {
      const blueprint = await requestBlueprint({idea: idea.value.trim(), audience: $("#audience").value.trim(), constraint: $("#constraint").value});
      renderBlueprint(blueprint); status.textContent = "청사진을 완성했습니다.";
    } catch (error) { status.className = "form-status error"; status.textContent = error.message; }
    finally { button.disabled = false; button.classList.remove("loading"); }
  });

  $("#copy-result").addEventListener("click", async () => {
    const text = `${$("#result-name").textContent}\n${$("#result-summary").textContent}\n\n${$("#result").innerText}`;
    await navigator.clipboard.writeText(text); $("#copy-result").textContent = "복사 완료"; setTimeout(() => $("#copy-result").textContent = "결과 복사", 1500);
  });

  if (new URLSearchParams(location.search).get("demo") === "1") {
    idea.value = "매일의 감정을 기록하면 AI가 마음을 정리할 질문을 제안하는 서비스";
    $("#audience").value = "바쁜 일상 속에서 감정을 돌아보고 싶은 사람";
    idea.dispatchEvent(new Event("input"));
  }
});
