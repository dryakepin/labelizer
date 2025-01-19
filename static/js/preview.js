// Function to generate preview
async function generatePreview(formData) {
    try {
        const response = await fetch('/upload/' + labelUuid, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            return null;
        }
        
        // Force image reload by adding timestamp
        const previewImage = document.getElementById('previewImage');
        previewImage.src = data.preview_url + '?t=' + new Date().getTime();
        document.getElementById('preview').style.display = 'block';
        
        currentFileName = data.original_file;
        return data.preview_url;
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while generating the preview');
        return null;
    }
}

// Store the original file name
let currentFileName = null;

// Define form controls that update on both change and input
const continuousUpdateControls = [
    'beer_name',
    'subtitle',
    'abv',
    'beer_size',
    'border_color',
    'text_color',
    'font',
    'font_size',
    'image_x',
    'image_y'
];

// Define controls that only update on change (release)
const changeOnlyControls = [
    'crop_x',
    'crop_y'
];

// Handle form submission
document.getElementById('labelForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    await generatePreview(formData);
});

// Add live preview updates for continuous update controls
continuousUpdateControls.forEach(controlId => {
    const element = document.getElementById(controlId);
    if (element) {
        ['change', 'input'].forEach(eventType => {
            element.addEventListener(eventType, async () => {
                const form = document.getElementById('labelForm');
                const formData = new FormData(form);
                await generatePreview(formData);
            });
        });
    }
});

// Add preview updates for change-only controls
changeOnlyControls.forEach(controlId => {
    const element = document.getElementById(controlId);
    if (element) {
        element.addEventListener('change', async () => {
            const form = document.getElementById('labelForm');
            const formData = new FormData(form);
            await generatePreview(formData);
        });
    }
});

// File upload preview
document.getElementById('background').addEventListener('change', function(e) {
    const placeholder = e.target.parentElement.querySelector('.file-input-placeholder');
    if (this.files && this.files[0]) {
        placeholder.innerHTML = `<span>${this.files[0].name}</span>`;
        // Trigger preview generation when file is uploaded
        const form = document.getElementById('labelForm');
        const formData = new FormData(form);
        generatePreview(formData);
    } else {
        placeholder.innerHTML = `
            <span>Drop image here or click to upload</span>
            <small>PNG, JPG up to 16MB</small>
        `;
    }
});

