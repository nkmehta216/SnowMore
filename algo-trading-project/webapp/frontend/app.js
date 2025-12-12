const API_BASE_URL = 'http://localhost:8000';

// Check API health on load
document.addEventListener('DOMContentLoaded', () => {
    checkAPIStatus();
    loadAvailableModels();
});

async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        const statusElement = document.getElementById('api-status');
        if (data.status === 'healthy') {
            statusElement.textContent = '✅ Online';
            statusElement.style.color = '#28a745';
        } else {
            statusElement.textContent = '⚠️ Issues';
            statusElement.style.color = '#ffc107';
        }
    } catch (error) {
        const statusElement = document.getElementById('api-status');
        statusElement.textContent = '❌ Offline';
        statusElement.style.color = '#dc3545';
    }
}

async function loadAvailableModels() {
    try {
        const response = await fetch(`${API_BASE_URL}/models`);
        const data = await response.json();
        
        const modelsList = document.getElementById('models-list');
        const modelsCount = document.getElementById('models-count');
        
        if (data.available_models && data.available_models.length > 0) {
            modelsList.innerHTML = `
                <ul style="list-style: none; padding: 0;">
                    ${data.available_models.map(model => `
                        <li style="padding: 10px; margin: 5px 0; background: white; border-radius: 6px; border-left: 4px solid #667eea;">
                            📊 ${model}
                        </li>
                    `).join('')}
                </ul>
            `;
            modelsCount.textContent = data.count;
        } else {
            modelsList.innerHTML = '<p class="loading">No models found. Train models first.</p>';
            modelsCount.textContent = '0';
        }
    } catch (error) {
        document.getElementById('models-list').innerHTML = '<p class="error">Failed to load models</p>';
        console.error('Error loading models:', error);
    }
}

async function getPrediction() {
    const ticker = document.getElementById('ticker').value.toUpperCase().trim();
    const resultDiv = document.getElementById('result');
    const signalDisplay = document.getElementById('signal-display');
    
    if (!ticker) {
        alert('Please enter a ticker symbol');
        return;
    }
    
    // Show loading state
    resultDiv.classList.remove('hidden');
    signalDisplay.innerHTML = '<p class="loading">Analyzing...</p>';
    signalDisplay.className = '';
    
    try {
        // For demo purposes, we'll use dummy features
        // In production, these would come from latest market data
        const dummyFeatures = {
            'Close': 150.0,
            'Volume': 1000000,
            'RSI': 45.0,
            'MACD_12_26_9': 2.5,
            'SMA_20': 148.5,
            'SMA_50': 147.0
        };
        
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ticker: ticker,
                features: dummyFeatures
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Display result
        let signalClass = '';
        let signalIcon = '';
        
        switch(data.signal_name) {
            case 'BUY':
                signalClass = 'signal-buy';
                signalIcon = '📈';
                break;
            case 'SELL':
                signalClass = 'signal-sell';
                signalIcon = '📉';
                break;
            case 'HOLD':
                signalClass = 'signal-hold';
                signalIcon = '⏸️';
                break;
        }
        
        signalDisplay.className = signalClass;
        signalDisplay.innerHTML = `
            <div>${signalIcon} ${data.signal_name}</div>
            <div style="font-size: 0.8em; margin-top: 10px;">
                Confidence: ${data.probability ? (data.probability[1] * 100).toFixed(1) + '%' : 'N/A'}
            </div>
        `;
        
    } catch (error) {
        signalDisplay.className = '';
        signalDisplay.innerHTML = `<p class="error">Error: ${error.message}<br>Make sure the API is running and the model exists for ${ticker}</p>`;
        console.error('Error getting prediction:', error);
    }
}

