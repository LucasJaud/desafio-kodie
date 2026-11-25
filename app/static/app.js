const API_URL = "/api/v1/tasks";
const statuses = ["todo", "in_progress", "done"];
const priorityLabels = {
  critica: "Crítica",
  alta: "Alta",
  media: "Média",
  baixa: "Baixa",
};
const statusLabels = {
  todo: "A fazer",
  in_progress: "Em andamento",
  done: "Concluída",
};

const board = document.querySelector("#board");
const taskForm = document.querySelector("#task-form");
const requestInput = document.querySelector("#request-text");
const notice = document.querySelector("#notice");
const taskDialog = document.querySelector("#task-dialog");
const editForm = document.querySelector("#edit-form");
let tasks = [];
let draggedTaskId = null;
let noticeTimer;

function showNotice(message, isError = false) {
  clearTimeout(noticeTimer);
  notice.textContent = message;
  notice.classList.toggle("error", isError);
  notice.hidden = false;
  noticeTimer = setTimeout(() => {
    notice.hidden = true;
  }, 5000);
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });
  if (!response.ok) {
    let message = "Não foi possível concluir a operação.";
    try {
      const body = await response.json();
      message = body.detail?.message || message;
    } catch {
      // Mantém a mensagem genérica quando a resposta não contém JSON.
    }
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}

function makeElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function formatDate(value) {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
  }).format(new Date(value));
}

function makeTaskCard(task) {
  const card = makeElement("article", "task-card");
  card.draggable = true;
  card.dataset.taskId = String(task.id);

  const meta = makeElement("div", "card-meta");
  meta.append(makeElement("span", `priority priority-${task.priority}`, priorityLabels[task.priority]));
  if (task.needs_human_review) {
    meta.append(makeElement("span", "review-badge", "Revisar"));
  }

  const title = makeElement("button", "card-title", task.title);
  title.type = "button";
  title.dataset.action = "edit";
  title.dataset.taskId = String(task.id);

  const description = makeElement("p", "card-description", task.description);
  const footer = makeElement("div", "card-footer");
  footer.append(
    makeElement("span", "", task.category),
    makeElement("time", "", formatDate(task.created_at)),
  );
  const actions = makeElement("div", "card-actions");
  const edit = makeElement("button", "card-action", "Editar");
  edit.type = "button";
  edit.dataset.action = "edit";
  edit.dataset.taskId = String(task.id);
  const remove = makeElement("button", "card-action delete", "Excluir");
  remove.type = "button";
  remove.dataset.action = "delete";
  remove.dataset.taskId = String(task.id);
  actions.append(edit, remove);
  card.append(meta, title, description, footer, actions);
  return card;
}

function renderBoard() {
  const grouped = Object.fromEntries(statuses.map((status) => [status, []]));
  tasks.forEach((task) => grouped[task.status]?.push(task));
  statuses.forEach((status) => {
    const cards = board.querySelector(`[data-cards="${status}"]`);
    const empty = board.querySelector(`[data-empty="${status}"]`);
    cards.replaceChildren(...grouped[status].map(makeTaskCard));
    board.querySelector(`[data-count="${status}"]`).textContent = String(grouped[status].length);
    empty.hidden = grouped[status].length > 0;
  });
  document.querySelector("#task-total").textContent = String(tasks.length);
}

async function loadTasks() {
  try {
    tasks = await request(API_URL);
    renderBoard();
    return true;
  } catch (error) {
    showNotice(error.message, true);
    return false;
  }
}

function openEditor(task) {
  editForm.elements.title.value = task.title;
  editForm.elements.description.value = task.description;
  editForm.elements.status.value = task.status;
  editForm.dataset.taskId = String(task.id);
  document.querySelector("#original-request").textContent = task.request_text;
  document.querySelector("#suggested-step").textContent = task.suggested_next_step;
  document.querySelector("#priority-reason").textContent = task.reason;
  taskDialog.showModal();
}

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = taskForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  try {
    await request(`${API_URL}/organize`, {
      method: "POST",
      body: JSON.stringify({ request_text: requestInput.value }),
    });
    taskForm.reset();
    document.querySelector("#char-count").textContent = "0 / 4000";
    if (await loadTasks()) showNotice("Tarefa organizada e salva no quadro.");
  } catch (error) {
    showNotice(error.message, true);
  } finally {
    submitButton.disabled = false;
  }
});

requestInput.addEventListener("input", () => {
  document.querySelector("#char-count").textContent = `${requestInput.value.length} / 4000`;
});

editForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const taskId = editForm.dataset.taskId;
  try {
    await request(`${API_URL}/${taskId}`, {
      method: "PATCH",
      body: JSON.stringify({
        title: editForm.elements.title.value,
        description: editForm.elements.description.value,
        status: editForm.elements.status.value,
      }),
    });
    taskDialog.close();
    if (await loadTasks()) showNotice("Alterações salvas.");
  } catch (error) {
    showNotice(error.message, true);
  }
});

document.querySelectorAll("[data-close-dialog]").forEach((button) => {
  button.addEventListener("click", () => taskDialog.close());
});

board.addEventListener("click", async (event) => {
  const action = event.target.closest("[data-action]");
  if (!action) return;
  const task = tasks.find((item) => item.id === Number(action.dataset.taskId));
  if (!task) return;
  if (action.dataset.action === "edit") {
    openEditor(task);
    return;
  }
  if (action.dataset.action === "delete" && window.confirm(`Excluir "${task.title}"?`)) {
    try {
      await request(`${API_URL}/${task.id}`, { method: "DELETE" });
      if (await loadTasks()) showNotice("Tarefa excluída.");
    } catch (error) {
      showNotice(error.message, true);
    }
  }
});

board.addEventListener("dragstart", (event) => {
  const card = event.target.closest(".task-card");
  if (!card) return;
  draggedTaskId = Number(card.dataset.taskId);
  card.classList.add("dragging");
  event.dataTransfer.effectAllowed = "move";
  event.dataTransfer.setData("text/plain", String(draggedTaskId));
});

board.addEventListener("dragend", (event) => {
  event.target.closest(".task-card")?.classList.remove("dragging");
  board.querySelectorAll(".lane.is-over").forEach((lane) => lane.classList.remove("is-over"));
});

board.querySelectorAll(".lane").forEach((lane) => {
  lane.addEventListener("dragover", (event) => {
    event.preventDefault();
    lane.classList.add("is-over");
    event.dataTransfer.dropEffect = "move";
  });
  lane.addEventListener("dragleave", (event) => {
    if (!lane.contains(event.relatedTarget)) lane.classList.remove("is-over");
  });
  lane.addEventListener("drop", async (event) => {
    event.preventDefault();
    lane.classList.remove("is-over");
    const taskId = Number(event.dataTransfer.getData("text/plain")) || draggedTaskId;
    const task = tasks.find((item) => item.id === taskId);
    const newStatus = lane.dataset.status;
    if (!task || !statuses.includes(newStatus) || task.status === newStatus) return;
    try {
      await request(`${API_URL}/${task.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: newStatus }),
      });
      if (await loadTasks()) {
        showNotice(`Tarefa movida para "${statusLabels[newStatus]}".`);
      }
    } catch (error) {
      showNotice(error.message, true);
    }
  });
});

document.querySelector("#refresh-button").addEventListener("click", loadTasks);
loadTasks();