// Update PDF generation to use UUID and proper filename
document.getElementById('generatePDF').onclick = async () => {
    if (!currentFileName) {
        alert('Please upload an image first');
        return;
    }
    
    const beerName = document.getElementById('beer_name').value;
    if (!beerName) {
        alert('Please enter a beer name');
        return;
    }

    console.log("currentFileName: ", currentFileName)
    console.log("beerName: ", beerName)
    
    // Get the form data
    const formData = new FormData();
    formData.append('label_data', JSON.stringify(getFormData()));
    
    // Add the current background file
    const backgroundInput = document.getElementById('background');
    if (backgroundInput.files.length > 0) {
        formData.append('background', backgroundInput.files[0]);
    }
    
    try {
        const pdfResponse = await fetch('/generate-pdf/' + labelUuid, {
            method: 'POST',
            body: formData  // Send as FormData instead of JSON
        });
        
        if (!pdfResponse.ok) {
            throw new Error('Failed to generate PDF');
        }
        
        const blob = await pdfResponse.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        // Sanitize filename by removing special characters
        const sanitizedBeerName = beerName.replace(/[^a-z0-9]/gi, '_').toLowerCase();

        console.log("sanitizedBeerName: ", sanitizedBeerName)
        
        a.download = `${sanitizedBeerName}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error generating PDF:', error);
        alert('Error generating PDF: ' + error.message);
    }
};

// Save function using UUID
async function saveLabel() {
    if (!currentFileName) {
        alert('Please upload an image first');
        return;
    }

    // Get the form data
    const formData = new FormData();
    formData.append('label_data', JSON.stringify(getFormData()));
    
    // Add the current background file
    const backgroundInput = document.getElementById('background');
    if (backgroundInput.files.length > 0) {
        formData.append('background', backgroundInput.files[0]);
    }
    
    try {
        const response = await fetch('/save-label/' + labelUuid, {
            method: 'POST',
            body: formData  // Send as FormData instead of JSON
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Label saved successfully!');
        } else {
            alert('Error saving label: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to save label');
    }
}

// Initialize form with data when page loads
document.addEventListener('DOMContentLoaded', async () => {
    if (initialData && Object.keys(initialData).length > 0) {
        // Set form values from initial data
        Object.keys(initialData).forEach(key => {
            const element = document.getElementById(key);
            if (element && key !== 'background' && key !== 'filename') {
                element.value = initialData[key] || '';
            }
        });

        // If we have a background image and filename, set up the file input
        if (initialData.background && initialData.filename) {
            try {
                // Fetch the image file
                const response = await fetch(initialData.background);
                const blob = await response.blob();
                
                // Create a File object
                const file = new File([blob], initialData.filename, { type: 'image/png' });
                
                // Create a FileList-like object
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                
                // Set the file input's files
                const fileInput = document.getElementById('background');
                fileInput.files = dataTransfer.files;
                
                // Update the placeholder text
                const placeholder = document.querySelector('.file-input-placeholder');
                if (placeholder) {
                    placeholder.innerHTML = `<span>${initialData.filename}</span>`;
                }
                
                // Set current filename
                currentFileName = initialData.filename;
                
                // Show the preview
                const previewSection = document.getElementById('preview');
                const previewImage = document.getElementById('previewImage');
                if (previewSection && previewImage) {
                    previewImage.src = initialData.background;
                    previewSection.style.display = 'block';
                }
            } catch (error) {
                console.error('Error setting up file input:', error);
            }
        }

        // Update all range value displays
        document.querySelectorAll('input[type="range"]').forEach(range => {
            const valueDisplay = document.getElementById(range.id + '_value');
            if (valueDisplay) {
                valueDisplay.textContent = `${range.value}%`;
            }
        });

        // Update color preview displays
        ['border_color', 'text_color'].forEach(id => {
            const preview = document.getElementById(id + '_preview');
            const input = document.getElementById(id);
            if (preview && input) {
                preview.textContent = input.value.toUpperCase();
            }
        });
    }
});

// Sync range and number inputs
function syncRangeAndNumber(rangeId, numberId) {
    const range = document.getElementById(rangeId);
    const number = document.getElementById(numberId);
    
    // When range changes, update number and trigger preview
    range.addEventListener('input', async () => {
        number.value = range.value;
        if (currentFileName) {
            const form = document.getElementById('labelForm');
            const formData = new FormData(form);
            await generatePreview(formData);
        }
    });
    
    // When number changes, update range and trigger preview
    number.addEventListener('input', async () => {
        range.value = number.value;
        if (currentFileName) {
            const form = document.getElementById('labelForm');
            const formData = new FormData(form);
            await generatePreview(formData);
        }
    });
}

// Add color preview functionality
function updateColorPreview(inputId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(inputId + '_preview');
    
    input.addEventListener('input', () => {
        preview.textContent = input.value.toUpperCase();
    });
}

updateColorPreview('border_color');
updateColorPreview('text_color');

// Add range value display updates
function updateRangeValue(inputId) {
    const input = document.getElementById(inputId);
    const valueDisplay = document.getElementById(inputId + '_value');
    
    input.addEventListener('input', () => {
        valueDisplay.textContent = `${input.value}%`;
    });
}

updateRangeValue('crop_x');

// Update or add getFormData function
function getFormData() {
    return {
        background: document.getElementById('background').value,
        beer_name: document.getElementById('beer_name').value,
        subtitle: document.getElementById('subtitle').value,
        abv: document.getElementById('abv').value,
        beer_size: document.getElementById('beer_size').value,
        border_color: document.getElementById('border_color').value,
        text_color: document.getElementById('text_color').value,
        font: document.getElementById('font').value,
        font_size: parseInt(document.getElementById('font_size').value),
        image_x: parseFloat(document.getElementById('image_x').value),
        image_y: parseFloat(document.getElementById('image_y').value),
        crop_x: parseFloat(document.getElementById('crop_x').value)
    };
}

