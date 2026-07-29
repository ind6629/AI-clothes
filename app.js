const state = {
  inventory: [],
  selectedCategory: "all",
  stagedItems: [],
  outfits: [],
  modelPhoto: "",
  config: loadConfig()
};

const inventoryGrid = document.getElementById("inventoryGrid");
const categoryFilter = document.getElementById("categoryFilter");
const dropzone = document.getElementById("dropzone");
const promptPreview = document.getElementById("promptPreview");
const stylingPrompt = document.getElementById("stylingPrompt");
const previewStage = document.getElementById("previewStage");
const statusPill = document.getElementById("statusPill");
const generateBtn = document.getElementById("generateBtn");
const clearCanvasBtn = document.getElementById("clearCanvasBtn");
const copyPromptBtn = document.getElementById("copyPromptBtn");
const saveConfigBtn = document.getElementById("saveConfigBtn");
const saveOutfitBtn = document.getElementById("saveOutfitBtn");
const uploadItemBtn = document.getElementById("uploadItemBtn");
const apiKeyInput = document.getElementById("apiKey");
const modelNameInput = document.getElementById("modelName");
const inventoryItemTemplate = document.getElementById("inventoryItemTemplate");
const outfitList = document.getElementById("outfitList");
const itemNameInput = document.getElementById("itemNameInput");
const itemCategoryInput = document.getElementById("itemCategoryInput");
const itemDescInput = document.getElementById("itemDescInput");
const itemImageInput = document.getElementById("itemImageInput");
const modelPhotoInput = document.getElementById("modelPhotoInput");
const clearModelPhotoBtn = document.getElementById("clearModelPhotoBtn");
const modelPhotoPreview = document.getElementById("modelPhotoPreview");
const imageLightbox = document.getElementById("imageLightbox");
const lightboxImage = document.getElementById("lightboxImage");
const lightboxCloseBtn = document.getElementById("lightboxCloseBtn");

bootstrap();

async function bootstrap() {
  apiKeyInput.value = state.config.apiKey;
  modelNameInput.value = state.config.model;
  bindEvents();
  await Promise.all([loadInventory(), loadOutfits()]);
  renderModelPhotoPreview();
  renderStage();
  renderPrompt();
}

function bindEvents() {
  categoryFilter.addEventListener("change", () => {
    state.selectedCategory = categoryFilter.value;
    renderInventory();
  });

  stylingPrompt.addEventListener("input", renderPrompt);

  dropzone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropzone.classList.add("active");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("active");
  });

  dropzone.addEventListener("drop", (event) => {
    event.preventDefault();
    dropzone.classList.remove("active");

    const itemId = event.dataTransfer.getData("text/plain");
    const item = state.inventory.find((entry) => entry.id === itemId);
    if (!item) {
      return;
    }

    state.stagedItems.push({
      ...item,
      x: clamp(event.offsetX - 74, 10, dropzone.clientWidth - 160),
      y: clamp(event.offsetY - 74, 10, dropzone.clientHeight - 188)
    });

    renderStage();
    renderPrompt();
  });

  clearCanvasBtn.addEventListener("click", () => {
    state.stagedItems = [];
    stylingPrompt.value = "";
    renderStage();
    renderPrompt();
    resetPreview();
  });

  copyPromptBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(buildPrompt());
      setStatus("提示词已复制", "success");
    } catch (error) {
      setStatus("复制失败", "error");
    }
  });

  saveConfigBtn.addEventListener("click", () => {
    state.config = {
      apiKey: apiKeyInput.value.trim(),
      model: modelNameInput.value.trim() || "gpt-image-1"
    };
    localStorage.setItem("outfit-demo-config", JSON.stringify(state.config));
    setStatus("配置已保存", "success");
  });

  saveOutfitBtn.addEventListener("click", saveOutfit);
  uploadItemBtn.addEventListener("click", uploadRealItem);
  modelPhotoInput.addEventListener("change", handleModelPhotoChange);
  clearModelPhotoBtn.addEventListener("click", clearModelPhoto);
  generateBtn.addEventListener("click", handleGenerate);

  if (lightboxCloseBtn) {
    lightboxCloseBtn.addEventListener("click", closeLightbox);
  }

  if (imageLightbox) {
    imageLightbox.addEventListener("click", (event) => {
      if (event.target === imageLightbox) {
        closeLightbox();
      }
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeLightbox();
    }
  });
}

