const getCsrfToken = () => {
    const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (input) {
        return input.value;
    }

    const cookieValue = document.cookie
        .split('; ')
        .find((row) => row.startsWith('csrftoken='));

    return cookieValue ? cookieValue.split('=')[1] : null;
};

const escapeHtml = (value) => {
    return value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
};

const openSavedAnswerModal = (title, content) => {
    const modalHost = document.getElementById('workspace-root');
    if (!modalHost) {
        return;
    }

    const modalElement = document.querySelector('[x-show*="isSavedModalOpen"]');
    const titleElement = document.querySelector('[x-text*="modalTitle"]');
    const contentElement = document.querySelector('[x-text*="modalContent"]');

    if (modalHost.__x && modalHost.__x.$data) {
        modalHost.__x.$data.isSavedModalOpen = true;
        modalHost.__x.$data.modalTitle = title;
        modalHost.__x.$data.modalContent = content;
        return;
    }

    if (modalHost._x_dataStack && modalHost._x_dataStack[0]) {
        const data = modalHost._x_dataStack[0];
        data.isSavedModalOpen = true;
        data.modalTitle = title;
        data.modalContent = content;
        return;
    }

    if (modalElement) {
        modalElement.style.display = 'flex';
    }
    if (titleElement) {
        titleElement.textContent = title;
    }
    if (contentElement) {
        contentElement.textContent = content;
    }
};

const buildSavedAnswerCard = (data, exportAnswerUrl) => {
    const newCard = document.createElement('div');
    newCard.className = 'flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-blue-400 cursor-pointer';
    newCard.dataset.savedAnswerId = data.id || '';
    newCard.dataset.modalTitle = data.summary;
    newCard.dataset.modalContent = data.full_content;

    const summary = data.summary || (data.full_content || '').substring(0, 100);

    newCard.innerHTML = `
        <span class="text-sm truncate w-4/5">${escapeHtml(summary)}</span>
        <div class="relative">
            <button type="button" class="text-gray-400 hover:text-gray-600 px-1 menu-toggle">
                ⋮
            </button>
            <div class="menu-dropdown hidden absolute right-0 mt-2 w-40 bg-white dark:bg-gray-800 rounded-md shadow-lg border border-gray-200 dark:border-gray-600 z-10">
                <a href="${escapeHtml(exportAnswerUrl(data.id || ''))}" class="block px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700">Xuất Text</a>
                <button type="button" data-action="delete-saved-answer" data-answer-id="${escapeHtml(String(data.id || ''))}" class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100 dark:hover:bg-gray-700 border-t border-gray-100 dark:border-gray-700">Xóa</button>
            </div>
        </div>
    `;

    const menuToggle = newCard.querySelector('.menu-toggle');
    const menuDropdown = newCard.querySelector('.menu-dropdown');

    menuToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        menuDropdown.classList.toggle('hidden');
    });

    newCard.addEventListener('click', (e) => {
        if (!e.target.closest('button') && !e.target.closest('a')) {
            openSavedAnswerModal(newCard.dataset.modalTitle, newCard.dataset.modalContent);
        }
    });

    return newCard;
};

const closeAllSavedAnswerMenus = () => {
    document.querySelectorAll('.menu-dropdown').forEach((menu) => {
        menu.classList.add('hidden');
    });
};

const safeFetchJson = async (url, options) => {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Server responded with an error.');
    }
    return data;
};

