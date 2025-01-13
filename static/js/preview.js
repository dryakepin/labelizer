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
    'brewer_name',
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

// Add the sync handlers for range/number pairs
syncRangeAndNumber('image_rotation_range', 'image_rotation');

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
        brewer_name: formData.get('brewer_name'),
        abv: formData.get('abv'),
        beer_size: formData.get('beer_size'),
        border_color: formData.get('border_color'),
        text_color: formData.get('text_color'),
        font: formData.get('font'),
        font_size: parseInt(formData.get('font_size'), 10),
        image_rotation: parseInt(formData.get('image_rotation'), 10),
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

// Rest of the code remains unchanged... 