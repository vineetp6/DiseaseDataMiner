/**
 * Main JavaScript file for the Drug Discovery Platform
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Set up tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (typeof bootstrap !== 'undefined') {
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
    
    // Handle compound search advanced filters toggle
    const advancedSearchToggle = document.querySelector('[data-bs-toggle="collapse"][data-bs-target="#advancedSearch"]');
    if (advancedSearchToggle) {
        advancedSearchToggle.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (icon) {
                if (icon.getAttribute('data-feather') === 'chevron-down') {
                    icon.setAttribute('data-feather', 'chevron-up');
                } else {
                    icon.setAttribute('data-feather', 'chevron-down');
                }
                feather.replace();
            }
        });
    }
    
    // Format any date elements
    const dateElements = document.querySelectorAll('.format-date');
    dateElements.forEach(function(element) {
        const date = new Date(element.textContent);
        if (!isNaN(date.getTime())) {
            element.textContent = date.toLocaleDateString();
        }
    });
    
    // Set active navigation link based on current URL
    setActiveNavLink();
    
    // Add event listener to property sliders to update their displayed values
    const propertySliders = document.querySelectorAll('.property-slider');
    propertySliders.forEach(function(slider) {
        const valueDisplay = document.getElementById(slider.dataset.valueDisplay);
        if (valueDisplay) {
            slider.addEventListener('input', function() {
                valueDisplay.textContent = slider.value;
            });
        }
    });
});

/**
 * Sets the active navigation link based on the current URL.
 */
function setActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(function(link) {
        const href = link.getAttribute('href');
        if (href === currentPath || 
            (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        } else if (currentPath === '/' && href === '/') {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

/**
 * Copies text to clipboard
 * @param {string} text - The text to copy to clipboard
 */
function copyToClipboard(text) {
    // Create a temporary input element
    const input = document.createElement('textarea');
    input.value = text;
    document.body.appendChild(input);
    
    // Select and copy the text
    input.select();
    document.execCommand('copy');
    
    // Remove the temporary element
    document.body.removeChild(input);
    
    // Show a small notification
    const notification = document.createElement('div');
    notification.textContent = 'Copied to clipboard';
    notification.className = 'copy-notification';
    document.body.appendChild(notification);
    
    // Remove notification after a short delay
    setTimeout(function() {
        notification.classList.add('fade-out');
        setTimeout(function() {
            document.body.removeChild(notification);
        }, 500);
    }, 1500);
}

/**
 * Toggles between two different views
 * @param {string} showId - ID of the element to show
 * @param {string} hideId - ID of the element to hide
 * @param {string} activeButtonId - ID of the button to mark as active
 * @param {string} inactiveButtonId - ID of the button to mark as inactive
 */
function toggleView(showId, hideId, activeButtonId, inactiveButtonId) {
    const showElement = document.getElementById(showId);
    const hideElement = document.getElementById(hideId);
    const activeButton = document.getElementById(activeButtonId);
    const inactiveButton = document.getElementById(inactiveButtonId);
    
    if (showElement && hideElement) {
        showElement.style.display = 'block';
        hideElement.style.display = 'none';
    }
    
    if (activeButton && inactiveButton) {
        activeButton.classList.add('active');
        inactiveButton.classList.remove('active');
    }
}

/**
 * Filter table rows based on input value
 * @param {string} inputId - ID of the input element
 * @param {string} tableId - ID of the table to filter
 */
function filterTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const filter = input.value.toUpperCase();
    const table = document.getElementById(tableId);
    const tr = table.getElementsByTagName('tr');
    
    for (let i = 1; i < tr.length; i++) { // Start from 1 to skip the header row
        let visible = false;
        const td = tr[i].getElementsByTagName('td');
        
        for (let j = 0; j < td.length; j++) {
            const cell = td[j];
            if (cell) {
                const text = cell.textContent || cell.innerText;
                if (text.toUpperCase().indexOf(filter) > -1) {
                    visible = true;
                    break;
                }
            }
        }
        
        tr[i].style.display = visible ? '' : 'none';
    }
}

/**
 * Updates the URL parameters without reloading the page
 * @param {string} key - Parameter key
 * @param {string} value - Parameter value
 */
function updateUrlParam(key, value) {
    const url = new URL(window.location.href);
    url.searchParams.set(key, value);
    window.history.replaceState({}, '', url);
}

/**
 * Validates a SMILES string format
 * @param {string} smiles - SMILES string to validate
 * @return {boolean} - Whether the SMILES string appears valid
 */
function validateSmiles(smiles) {
    // Basic validation - check for invalid characters
    const invalidChars = /[^A-Za-z0-9@\-\+\[\]\(\)\\\/%=#$\.~]/;
    if (invalidChars.test(smiles)) {
        return false;
    }
    
    // Check for balanced parentheses and brackets
    let parensCount = 0;
    let bracketsCount = 0;
    
    for (let i = 0; i < smiles.length; i++) {
        if (smiles[i] === '(') parensCount++;
        if (smiles[i] === ')') parensCount--;
        if (smiles[i] === '[') bracketsCount++;
        if (smiles[i] === ']') bracketsCount--;
        
        if (parensCount < 0 || bracketsCount < 0) {
            return false;
        }
    }
    
    return parensCount === 0 && bracketsCount === 0;
}