const initWorkspace = () => {
    const workspaceRoot = document.getElementById('workspace-root');
    if (!workspaceRoot) {
        return;
    }

    const baseUrl = (workspaceRoot.dataset.workspaceBaseUrl || '').replace(/\/$/, '');
    const chatEndpoint = `${baseUrl}/chat/`;
    const saveAnswerEndpoint = `${baseUrl}/save-answer/`;
    const exportAnswerUrl = (id) => `${baseUrl}/saved-answer/${id}/export/`;
    const deleteAnswerUrl = (id) => `${baseUrl}/saved-answer/${id}/delete/`;

    const csrfToken = getCsrfToken();
    if (!csrfToken) {
        console.warn('CSRF token not found for workspace script.');
    }

    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatHistory = document.getElementById('chat-history');
    const savedAnswersList = document.getElementById('saved-answers-list');

    if (!chatForm || !chatInput || !chatHistory) {
        return;
    }

    const appendChatMessage = (type, text) => {
        const wrapper = document.createElement('div');
        if (type === 'user') {
            wrapper.className = 'flex justify-end';
            wrapper.innerHTML = `
                <div class="bg-blue-600 text-white p-3 rounded-xl rounded-tr-none max-w-[80%] shadow-sm">
                    <p class="text-sm">${escapeHtml(text)}</p>
                </div>
            `;
        } else {
            wrapper.className = 'flex justify-start chat-answer-group';
            wrapper.dataset.answer = text;
            wrapper.innerHTML = `
                <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 p-4 rounded-xl rounded-tl-none max-w-[90%] shadow-sm group relative">
                    <p class="text-sm whitespace-pre-wrap chat-answer-text">${escapeHtml(text)}</p>
                    <div class="absolute -bottom-3 right-2 hidden group-hover:flex gap-2">
                        <button type="button" data-action="copy-answer" class="px-2 py-1 bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-xs shadow hover:bg-gray-200 dark:hover:bg-gray-600">Copy</button>
                        <button type="button" data-action="save-answer" class="px-2 py-1 bg-blue-100 text-blue-700 border border-blue-200 rounded text-xs shadow hover:bg-blue-200">Save</button>
                    </div>
                </div>
            `;
        }
        chatHistory.appendChild(wrapper);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    };

    chatForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const question = chatInput.value.trim();
        if (!question) {
            return;
        }

        const submitButton = chatForm.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
        }

        appendChatMessage('user', question);
        chatInput.value = '';

        try {
            const data = await safeFetchJson(chatEndpoint, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({ question }),
            });

            appendChatMessage('assistant', data.answer || 'No response');
        } catch (error) {
            console.error(error);
            alert(error.message || 'Không thể kết nối đến máy chủ. Vui lòng thử lại.');
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
            }
        }
    });

    document.addEventListener('click', async (event) => {
        const target = event.target;
        const action = target.dataset.action;
        if (!action) {
            return;
        }

        if (action === 'copy-answer') {
            const answerGroup = target.closest('.chat-answer-group');
            const answerText = answerGroup?.querySelector('.chat-answer-text')?.innerText || answerGroup?.dataset.answer;
            if (!answerText) {
                return;
            }

            try {
                await navigator.clipboard.writeText(answerText);
                const originalText = target.textContent;
                target.textContent = 'Copied!';
                setTimeout(() => {
                    target.textContent = originalText;
                }, 1200);
            } catch (err) {
                console.error(err);
                alert('Không thể sao chép văn bản.');
            }
            return;
        }

        if (action === 'save-answer') {
            const answerGroup = target.closest('.chat-answer-group');
            const answerText = answerGroup?.querySelector('.chat-answer-text')?.innerText || answerGroup?.dataset.answer;
            if (!answerText) {
                return;
            }

            try {
                const data = await safeFetchJson(saveAnswerEndpoint, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({ answer_text: answerText }),
                });

                if (!savedAnswersList) {
                    return;
                }

                const emptyMessage = savedAnswersList.querySelector('p');
                if (emptyMessage) {
                    emptyMessage.remove();
                }

                const card = buildSavedAnswerCard(data, exportAnswerUrl);
                savedAnswersList.insertBefore(card, savedAnswersList.firstChild);
                alert('Câu trả lời đã được lưu thành công.');
            } catch (err) {
                console.error(err);
                alert(err.message || 'Không thể lưu câu trả lời hiện tại.');
            }
            return;
        }

        if (action === 'delete-saved-answer') {
            const answerId = target.dataset.answerId;
            if (!answerId) {
                return;
            }

            if (!confirm('Bạn có chắc muốn xóa ghi chú đã lưu này không?')) {
                return;
            }

            const card = target.closest('[data-saved-answer-id]');
            try {
                await safeFetchJson(deleteAnswerUrl(answerId), {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                    },
                });
                card?.remove();
            } catch (err) {
                console.error(err);
                alert(err.message || 'Không thể xóa ghi chú hiện tại.');
            }
            return;
        }
    });

    document.addEventListener('click', () => {
        closeAllSavedAnswerMenus();
    });
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWorkspace);
} else {
    initWorkspace();
}
