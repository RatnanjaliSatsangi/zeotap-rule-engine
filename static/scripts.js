document.addEventListener('DOMContentLoaded', function () {
    loadAttributes();
    loadRules();

    // Handle Create Rule Form Submission
    document.getElementById('create-rule-form').addEventListener('submit', function (e) {
        e.preventDefault();
        const ruleName = document.getElementById('rule-name').value;
        const ruleText = document.getElementById('rule-text').value;

        fetch('/api/create_rule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rule_name: ruleName, rule_text: ruleText }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showFlashMessage(data.error, 'error');
            } else {
                showFlashMessage(data.message, 'success');
                resetCreateForm();
                loadRules(); // Refresh the dropdown and existing rules list with the new rule
            }
        })
        .catch(error => {
            showFlashMessage('An unexpected error occurred', 'error');
        });
    });

    // Handle Add Attribute Form Submission
    document.getElementById('add-attribute-form').addEventListener('submit', function (e) {
        e.preventDefault();
        const attributeName = document.getElementById('attribute-name').value;

        fetch('/api/add_attribute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ attribute_name: attributeName }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showFlashMessage(data.error, 'error');
            } else {
                showFlashMessage(data.message, 'success');
                loadAttributes();  // Reload attributes after successful addition
                resetAttributeForm();
            }
        })
        .catch(error => {
            showFlashMessage('An unexpected error occurred', 'error');
        });
    });

    // Handle Combine Rules Form Submission
    document.getElementById('combine-rule-form').addEventListener('submit', function (e) {
        e.preventDefault();
        const ruleIds = document.getElementById('rule-ids').value.split(',').map(id => parseInt(id.trim()));

        fetch('/api/combine_rules', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rule_ids: ruleIds }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showFlashMessage(data.error, 'error');
            } else {
                showFlashMessage(data.message, 'success');
            }
        })
        .catch(error => {
            showFlashMessage('An unexpected error occurred', 'error');
        });
    });

    // Handle Select Rule Form Submission (for evaluation)
    document.getElementById('select-rule-form').addEventListener('submit', function (e) {
        e.preventDefault();
        const ruleId = document.getElementById('select-rule-id').value;

        fetch(`/api/get_rule_metadata/${ruleId}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showFlashMessage(data.error, 'error');
                    return;
                }

                const dynamicInputs = document.getElementById('dynamic-inputs');
                dynamicInputs.innerHTML = '';  // Clear existing inputs

                // Create input fields based on rule metadata (fields only)
                data.fields.forEach(field => {
                    const div = document.createElement('div');
                    div.classList.add('input-group');

                    const label = document.createElement('label');
                    label.textContent = `Enter value for ${field}:`;
                    label.htmlFor = `input-${field}`;

                    const input = document.createElement('input');
                    input.type = 'text';
                    input.name = field;
                    input.id = `input-${field}`;
                    input.placeholder = `Enter value for ${field}`;

                    div.appendChild(label);
                    div.appendChild(input);
                    dynamicInputs.appendChild(div);
                });

                // Show the evaluation form now that fields are ready
                document.getElementById('evaluate-rule-form').style.display = 'block';
            })
            .catch(error => {
                showFlashMessage('An unexpected error occurred', 'error');
            });
    });

    // Handle Evaluate Rule Form Submission
    document.getElementById('evaluate-rule-form').addEventListener('submit', function (e) {
        e.preventDefault();
        const ruleId = document.getElementById('select-rule-id').value;
        const data = {};

        // Collect all input values dynamically
        document.querySelectorAll('#dynamic-inputs input').forEach(input => {
            data[input.name] = input.value;
        });

        fetch('/api/evaluate_rule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rule_id: ruleId, data: data }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showFlashMessage(data.error, 'error');
            } else {
                showFlashMessage(`Evaluation Result: ${data.result}`, data.result ? 'success' : 'error');
            }
        })
        .catch(error => {
            showFlashMessage('An unexpected error occurred', 'error');
        });
    });

    // Function to load and display attributes with Delete buttons
    function loadAttributes() {
        fetch('/api/get_attributes')
            .then(response => response.json())
            .then(data => {
                const attributeList = document.getElementById('attribute-list');
                attributeList.innerHTML = '';  // Clear the list
                data.attributes.forEach(attr => {
                    const li = document.createElement('li');
                    li.innerHTML = `${attr} `;
                    
                    // Create delete button for each attribute
                    const deleteButton = document.createElement('button');
                    deleteButton.textContent = 'Delete';
                    deleteButton.classList.add('delete-attr-btn');
                    deleteButton.setAttribute('data-attribute-name', attr);
                    
                    li.appendChild(deleteButton);
                    attributeList.appendChild(li);
                });
            });
    }

    // Handle Delete Attribute Button Click
    document.getElementById('attribute-list').addEventListener('click', function (e) {
        if (e.target.classList.contains('delete-attr-btn')) {
            const attributeName = e.target.getAttribute('data-attribute-name');
            
            fetch('/api/delete_attribute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ attribute_name: attributeName }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showFlashMessage(data.error, 'error');
                } else {
                    showFlashMessage(data.message, 'success');
                    loadAttributes();  // Reload attributes after deletion
                }
            })
            .catch(error => {
                showFlashMessage('An unexpected error occurred', 'error');
            });
        }
    });

    // Load existing rules and populate the dropdown and the "Existing Rules" list
    function loadRules() {
        fetch('/api/get_rules')
            .then(response => response.json())
            .then(data => {
                const select = document.getElementById('select-rule-id');
                select.innerHTML = '';  // Clear existing options
                const ruleList = document.getElementById('rule-list');
                ruleList.innerHTML = '';  // Clear the rule list

                // Add default option for select
                const defaultOption = document.createElement('option');
                defaultOption.value = "";
                defaultOption.text = "Select a rule";
                defaultOption.disabled = true;
                defaultOption.selected = true;
                select.appendChild(defaultOption);

                // Populate the select dropdown and the rule list
                data.rules.forEach(rule => {
                    const option = document.createElement('option');
                    option.value = rule.id;
                    option.text = `ID: ${rule.id}, Name: ${rule.name}`;
                    select.appendChild(option);

                    const li = document.createElement('li');
                    li.innerHTML = `ID: ${rule.id}, Name: ${rule.name}, Rule: ${rule.text}<br>`;
                    
                    const editButton = document.createElement('button');
                    editButton.classList.add('edit-btn');
                    editButton.textContent = 'Edit';
                    editButton.setAttribute('data-rule-id', rule.id);
                    editButton.setAttribute('data-rule-text', rule.text);

                    const deleteButton = document.createElement('button');
                    deleteButton.classList.add('delete-btn');
                    deleteButton.textContent = 'Delete';
                    deleteButton.setAttribute('data-rule-id', rule.id);

                    li.appendChild(editButton);
                    li.appendChild(deleteButton);
                    ruleList.appendChild(li);
                });
            });
    }

    // Handle Edit Rule Button Click
    document.getElementById('rule-list').addEventListener('click', function (e) {
        if (e.target.classList.contains('edit-btn')) {
            const ruleId = e.target.getAttribute('data-rule-id');
            const ruleText = e.target.getAttribute('data-rule-text');

            // Populate the edit form with the existing rule text
            document.getElementById('edit-rule-id').value = ruleId;
            document.getElementById('edit-rule-text').value = ruleText;

            // Show the edit section and scroll to it
            document.getElementById('edit-rule-section').style.display = 'block';
            window.scrollTo({ top: document.getElementById('edit-rule-section').offsetTop, behavior: 'smooth' });
        }
    });

    // Handle Delete Rule Button Click
    document.getElementById('rule-list').addEventListener('click', function (e) {
        if (e.target.classList.contains('delete-btn')) {
            const ruleId = e.target.getAttribute('data-rule-id');
            
            fetch('/api/delete_rule', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rule_id: ruleId }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showFlashMessage(data.error, 'error');
                } else {
                    showFlashMessage(data.message, 'success');
                    loadRules();  // Reload rules after deletion
                }
            })
            .catch(error => {
                showFlashMessage('An unexpected error occurred', 'error');
            });
        }
    });

    // Handle Edit Rule Form Submission
    document.getElementById('edit-rule-form').addEventListener('submit', function (e) {
        e.preventDefault();
        const ruleId = document.getElementById('edit-rule-id').value;
        const ruleText = document.getElementById('edit-rule-text').value;

        fetch('/api/edit_rule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rule_id: ruleId, rule_text: ruleText }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showFlashMessage(data.error, 'error');
            } else {
                showFlashMessage(data.message, 'success');
                loadRules();  // Reload rules after editing
            }
        })
        .catch(error => {
            showFlashMessage('An unexpected error occurred', 'error');
        });
    });

    function resetCreateForm() {
        document.getElementById('create-rule-form').reset();
    }

    function resetAttributeForm() {
        document.getElementById('add-attribute-form').reset();
    }

    // Show flash message and scroll to top
    function showFlashMessage(message, type) {
        const flashMessageDiv = document.getElementById('flash-message');
        flashMessageDiv.textContent = message;
        flashMessageDiv.className = type === 'error' ? 'flash-error' : 'flash-success';
        window.scrollTo({ top: 0, behavior: 'smooth' });

        setTimeout(() => {
            flashMessageDiv.textContent = '';
            flashMessageDiv.className = '';  // Clear after 3 seconds
        }, 3000);
    }
});
