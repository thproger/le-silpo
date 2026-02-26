const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileNameDisplay = document.getElementById('fileNameDisplay');
const cancelGroup = document.getElementById('cancelGroup');
const uploadBtn = document.getElementById('uploadBtn');
const statusHeader = document.getElementById('statusHeader');
const previewContainer = document.getElementById('previewContainer');
const fileNameHeader = document.getElementById('fileNameHeader');
const statusDots = document.getElementById('statusDots');

dropZone.addEventListener('click', () => fileInput.click());

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, e => {
        e.preventDefault();
        e.stopPropagation();
    });
});

dropZone.addEventListener('dragover', () => dropZone.classList.add('dragover'));
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

dropZone.addEventListener('drop', (e) => {
    dropZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length) handleFiles(files[0]);
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleFiles(e.target.files[0]);
});

function handleFiles(file) {
    if (!file.name.endsWith('.csv')) {
        alert("Тільки CSV файли!");
        return;
    }

    Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        preview: 20,
        complete: function(results) {
            renderTable(results);

            dropZone.classList.add('d-none');
            previewContainer.classList.remove('d-none');
            fileNameHeader.classList.remove('d-none');
            fileNameHeader.innerText = file.name;

            fileNameDisplay.value = file.name;
            statusHeader.innerText = "Import CSV";
            statusDots.innerText = "...";
            cancelGroup.classList.remove('d-none');
            uploadBtn.classList.add('btn-upload-active');
        }
    });
}

function renderTable(results) {
    const table = document.getElementById('previewTable');
    let thead = `<thead class="table-dark"><tr><th class="text-center">#</th>`;
    results.meta.fields.forEach((field, index) => {
        thead += `<th class="text-center">${String.fromCharCode(65 + index)}</th>`;
    });
    thead += `</tr></thead>`;

    let tbody = `<tbody><tr class="table-secondary fw-bold"><td>1</td>`;
    results.meta.fields.forEach(field => { tbody += `<td>${field}</td>`; });
    tbody += `</tr>`;

    results.data.forEach((row, i) => {
        tbody += `<tr><td class="bg-dark text-white text-center">${i + 2}</td>`;
        results.meta.fields.forEach(field => {
            tbody += `<td>${row[field] || ''}</td>`;
        });
        tbody += `</tr>`;
    });
    tbody += `</tbody>`;
    table.innerHTML = thead + tbody;
}

document.getElementById('cancelBtn').addEventListener('click', () => {
    fileInput.value = "";
    fileNameDisplay.value = "";
    previewContainer.classList.add('d-none');
    fileNameHeader.classList.add('d-none');
    dropZone.classList.remove('d-none');
    cancelGroup.classList.add('d-none');
    statusHeader.innerText = "Orders list";
    uploadBtn.classList.remove('btn-upload-active');
});

uploadBtn.addEventListener('click', async () => {
    if (!fileInput.files.length) return;
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('http://127.0.0.1:8000/orders', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        alert("Успішно завантажено!");
        console.log(result);
    } catch (err) {
        alert("Помилка з'єднання з сервером.");
    }
});