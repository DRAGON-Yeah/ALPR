// 页面元素
const uploadPage = document.getElementById('uploadPage');
const paymentPage = document.getElementById('paymentPage');
const resultPage = document.getElementById('resultPage');

const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const previewImage = document.getElementById('previewImage');
const uploadBtn = document.getElementById('uploadBtn');

const recognitionStatus = document.getElementById('recognitionStatus');
const paymentForm = document.getElementById('paymentForm');
const plateNumber = document.getElementById('plateNumber');
const amountInput = document.getElementById('amountInput');
const payBtn = document.getElementById('payBtn');
const backToUpload = document.getElementById('backToUpload');

const resultPlateNumber = document.getElementById('resultPlateNumber');
const newTransaction = document.getElementById('newTransaction');

// 全局变量
let selectedFile = null;
let recognitionId = null;
let pollingInterval = null;

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
        };
        reader.readAsDataURL(file);
    }
});

// 上传并识别
uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        alert('请先选择图片');
        return;
    }
    
    uploadBtn.disabled = true;
    uploadBtn.textContent = '上传中...';
    
    try {
        const formData = new FormData();
        formData.append('image', selectedFile);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            recognitionId = result.recognition_id;
            showPage('payment');
            startPolling();
        } else {
            alert(`上传失败: ${result.message}`);
            uploadBtn.disabled = false;
            uploadBtn.textContent = '开始识别';
        }
    } catch (error) {
        alert(`上传失败: ${error.message}`);
        uploadBtn.disabled = false;
        uploadBtn.textContent = '开始识别';
    }
});

// 轮询识别状态
function startPolling() {
    recognitionStatus.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>正在识别车牌...</p>
        </div>
    `;
    
    pollingInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/check_status/${recognitionId}`);
            const result = await response.json();
            
            if (result.code === '0') {
                // 识别成功
                clearInterval(pollingInterval);
                showPaymentForm(result.plate_number);
            } else if (result.code !== '0' && result.message !== '识别中...') {
                // 识别失败
                clearInterval(pollingInterval);
                recognitionStatus.innerHTML = `
                    <div class="error-message">
                        <p>❌ ${result.message}</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('轮询错误:', error);
        }
    }, 2000); // 每2秒轮询一次
}

// 显示付款表单
function showPaymentForm(plate) {
    recognitionStatus.style.display = 'none';
    paymentForm.style.display = 'block';
    plateNumber.textContent = plate;
}

// 处理付款
payBtn.addEventListener('click', async () => {
    const amount = amountInput.value;
    
    if (!amount) {
        alert('请输入付款金额');
        return;
    }
    
    if (parseFloat(amount) !== 10) {
        alert('付款金额应为10元');
        return;
    }
    
    payBtn.disabled = true;
    payBtn.textContent = '处理中...';
    
    try {
        const response = await fetch('/api/payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                recognition_id: recognitionId,
                amount: amount
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.code === '0') {
            resultPlateNumber.textContent = result.plate_number;
            showPage('result');
        } else {
            alert(`付款失败: ${result.message}`);
            payBtn.disabled = false;
            payBtn.textContent = '确认付款';
        }
    } catch (error) {
        alert(`付款失败: ${error.message}`);
        payBtn.disabled = false;
        payBtn.textContent = '确认付款';
    }
});

// 返回上传页面
backToUpload.addEventListener('click', () => {
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
    resetUploadPage();
    showPage('upload');
});

// 开始新的交易
newTransaction.addEventListener('click', () => {
    resetUploadPage();
    showPage('upload');
});

// 重置上传页面
function resetUploadPage() {
    selectedFile = null;
    recognitionId = null;
    fileInput.value = '';
    previewImage.style.display = 'none';
    previewImage.src = '';
    document.querySelector('.upload-content').style.display = 'block';
    uploadBtn.style.display = 'none';
    uploadBtn.disabled = false;
    uploadBtn.textContent = '开始识别';
    amountInput.value = '';
    payBtn.disabled = false;
    payBtn.textContent = '确认付款';
    paymentForm.style.display = 'none';
    recognitionStatus.style.display = 'block';
}

// 显示指定页面
function showPage(page) {
    uploadPage.classList.remove('active');
    paymentPage.classList.remove('active');
    resultPage.classList.remove('active');
    
    switch(page) {
        case 'upload':
            uploadPage.classList.add('active');
            break;
        case 'payment':
            paymentPage.classList.add('active');
            break;
        case 'result':
            resultPage.classList.add('active');
            break;
    }
}
