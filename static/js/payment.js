// 页面元素
const waitingStatus = document.getElementById('waitingStatus');
const paymentForm = document.getElementById('paymentForm');
const plateNumber = document.getElementById('plateNumber');
const amountInput = document.getElementById('amountInput');
const payBtn = document.getElementById('payBtn');

// 全局变量
let pollingInterval = null;
let currentRecognitionId = null;
let lastCheckedId = -1;

// 页面加载时开始监听
window.addEventListener('load', () => {
    startMonitoring();
});

// 开始监听最新的识别结果
function startMonitoring() {
    console.log('🔍 开始监听车牌识别...');
    
    pollingInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/latest_recognition');
            const result = await response.json();
            
            if (response.ok && result.recognition_id) {
                const recognitionId = parseInt(result.recognition_id);
                
                // 如果是新的识别记录
                if (recognitionId > lastCheckedId) {
                    console.log('🆕 发现新的识别记录:', result);
                    lastCheckedId = recognitionId;
                    
                    // 如果识别成功
                    if (result.code === '0' && result.plate_number) {
                        currentRecognitionId = result.recognition_id;
                        showPaymentForm(result.plate_number);
                    }
                }
            }
        } catch (error) {
            console.error('❌ 监听错误:', error);
        }
    }, 2000); // 每2秒检查一次
}

// 显示付款表单
function showPaymentForm(plate) {
    console.log('💳 显示付款表单，车牌号:', plate);
    waitingStatus.style.display = 'none';
    paymentForm.style.display = 'block';
    plateNumber.textContent = plate;
    
    // 自动聚焦到金额输入框
    amountInput.focus();
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
    
    if (!currentRecognitionId) {
        alert('未找到识别记录');
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
                recognition_id: currentRecognitionId,
                amount: amount
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.code === '0') {
            console.log('✅ 付款成功');
            // 停止监听
            if (pollingInterval) {
                clearInterval(pollingInterval);
            }
            // 跳转到成功页面
            window.location.href = `/success?plate=${encodeURIComponent(result.plate_number)}`;
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

// 页面卸载时停止监听
window.addEventListener('beforeunload', () => {
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
});
