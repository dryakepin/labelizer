// Function to generate preview
async function generatePreview(formData) {
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            return null;
        }
        
        document.getElementById('previewImage').src = data.preview_url;
        document.getElementById('preview').style.display = 'block';
        return data.original_file;
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while generating the preview');
        return null;
    }
}

// Store the original file name
let currentFileName = null;

// Define form controls
const formControls = [
    'beer_name',
    'subtitle',
    'abv',
    'beer_size',
    'border_color',
    'text_color',
    'font',
    'font_size',
    'image_x',
    'image_y',
    'crop_x'
];

// Handle form submission
document.getElementById('labelForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    currentFileName = await generatePreview(formData);
});

// Add live preview updates for all form controls
formControls.forEach(controlId => {
    const element = document.getElementById(controlId);
    ['change', 'input'].forEach(eventType => {
        element.addEventListener(eventType, async () => {
            if (currentFileName) {
                const form = document.getElementById('labelForm');
                const formData = new FormData(form);
                await generatePreview(formData);
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', () => {
    if (initialData) {
        // Text Inputs
        document.getElementById('beer_name').value = initialData.beer_name || '';
        document.getElementById('subtitle').value = initialData.subtitle || '';
        document.getElementById('abv').value = initialData.abv || '';
        document.getElementById('font_size').value = initialData.font_size || 32;

        // Dropdown Select
        document.getElementById('beer_size').value = initialData.beer_size || '500ML';

        // Color Inputs
        document.getElementById('border_color').value = initialData.border_color || '#000000';
        document.getElementById('text_color').value = initialData.text_color || '#000000';

        // Font Dropdown
        document.getElementById('font').value = initialData.font || 'Arial';

        // Range Input
        document.getElementById('crop_x').value = initialData.crop_x || 50;
        document.getElementById('crop_x_value').innerText = `${initialData.crop_x || 50}%`;

        // Number Inputs
        document.getElementById('image_x').value = initialData.image_x || 50;
        document.getElementById('image_y').value = initialData.image_y || 50;
    }

    // Update range slider display value
    const cropXInput = document.getElementById('crop_x');
    const cropXValue = document.getElementById('crop_x_value');
    if (cropXInput && cropXValue) {
        cropXInput.addEventListener('input', (event) => {
            cropXValue.innerText = `${event.target.value}%`;
        });
    }

    // Handle background image if it exists
    if (initialData.background) {
        const previewSection = document.getElementById('preview');
        const previewImage = document.getElementById('previewImage');
        if (previewSection && previewImage) {
            previewImage.src = initialData.background;
            previewSection.style.display = 'block';
        }
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

// File upload preview
document.getElementById('background').addEventListener('change', function(e) {
    const placeholder = e.target.parentElement.querySelector('.file-input-placeholder');
    if (this.files && this.files[0]) {
        placeholder.innerHTML = `<span>${this.files[0].name}</span>`;
        // Trigger preview generation when file is uploaded
        document.getElementById('labelForm').dispatchEvent(new Event('submit'));
    } else {
        placeholder.innerHTML = `
            <span>Drop image here or click to upload</span>
            <small>PNG, JPG up to 16MB</small>
        `;
    }
});

// Update PDF generation to use stored filename
document.getElementById('generatePDF').onclick = async () => {
    if (!currentFileName) return;
    
    const form = document.getElementById('labelForm');
    const formData = new FormData(form);
    const labelData = {
        beer_name: formData.get('beer_name'),
        subtitle: formData.get('subtitle'),
        abv: formData.get('abv'),
        beer_size: formData.get('beer_size'),
        border_color: formData.get('border_color'),
        text_color: formData.get('text_color'),
        font: formData.get('font'),
        font_size: parseInt(formData.get('font_size'), 10),
        image_x: parseInt(formData.get('image_x'), 10),
        image_y: parseInt(formData.get('image_y'), 10),
        crop_x: parseInt(formData.get('crop_x'), 10),
    };
    
    const pdfResponse = await fetch('/generate-pdf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            filename: currentFileName,
            label_data: labelData
        })
    });
    
    if (pdfResponse.ok) {
        const blob = await pdfResponse.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'beer_label.pdf';
        a.click();
        window.URL.revokeObjectURL(url);
    }
};

async function saveLabel() {
    if (!currentFileName) {
        alert('Please upload an image first');
        return;
    }

    const formData = getFormData();
    
    try {
        const response = await fetch('/save-label', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                uuid: labelUuid,
                label_data: formData,
                filename: currentFileName
            }),
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

// Update or add getFormData function
function getFormData() {
    return {
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

