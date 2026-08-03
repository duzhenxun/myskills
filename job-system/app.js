const state = {
  jobs: [],
  filtered: [],
};

const elements = {
  totalCount: document.getElementById("totalCount"),
  detailCount: document.getElementById("detailCount"),
  missingCount: document.getElementById("missingCount"),
  visibleCount: document.getElementById("visibleCount"),
  resultSummary: document.getElementById("resultSummary"),
  jobList: document.getElementById("jobList"),
  searchInput: document.getElementById("searchInput"),
  detailFilter: document.getElementById("detailFilter"),
  sortSelect: document.getElementById("sortSelect"),
  jobDialog: document.getElementById("jobDialog"),
  closeDialog: document.getElementById("closeDialog"),
  dialogCompany: document.getElementById("dialogCompany"),
  dialogTitle: document.getElementById("dialogTitle"),
  dialogMeta: document.getElementById("dialogMeta"),
  dialogStatus: document.getElementById("dialogStatus"),
  dialogDescription: document.getElementById("dialogDescription"),
  dialogWelfare: document.getElementById("dialogWelfare"),
  dialogDetails: document.getElementById("dialogDetails"),
  dialogLink: document.getElementById("dialogLink"),
};

let activeDialogJobId = null;

function parseSalaryValue(text) {
  if (!text) return 0;
  const match = text.match(/(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)/i);
  if (match) return (Number(match[1]) + Number(match[2])) / 2;
  const single = text.match(/(\d+(?:\.\d+)?)/);
  return single ? Number(single[1]) : 0;
}

function normalizeWelfare(welfare) {
  if (Array.isArray(welfare)) return welfare.filter(Boolean);
  if (typeof welfare === "string" && welfare.trim()) {
    return welfare.split(/[，,|]/).map((item) => item.trim()).filter(Boolean);
  }
  return [];
}

function buildSearchText(job) {
  return [
    job.name,
    job.company,
    job.area,
    job.salary,
    job.experience,
    job.degree,
    job.skills,
    job.description,
    job.industry,
    job.address,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function decorateJob(job) {
  return {
    ...job,
    _salaryValue: parseSalaryValue(job.salary),
    _searchText: buildSearchText(job),
  };
}

function setDialogStatus(message, tone) {
  if (!message) {
    elements.dialogStatus.hidden = true;
    elements.dialogStatus.textContent = "";
    elements.dialogStatus.className = "dialog-status";
    return;
  }

  elements.dialogStatus.hidden = false;
  elements.dialogStatus.textContent = message;
  elements.dialogStatus.className = `dialog-status ${tone}`;
}

function renderStats(jobs) {
  const detailOk = jobs.filter((job) => job.detail_status === "ok").length;
  const missing = jobs.length - detailOk;
  elements.totalCount.textContent = jobs.length;
  elements.detailCount.textContent = detailOk;
  elements.missingCount.textContent = missing;
}

function renderList(jobs) {
  elements.visibleCount.textContent = jobs.length;
  elements.resultSummary.textContent = `当前共展示 ${jobs.length} 条职位，已按你的筛选条件实时更新。`;

  if (!jobs.length) {
    elements.jobList.innerHTML = '<div class="empty-state">没有匹配到职位，换个关键词试试。</div>';
    return;
  }

  elements.jobList.innerHTML = jobs
    .map((job, index) => {
      const chips = [job.area, job.experience, job.degree].filter(Boolean);
      const snippet = job.description || job.skills || "该职位当前缺少详情描述，先保留了基础信息。";
      return `
        <article class="job-card" data-index="${index}">
          <div class="job-topline">
            <div>
              <h3 class="job-title">${escapeHtml(job.name || "未命名职位")}</h3>
              <div class="job-company">${escapeHtml(job.company || "未知公司")}</div>
            </div>
            <div class="salary">${escapeHtml(job.salary || "薪资未写")}</div>
          </div>
          <div class="meta-row">
            ${chips.map((chip) => `<span class="tag">${escapeHtml(chip)}</span>`).join("")}
            <span class="state-badge ${job.detail_status === "ok" ? "ok" : "missing"}">
              ${job.detail_status === "ok" ? "详情已抓取" : "详情待补"}
            </span>
          </div>
          <p class="job-snippet">${escapeHtml(snippet.slice(0, 180))}${snippet.length > 180 ? "..." : ""}</p>
        </article>
      `;
    })
    .join("");

  Array.from(elements.jobList.querySelectorAll(".job-card")).forEach((card) => {
    card.addEventListener("click", () => {
      const job = jobs[Number(card.dataset.index)];
      openDialog(job);
    });
  });
}

function updateJobInState(nextJob) {
  const index = state.jobs.findIndex((item) => item.security_id === nextJob.security_id);
  if (index === -1) return;
  state.jobs[index] = decorateJob(nextJob);
  renderStats(state.jobs);
  applyFilters();
}

function renderDialog(job) {
  activeDialogJobId = job.security_id || `${job.company}-${job.name}`;
  elements.dialogCompany.textContent = job.company || "未知公司";
  elements.dialogTitle.textContent = job.name || "未命名职位";

  const metaItems = [
    job.salary,
    job.area,
    job.experience,
    job.degree,
    job.detail_status === "ok" ? "详情已抓取" : "详情待补",
  ].filter(Boolean);
  elements.dialogMeta.innerHTML = metaItems.map((item) => `<span class="tag">${escapeHtml(item)}</span>`).join("");

  elements.dialogDescription.textContent = job.description || "这条职位当前没有抓到描述内容，系统正在尝试为你实时补抓。";

  const welfareList = normalizeWelfare(job.welfare);
  elements.dialogWelfare.innerHTML = welfareList.length
    ? welfareList.map((item) => `<span class="tag">${escapeHtml(item)}</span>`).join("")
    : '<span class="tag">暂无福利明细</span>';

  const detailRows = [
    ["招聘者", job.boss],
    ["招聘者姓名", job.boss_name],
    ["招聘者职位", job.boss_title],
    ["活跃时间", job.active_time],
    ["技能", job.skills],
    ["行业", job.industry],
    ["公司规模", job.scale],
    ["融资阶段", job.stage],
    ["地址", job.address],
    ["security_id", job.security_id],
  ].filter(([, value]) => value);

  elements.dialogDetails.innerHTML = detailRows
    .map(
      ([label, value]) => `
        <div>
          <dt>${escapeHtml(label)}</dt>
          <dd>${escapeHtml(value)}</dd>
        </div>
      `
    )
    .join("");

  elements.dialogLink.href = job.url || "#";
  elements.dialogLink.textContent = job.url || "暂无原始链接";
}

async function fetchDetailOnDemand(job) {
  if (job.detail_status === "ok" && (job.description || "").trim()) {
    setDialogStatus("", "");
    return;
  }

  setDialogStatus("正在补抓这条职位的详情，请稍等几秒…", "loading");
  try {
    const response = await fetch("/api/job-detail", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        security_id: job.security_id,
      }),
    });

    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.error || "补抓详情失败");
    }

    updateJobInState(payload.job);
    if (activeDialogJobId === payload.job.security_id) {
      renderDialog(payload.job);
      setDialogStatus("这条职位的详情已经补回来，并且写入本地数据了。", "success");
    }
  } catch (error) {
    if (activeDialogJobId === (job.security_id || `${job.company}-${job.name}`)) {
      setDialogStatus(`暂时没补到详情：${error.message}`, "error");
    }
  }
}