async function loadInventory() {
  try {
    const response = await fetch("/api/items");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const payload = await response.json();
    state.inventory = payload.items || [];
    renderInventory();
  } catch (error) {
    setStatus("衣柜加载失败", "error");
  }
}

async function loadOutfits() {
  try {
    const response = await fetch("/api/outfits");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const payload = await response.json();
    state.outfits = payload.outfits || [];
    renderOutfits();
  } catch (error) {
    state.outfits = [];
    renderOutfits();
  }
}

async function uploadRealItem() {
  const name = itemNameInput.value.trim();
  const category = itemCategoryInput.value;
  const desc = itemDescInput.value.trim() || "上传的服装照片";
  const file = itemImageInput.files?.[0];

  if (!name || !file) {
    setStatus("请先填写名称并选择照片", "error");
    return;
  }

  try {
    const imageUrl = await readFileAsDataUrl(file);
    const payload = { name, category, desc, imageUrl };

    const response = await fetch("/api/items", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || `HTTP ${response.status}`);
    }

    state.inventory = result.items || [];
    renderInventory();
    itemNameInput.value = "";
    itemDescInput.value = "";
    itemImageInput.value = "";
    setStatus("服装照片已加入衣柜", "success");
  } catch (error) {
    setStatus("服装照片上传失败", "error");
  }
}

function renderInventory() {
  inventoryGrid.innerHTML = "";

  const visibleItems = state.inventory.filter((item) => {
    return state.selectedCategory === "all" || item.category === state.selectedCategory;
  });

  visibleItems.forEach((item) => {
    const fragment = inventoryItemTemplate.content.cloneNode(true);
    const card = fragment.querySelector(".item-card");
    const thumb = fragment.querySelector(".item-thumb");
    const title = fragment.querySelector("h3");
    const category = fragment.querySelector(".item-category");
    const desc = fragment.querySelector(".item-desc");

    card.dataset.itemId = item.id;
    thumb.innerHTML = item.imageUrl
      ? `<img src="${item.imageUrl}" alt="${escapeHtml(item.name)}">`
      : `<span>${escapeHtml(item.badge || "衣")}</span>`;

    title.textContent = item.name;
    category.textContent = item.categoryLabel;
    desc.textContent = item.desc;

    card.addEventListener("dragstart", (event) => {
      event.dataTransfer.setData("text/plain", item.id);
      event.dataTransfer.effectAllowed = "copy";
      card.classList.add("dragging");
    });

    card.addEventListener("dragend", () => {
      card.classList.remove("dragging");
    });

    inventoryGrid.appendChild(fragment);
  });
}

function renderStage() {
  const existingItems = Array.from(dropzone.querySelectorAll(".dropzone-item"));
  existingItems.forEach((element) => element.remove());

  const overlay = dropzone.querySelector(".dropzone-overlay");
  overlay.style.display = state.stagedItems.length ? "none" : "grid";

  state.stagedItems.forEach((item, index) => {
    const element = document.createElement("div");
    element.className = "dropzone-item";
    element.style.left = `${item.x}px`;
    element.style.top = `${item.y}px`;
    element.innerHTML = `
      <button class="remove-chip" type="button" aria-label="remove">x</button>
      <div class="item-badge">${item.imageUrl ? `<img src="${item.imageUrl}" alt="${escapeHtml(item.name)}">` : escapeHtml(item.badge || "衣")}</div>
      <strong>${escapeHtml(item.name)}</strong>
      <span>${escapeHtml(item.categoryLabel)}</span>
    `;

    element.querySelector(".remove-chip").addEventListener("click", () => {
      state.stagedItems.splice(index, 1);
      renderStage();
      renderPrompt();
    });

    enableStageDragging(element, index);
    dropzone.appendChild(element);
  });
}

