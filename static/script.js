// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    console.log("DeepGuard AI - Script loaded");
    
    // Get elements
    const fileInput = document.getElementById('fileInput');
    const fileText = document.getElementById('fileText');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const uploadBox = document.getElementById('uploadBox');
    const removeFileBtn = document.getElementById('removeFile');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const form = document.getElementById('uploadForm');
    
    // If file input exists (index page)
    if (fileInput) {
        // File selection via input
        fileInput.addEventListener('change', function(e) {
            console.log("File input changed");
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                const sizeKB = (file.size / 1024).toFixed(2);
                const sizeMB = (sizeKB / 1024).toFixed(2);
                const displaySize = sizeKB > 1024 ? `${sizeMB} MB` : `${sizeKB} KB`;
                
                if (fileText) fileText.innerText = file.name;
                if (fileName) fileName.innerText = file.name;
                if (fileSize) fileSize.innerText = displaySize;
                if (fileInfo) fileInfo.style.display = "flex";
                
                if (uploadBox) {
                    uploadBox.style.borderColor = "#00c6ff";
                    uploadBox.style.background = "rgba(0,198,255,0.05)";
                }
                
                console.log("File selected:", file.name);
                showToast("File selected: " + file.name, "success");
            }
        });
        
        // Click on upload box triggers file input
        if (uploadBox) {
            uploadBox.addEventListener('click', function(e) {
                // Don't trigger if clicking on remove button
                if (e.target === removeFileBtn || (removeFileBtn && removeFileBtn.contains(e.target))) {
                    return;
                }
                console.log("Upload box clicked");
                fileInput.click();
            });
        }
        
        // Remove file button
        if (removeFileBtn) {
            removeFileBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                fileInput.value = "";
                if (fileInfo) fileInfo.style.display = "none";
                if (fileText) fileText.innerText = "Choose a file or drag & drop";
                if (uploadBox) {
                    uploadBox.style.borderColor = "rgba(255,255,255,0.3)";
                    uploadBox.style.background = "transparent";
                }
                showToast("File removed", "info");
            });
        }
        
        // Drag and drop
        if (uploadBox) {
            uploadBox.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.style.borderColor = "#00c6ff";
                this.style.background = "rgba(0,198,255,0.1)";
            });
            
            uploadBox.addEventListener('dragleave', function(e) {
                e.preventDefault();
                this.style.borderColor = "rgba(255,255,255,0.3)";
                this.style.background = "transparent";
            });
            
            uploadBox.addEventListener('drop', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    const changeEvent = new Event('change');
                    fileInput.dispatchEvent(changeEvent);
                }
                
                this.style.borderColor = "rgba(255,255,255,0.3)";
                this.style.background = "transparent";
            });
        }
        
        // Form submit
        if (form) {
            form.addEventListener('submit', function(e) {
                if (!fileInput.files.length) {
                    e.preventDefault();
                    showToast("Please select a file first!", "error");
                    return;
                }
                
                if (analyzeBtn) {
                    analyzeBtn.disabled = true;
                    analyzeBtn.innerHTML = '<span class="btn-text">Analyzing...</span><span class="btn-icon">🤖</span>';
                }
                
                const loadingOverlay = document.getElementById('loadingOverlay');
                if (loadingOverlay) loadingOverlay.classList.add('active');
            });
        }
    }
    
    // Toast function
    function showToast(message, type) {
        let toast = document.getElementById('toastNotification');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'toastNotification';
            toast.style.cssText = `
                position: fixed;
                bottom: 30px;
                right: 30px;
                background: rgba(0,0,0,0.9);
                backdrop-filter: blur(10px);
                border: 1px solid #00c6ff;
                border-radius: 12px;
                padding: 12px 24px;
                color: white;
                z-index: 9999;
                transform: translateX(400px);
                transition: transform 0.3s ease;
                font-size: 14px;
                font-weight: 500;
            `;
            document.body.appendChild(toast);
        }
        
        toast.innerHTML = message;
        toast.style.transform = 'translateX(0)';
        
        setTimeout(() => {
            toast.style.transform = 'translateX(400px)';
        }, 3000);
    }
    
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.feature-card, .glass-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.6s ease';
        observer.observe(card);
    });
    
    console.log("DeepGuard AI - Ready!");
});