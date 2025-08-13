// Global variables
let currentAnalysisData = null;

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const csvFileInput = document.getElementById('csvFile');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
});

function setupEventListeners() {
    // File input change
    csvFileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Click to upload
    uploadArea.addEventListener('click', () => csvFileInput.click());
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file && file.type === 'text/csv') {
        processFile(file);
    } else {
        showError('Please select a valid CSV file');
    }
}

function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0 && files[0].type === 'text/csv') {
        processFile(files[0]);
    } else {
        showError('Please drop a valid CSV file');
    }
}

async function processFile(file) {
    try {
        showLoading();
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            currentAnalysisData = result.data;
            displayResults(result.data);
            hideLoading();
            showResults();
        } else {
            throw new Error(result.message || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
        hideLoading();
    }
}

function displayResults(data) {
    // Performance Metrics
    displayPerformanceMetrics(data.performance_variance);
    
    // Root Causes
    displayRootCauses(data.root_causes);
    
    // Campaign Decisions
    displayCampaignDecisions(data.campaign_decisions);
    
    // Fatigue Detection
    if (data.fatigue_detection && data.fatigue_detection.length > 0) {
        displayFatigueDetection(data.fatigue_detection);
        document.getElementById('fatigueSection').style.display = 'block';
    }
    
    // Expected Impact
    displayExpectedImpact(data.expected_impact);
}

function displayPerformanceMetrics(metrics) {
    const container = document.getElementById('performanceMetrics');
    
    const metricsHTML = `
        <div class="metric-item">
            <div class="metric-value">${metrics.ctr_range}</div>
            <div class="metric-label">CTR Range</div>
        </div>
        <div class="metric-item">
            <div class="metric-value">${metrics.ctr_variance}</div>
            <div class="metric-label">CTR Variance</div>
        </div>
        <div class="metric-item">
            <div class="metric-value">${metrics.cpql_range}</div>
            <div class="metric-label">CPQL Range</div>
        </div>
        <div class="metric-item">
            <div class="metric-value">${metrics.cpql_variance}</div>
            <div class="metric-label">CPQL Variance</div>
        </div>
        <div class="metric-item">
            <div class="metric-value">${metrics.qpi_range}</div>
            <div class="metric-label">QPI Range</div>
        </div>
        <div class="metric-item">
            <div class="metric-value">${metrics.total_campaigns}</div>
            <div class="metric-label">Total Campaigns</div>
        </div>
    `;
    
    container.innerHTML = metricsHTML;
}

function displayRootCauses(rootCauses) {
    const container = document.getElementById('rootCauses');
    
    let rootCausesHTML = '';
    
    rootCauses.forEach((cause, index) => {
        const evidenceTable = createEvidenceTable(cause.evidence);
        
        rootCausesHTML += `
            <div class="root-cause-item" style="margin-bottom: 25px; padding: 20px; background: #f8f9ff; border-radius: 10px; border-left: 4px solid #dc3545;">
                <h4 style="color: #dc3545; margin-bottom: 10px;">${cause.name}</h4>
                <p style="color: #666; margin-bottom: 15px;">${cause.description}</p>
                <p style="color: #333; font-weight: 600;">Cases Found: ${cause.case_count}</p>
                ${evidenceTable}
            </div>
        `;
    });
    
    container.innerHTML = rootCausesHTML;
}

function createEvidenceTable(evidence) {
    if (!evidence || evidence.length === 0) return '';
    
    const headers = Object.keys(evidence[0]);
    
    let tableHTML = '<div class="evidence-table"><table><thead><tr>';
    headers.forEach(header => {
        tableHTML += `<th>${header.replace(/_/g, ' ').toUpperCase()}</th>`;
    });
    tableHTML += '</tr></thead><tbody>';
    
    evidence.forEach(row => {
        tableHTML += '<tr>';
        headers.forEach(header => {
            let value = row[header];
            if (header === 'CTR' || header === 'CVR' || header === 'qualified_rate') {
                value = `${(value * 100).toFixed(2)}%`;
            } else if (header === 'QPI') {
                value = value.toFixed(4);
            } else if (header === 'CPQL') {
                value = `₹${value.toFixed(0)}`;
            }
            tableHTML += `<td>${value}</td>`;
        });
        tableHTML += '</tr>';
    });
    
    tableHTML += '</tbody></table></div>';
    return tableHTML;
}

function displayCampaignDecisions(decisions) {
    const container = document.getElementById('campaignDecisions');
    
    const decisionsHTML = `
        <div class="decision-card pause">
            <div class="decision-count">${decisions.pause_count}</div>
            <div class="decision-label">PAUSE</div>
        </div>
        <div class="decision-card keep">
            <div class="decision-count">${decisions.keep_count}</div>
            <div class="decision-label">KEEP</div>
        </div>
        <div class="decision-card monitor">
            <div class="decision-count">${decisions.monitor_count}</div>
            <div class="decision-label">MONITOR</div>
        </div>
    `;
    
    container.innerHTML = decisionsHTML;
}

function displayFatigueDetection(fatigueData) {
    const container = document.getElementById('fatigueDetection');
    
    let fatigueHTML = '<p style="color: #666; margin-bottom: 15px;">Detected fatigued creatives:</p>';
    
    fatigueData.forEach(item => {
        fatigueHTML += `
            <div style="padding: 15px; background: #fff3cd; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #ffc107;">
                <strong>${item.headline}</strong><br>
                <span style="color: #666;">Segment: ${item.segment} | Fatigue Ratio: ${(item.fatigue_ratio * 100).toFixed(1)}% | Days Live: ${item.days_live}</span>
            </div>
        `;
    });
    
    container.innerHTML = fatigueHTML;
}

function displayExpectedImpact(impact) {
    const container = document.getElementById('expectedImpact');
    
    const impactHTML = `
        <div class="impact-item">
            <div class="impact-value">${impact.ctr_improvement}</div>
            <div class="impact-label">CTR Improvement</div>
        </div>
        <div class="impact-item">
            <div class="impact-value">${impact.cpql_reduction}</div>
            <div class="impact-label">CPQL Reduction</div>
        </div>
        <div class="impact-item">
            <div class="impact-value">${impact.timeline}</div>
            <div class="impact-label">Timeline</div>
        </div>
        <div class="impact-item">
            <div class="impact-value">${impact.qualified_leads_improvement}</div>
            <div class="impact-label">Qualified Leads</div>
        </div>
        <div class="impact-item">
            <div class="impact-value">${impact.cac_reduction}</div>
            <div class="impact-label">CAC Reduction</div>
        </div>
    `;
    
    container.innerHTML = impactHTML;
}

// Download functions
function downloadVariants() {
    if (!currentAnalysisData) return;
    
    // For MVP, we'll create a sample variants CSV
    const variantsData = generateSampleVariants();
    downloadCSV(variantsData, 'adlift_variants.csv');
}

function downloadPrioritization() {
    if (!currentAnalysisData) return;
    
    // For MVP, we'll create a sample prioritization CSV
    const prioritizationData = generateSamplePrioritization();
    downloadCSV(prioritizationData, 'adlift_prioritization.csv');
}

function downloadAllFiles() {
    downloadVariants();
    setTimeout(() => downloadPrioritization(), 500);
}

function generateSampleVariants() {
    // Sample data structure for variants
    return [
        ['Headline', 'Description', 'Keywords', 'Type', 'Target Segment', 'Quality Score'],
        ['Boost Your Career with Data Science', 'Master data science skills for better job prospects', 'data science, career, skills', 'Winner-like', 'Graduates', '0.85'],
        ['Data Science for Working Professionals', 'Advance your career with data science expertise', 'data science, professional, career', 'Explorer', 'Working Professionals', '0.78']
    ];
}

function generateSamplePrioritization() {
    // Sample data structure for prioritization
    return [
        ['Campaign', 'Ad Group', 'Headline', 'Decision', 'Reason', 'QPI', 'CPQL'],
        ['Data Science', 'Graduates', 'Learn Data Science', 'KEEP', 'High QPI, Low CPQL', '0.0023', '₹450'],
        ['Data Science', 'Professionals', 'Career Boost', 'PAUSE', 'Low QPI, High CPQL', '0.0011', '₹1200']
    ];
}

function downloadCSV(data, filename) {
    const csvContent = data.map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// UI state functions
function showLoading() {
    loadingSection.style.display = 'block';
    uploadArea.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
}

function hideLoading() {
    loadingSection.style.display = 'none';
}

function showResults() {
    resultsSection.style.display = 'block';
    uploadArea.style.display = 'block';
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    errorSection.style.display = 'block';
    uploadArea.style.display = 'block';
}

function resetForm() {
    errorSection.style.display = 'none';
    resultsSection.style.display = 'none';
    loadingSection.style.display = 'none';
    uploadArea.style.display = 'block';
    csvFileInput.value = '';
    currentAnalysisData = null;
}