function enableStageDragging(element, index) {
  let dragging = false;
  let offsetX = 0;
  let offsetY = 0;

  element.addEventListener("pointerdown", (event) => {
    if (event.target.closest(".remove-chip")) {
      return;
    }

    dragging = true;
    offsetX = event.clientX - element.offsetLeft;
    offsetY = event.clientY - element.offsetTop;
    element.setPointerCapture(event.pointerId);
  });

  element.addEventListener("pointermove", (event) => {
    if (!dragging) {
      return;
    }

    const rect = dropzone.getBoundingClientRect();
    const nextX = clamp(event.clientX - rect.left - offsetX, 10, dropzone.clientWidth - element.offsetWidth - 10);
    const nextY = clamp(event.clientY - rect.top - offsetY, 10, dropzone.clientHeight - element.offsetHeight - 10);
    element.style.left = `${nextX}px`;
    element.style.top = `${nextY}px`;
    state.stagedItems[index].x = nextX;
    state.stagedItems[index].y = nextY;
  });

  const stopDrag = () => {
    dragging = false;
  };

  element.addEventListener("pointerup", stopDrag);
  element.addEventListener("pointercancel", stopDrag);
}

function renderPrompt() {
  promptPreview.textContent = buildPrompt();
}

function renderModelPhotoPreview() {
  if (!state.modelPhoto) {
    modelPhotoPreview.className = "model-preview empty";
    modelPhotoPreview.innerHTML = "<span>上传模特照片后，生成时会一起作为人物参考发送。</span>";
    return;
  }

  modelPhotoPreview.className = "model-preview";
  modelPhotoPreview.innerHTML = `<img src="${state.modelPhoto}" alt="上传的模特参考图">`;
}

function renderOutfits() {
  outfitList.innerHTML = "";

  if (!state.outfits.length) {
    outfitList.innerHTML = "<p class=\"saved-empty\">还没有保存的搭配。</p>";
    return;
  }

  state.outfits.forEach((outfit) => {
    const card = document.createElement("article");
    card.className = "saved-outfit";
    card.innerHTML = `
      <h4>${escapeHtml(outfit.name)}</h4>
      <p>${escapeHtml(outfit.summary)}</p>
      <button type="button">加载</button>
    `;

    card.querySelector("button").addEventListener("click", () => {
      state.stagedItems = (outfit.items || []).map((item) => ({ ...item }));
      stylingPrompt.value = outfit.stylingPrompt || "";
      renderStage();
      renderPrompt();
      setStatus(`已加载 ${outfit.name}`, "success");
    });

    outfitList.appendChild(card);
  });
}

function buildPrompt() {
  if (!state.stagedItems.length) {
    return "将单品添加到画布后，AI 提示词会自动组装在这里。";
  }

  const itemsLine = state.stagedItems
    .map((item) => `${item.name}（${item.categoryLabel}，${item.desc}）`)
    .join("，");

  const extraStyle = stylingPrompt.value.trim() || "极简奢华、干净背景、电商风格、高级质感";

  return [
    "生成一张时尚穿搭预览图。",
    `包含单品：${itemsLine}。`,
    `风格方向：${extraStyle}。`,
    state.modelPhoto
      ? "使用上传的模特图作为人物参考，尽量保留相同的面部、姿态和构图。"
      : "创建一位单人时尚模特用于展示穿搭。",
    "使用提供的服装参考图作为款式、轮廓、颜色和材质依据。",
    "必须展示模特全身，从头顶到鞋底完整入镜，双脚不能被裁切，人物四周留出适度边距。",
    "优先使用竖版电商模特构图，人物完整站立，避免半身、近景或局部裁切。",
    "服装纹理真实清晰，层次明确，适合品牌展示和电商预览。"
  ].join("\n");
}

async function handleModelPhotoChange() {
  const file = modelPhotoInput.files?.[0];
  if (!file) {
    return;
  }

  try {
    state.modelPhoto = await readFileAsDataUrl(file);
    renderModelPhotoPreview();
    renderPrompt();
    setStatus("模特照片已就绪", "success");
  } catch (error) {
    setStatus("模特照片上传失败", "error");
  }
}

function clearModelPhoto() {
  state.modelPhoto = "";
  modelPhotoInput.value = "";
  renderModelPhotoPreview();
  renderPrompt();
  setStatus("模特照片已清除", "idle");
}

