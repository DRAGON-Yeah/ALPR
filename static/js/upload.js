// 页面元素
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const previewImage = document.getElementById('previewImage');
const uploadBtn = document.getElementById('uploadBtn');
const uploadStatus = document.getElementById('uploadStatus');

// 全局变量
let selectedFile = null;

// 文件选择
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        selectedFile = file;
        
        // 显示预览
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            previewImage.style.display = 'block';
            document.querySelector('.upload-content').style.display = 'none';
            uploadBtn.style.display = 'block';
            uploadStatus.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
});

// 上传并识别
uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        showStatus('请先选择图片', 'error');
        return;
    }
    
    uploadBtn.disabled = true;
    uploadBtn.textContent = '上传中...';
    showStatus('正在上传图片...', 'info');
    
    try {
        const formData = new FormData();
        formData.append('image', selectedFile);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showStatus('✅ 上传成功！识别ID: ' + result.recognition_id, 'success');
            
            // 2秒后重置页面，准备下一次上传
            setTimeout(() => {
                resetPage();
            }, 2000);
        } else {
            showStatus(`❌ 上传失败: ${result.message}`, 'error');
            uploadBtn.disabled = false;
            uploadBtn.textContent = '开始识别';
        }
    } catch (error) {
        showStatus(`❌ 上传失败: ${error.message}`, 'error');
        uploadBtn.disabled = false;
        uploadBtn.textContent = '开始识别';
    }
});

// 显示状态消息
function showStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = 'status-message ' + type;
    uploadStatus.style.display = 'block';
}

// 重置页面
function resetPage() {
    selectedFile = null;
    fileInput.value = '';
    previewImage.style.display = 'none';
    previewImage.src = '';
    document.querySelector('.upload-content').style.display = 'block';
    uploadBtn.style.display = 'none';
    uploadBtn.disabled = false;
    uploadBtn.textContent = '开始识别';
    uploadStatus.style.display = 'none';
}
