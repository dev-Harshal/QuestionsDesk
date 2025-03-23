createQuestionSetForm = document.getElementById('createQuestionSetForm')
if (createQuestionSetForm) {
    createQuestionSetForm.addEventListener('submit', function(event) {
        event.preventDefault();

        fetch('/teacher/create/question-set/', {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(createQuestionSetForm)

        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.success_url
            }
            else {
                popAlert(data)
            }
        })

    })
}

updateQuestionSetForm = document.getElementById('updateQuestionSetForm')
if (updateQuestionSetForm) {
    updateQuestionSetForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const id = document.getElementById('id').value
        
        fetch(`/teacher/update/question-set/${id}/`, {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(updateQuestionSetForm)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.success_url
            }
            else {
                popAlert(data)
            }
        })

    })
}

const questionContainer = document.getElementById('questionContainer');
const addQuestionRow = document.getElementById('addQuestionRow');


if (addQuestionRow) {
    addQuestionRow.addEventListener('click', function(event) {

        const questionCount = questionContainer.getElementsByClassName('questionRow').length + 1;
        const newRow = document.createElement('div');
        newRow.classList.add('row', 'align-items-end', 'mb-3', 'questionRow');

        newRow.innerHTML = `
            <div class="col-9">
                <label for="questionTitle" class="form-label">(${questionCount}) Question Title</label>
                <input type="text" class="form-control" name="question_title[]" required>
            </div>

            <div class="col-2">
                <label for="mark" class="form-label">Mark</label>
                <input type="text" class="form-control" name="mark[]" required>
            </div>

            <div class="col-1">

                <button type="button" class="btn btn-transparent btn-sm text-end" data-bs-toggle="modal" data-bs-target="#verticalycentered(${questionCount})">
                    <i class="bi bi-trash3" style="cursor: pointer; color: red;"></i>
                </button>

            <div class="modal fade" id="verticalycentered(${questionCount})" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                            <div class="modal-header bg-primary text-light fw-bold">
                                <h5 class="modal-title">Confrim Delete</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>

                            <div class="modal-body text-center">
                                Confirm you want to delete <br> 
                                Question (${questionCount}) ?
                            </div>

                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                <button type="submit" value="(${questionCount})" class="btn btn-danger removeRow">Delete</button>
                            </div>
                    </div>
                </div>
            </div>
        </div>

        `;
        
        // Append new row to the container
        questionContainer.appendChild(newRow);
        
        // Attach remove functionality to the newly added row
        attachRemoveEvent(newRow);
    });
}

// Attach remove functionality to each remove icon
function attachRemoveEvent(row) {
    const removeIcon = row.querySelector('.removeRow');
    removeIcon.addEventListener('click', function() {
        const modal = bootstrap.Modal.getInstance(document.getElementById(`verticalycentered${removeIcon.value}`));
        modal.hide();
        row.remove();
        updateQuestionNumbers(); // Update question numbers after removing a row

    });
}

// Update the question numbers after adding/removing a row
function updateQuestionNumbers() {
    const rows = questionContainer.getElementsByClassName('questionRow');
    for (let i = 0; i < rows.length; i++) {
        const label = rows[i].querySelector('label');
        label.textContent = `(${i + 1}) Question Title`; // Update the question number
    }
}

// Initial setup: Attach remove event to any existing rows
if (questionContainer) {
    const existingRows = questionContainer.getElementsByClassName('questionRow');
    for (let row of existingRows) {
        attachRemoveEvent(row);
    }
}

createQuestionForm = document.getElementById('createQuestionForm')
if (createQuestionForm) {
    createQuestionForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const id = document.getElementById('id').value

        fetch(`/teacher/create/questions/${id}/`, {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(createQuestionForm)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.success_url
            }
            else {
                popAlert(data)
            }
        })

    })
}

updateQuestionForm = document.getElementById('updateQuestionForm')
if (updateQuestionForm) {
    updateQuestionForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const currentUnit = document.getElementById('currentUnit').value
        const subjectId = document.getElementById('subjectId').value;
        
        const url = `/teacher/update/questions/${subjectId}/${currentUnit}/`
        fetch(url, {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(updateQuestionForm)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.success_url
            }
            else {
                popAlert(data)
            }
        })

    })
}

const unitDropdown =  document.getElementById("unit-dropdown")
if (unitDropdown) {
    unitDropdown.addEventListener("change", function() {
        const selectedNumber = this.value;
        const subjectId = document.getElementById('subjectId').value;
        if (selectedNumber) {
            var url = `http://127.0.0.1:8000/teacher/update/questions/${subjectId}/${selectedNumber}/`;
            window.location.href = url;  // Redirect to the URL
        }
    });
}