async function saveOutfit() {
  if (!state.stagedItems.length) {
    setStatus("保存前请先添加单品", "error");
    return;
  }

  const payload = {
    name: `搭配 ${new Date().toLocaleString()}`,
    stylingPrompt: stylingPrompt.value.trim(),
    summary: state.stagedItems.map((item) => item.name).join(" / "),
    items: state.stagedItems
  };

  try {
    const response = await fetch("/api/outfits", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const result = await response.json();
    state.outfits = result.outfits || [];
    renderOutfits();
    setStatus("搭配已保存", "success");
  } catch (error) {
    setStatus("保存失败", "error");
  }
}

async function handleGenerate() {
  if (!state.stagedItems.length) {
    setStatus("请先添加单品", "error");
    return;
  }

  setStatus("正在生成图像...", "loading");
  previewStage.innerHTML = `
    <div class="preview-placeholder">
      <p>正在生成...</p>
      <span>通常需要几秒到十几秒。</span>
    </div>
  `;

  const payload = {
    prompt: buildPrompt(),
    apiKey: state.config.apiKey,
    model: state.config.model,
    modelImage: state.modelPhoto,
    referenceImages: state.stagedItems
      .filter((item) => item.imageUrl)
      .map((item) => ({
        name: item.name,
        category: item.category,
        imageUrl: item.imageUrl
      }))
  };

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || `HTTP ${response.status}`);
    }

    if (result.image_url) {
      renderGeneratedImage(result.image_url);
      setStatus("图像已就绪", "success");
      return;
    }

    if (result.demo_message) {
      showPromptOnlyFallback(buildPrompt(), result.demo_message);
      setStatus("演示模式", "idle");
      return;
    }

    throw new Error("接口未返回图片");
  } catch (error) {
    showPromptOnlyFallback(buildPrompt(), error.message);
    setStatus("生成失败", "error");
  }
}

function renderGeneratedImage(imageUrl) {
  const safeUrl = escapeHtml(imageUrl);
  previewStage.innerHTML = `
    <button class="preview-image-button" type="button" aria-label="打开大图预览">
      <img src="${safeUrl}" alt="生成的搭配预览">
      <span class="preview-image-hint">点击放大查看</span>
    </button>
  `;

  const trigger = previewStage.querySelector(".preview-image-button");
  if (trigger) {
    trigger.addEventListener("click", () => {
      openLightbox(imageUrl);
    });
  }
}

function showPromptOnlyFallback(prompt, message = "") {
  previewStage.innerHTML = `
    <div class="preview-placeholder">
      <p>提示词已准备好</p>
      <span>${escapeHtml(message || "添加 API Key 后，可从 Python 后端调用图像接口。")}</span>
    </div>
  `;
  promptPreview.textContent = prompt;
}

function resetPreview() {
  previewStage.innerHTML = `
    <div class="preview-placeholder">
      <p>生成结果会显示在这里</p>
      <span>结果图支持完整预览，也支持点击放大查看。</span>
    </div>
  `;
  setStatus("等待中", "idle");
}

function openLightbox(imageUrl) {
  if (!imageLightbox || !lightboxImage || !imageUrl) {
    return;
  }

  lightboxImage.src = imageUrl;
  imageLightbox.hidden = false;
  document.body.classList.add("lightbox-open");
}

function closeLightbox() {
  if (!imageLightbox || !lightboxImage) {
    return;
  }

  imageLightbox.hidden = true;
  lightboxImage.removeAttribute("src");
  document.body.classList.remove("lightbox-open");
}

function setStatus(text, tone) {
  statusPill.textContent = text;
  statusPill.className = `status-pill ${tone}`;
}

function loadConfig() {
  const raw = localStorage.getItem("outfit-demo-config");
  if (!raw) {
    return { apiKey: "", model: "gpt-image-1" };
  }

  try {
    const parsed = JSON.parse(raw);
    return {
      apiKey: parsed.apiKey || "",
      model: parsed.model || "gpt-image-1"
    };
  } catch (error) {
    return { apiKey: "", model: "gpt-image-1" };
  }
}

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("Failed to read file"));
    reader.readAsDataURL(file);
  });
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