function openDialog(job) {
  renderDialog(job);
  setDialogStatus("", "");
  if (!elements.jobDialog.open) {
    elements.jobDialog.showModal();
  }
  void fetchDetailOnDemand(job);
}

function applyFilters() {
  const keyword = elements.searchInput.value.trim().toLowerCase();
  const detailFilter = elements.detailFilter.value;
  const sortMode = elements.sortSelect.value;

  let jobs = state.jobs.filter((job) => {
    if (detailFilter !== "all" && job.detail_status !== detailFilter) return false;
    if (!keyword) return true;
    return job._searchText.includes(keyword);
  });

  if (sortMode === "salary-desc") {
    jobs = [...jobs].sort((a, b) => b._salaryValue - a._salaryValue);
  } else if (sortMode === "salary-asc") {
    jobs = [...jobs].sort((a, b) => a._salaryValue - b._salaryValue);
  }

  state.filtered = jobs;
  renderList(jobs);
}

async function init() {
  const response = await fetch("./data/jobs.json");
  const jobs = await response.json();
  state.jobs = jobs.map(decorateJob);
  renderStats(state.jobs);
  applyFilters();
}

elements.searchInput.addEventListener("input", applyFilters);
elements.detailFilter.addEventListener("change", applyFilters);
elements.sortSelect.addEventListener("change", applyFilters);
elements.closeDialog.addEventListener("click", () => elements.jobDialog.close());
elements.jobDialog.addEventListener("click", (event) => {
  const rect = elements.jobDialog.getBoundingClientRect();
  const inDialog =
    rect.top <= event.clientY &&
    event.clientY <= rect.top + rect.height &&
    rect.left <= event.clientX &&
    event.clientX <= rect.left + rect.width;
  if (!inDialog) elements.jobDialog.close();
});
elements.jobDialog.addEventListener("close", () => {
  activeDialogJobId = null;
  setDialogStatus("", "");
});

init().catch((error) => {
  elements.resultSummary.textContent = "职位数据加载失败，请检查 JSON 文件。";
  elements.jobList.innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`;
});
