// Global variable to store current analysis data
let currentAnalysisData = null;

// File upload and form handling
document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a CSV file to upload.');
        return;
    }
    
    showLoading();
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/adlift/analyze', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentAnalysisData = result.data;
            displayResults(result.data);
            showResults();
        } else {
            throw new Error(result.message || 'Analysis failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Analysis failed: ${error.message}`);
        hideLoading();
    }
});

// SIMPLIFIED DISPLAY FUNCTIONS - ONLY 3 SECTIONS AS REQUIRED

function displayResults(data) {
    // 1. DIAGNOSE THE PROBLEM (1-2 reasons)
    displayProblemDiagnosis(data.root_causes);
    
    // 2. PROPOSE SOLUTIONS (AI-driven ways) 
    displayProposedSolutions(data);
    
    // 3. PRIORITIZE & JUSTIFY (Ranked with metrics)
    displayPriorityRanking(data);
}

// 1. Problem Diagnosis Display
function displayProblemDiagnosis(rootCauses) {
    const container = document.getElementById('rootCauses');
    
    if (!rootCauses || rootCauses.length === 0) {
        container.innerHTML = '<p class="no-data">No significant issues detected.</p>';
        return;
    }
    
    const causesHTML = rootCauses.map((cause, index) => `
        <div class="cause-item">
            <div class="cause-header">
                <h4>${index + 1}. ${cause.name}</h4>
                <span class="cause-count">${cause.case_count} campaigns affected</span>
            </div>
            <p class="cause-description">${cause.description}</p>
        </div>
    `).join('');
    
    container.innerHTML = causesHTML;
}

// 2. Proposed Solutions Display
function displayProposedSolutions(data) {
    const container = document.getElementById('proposedSolutions');
    
    const variantsCount = data.variants_data?.variants_count || 0;
    const pauseCount = data.campaign_decisions?.pause_count || 0;
    const keepCount = data.campaign_decisions?.keep_count || 0;
    
    const solutionsHTML = `
        <div class="solution-item">
            <h4>🤖 AI-Driven Variant Generation</h4>
            <p>Generate fresh headlines and descriptions based on top-performing patterns from your data.</p>
            <div class="solution-details">
                <span class="detail-badge">✨ ${variantsCount} variants generated</span>
                <span class="detail-badge">🎯 Pattern-based templates</span>
                <span class="detail-badge">🔍 Quality filtered</span>
            </div>
        </div>
        
        <div class="solution-item">
            <h4>⚡ Smart Campaign Rotation</h4>
            <p>Automatically pause underperformers and scale winning creatives using statistical thresholds.</p>
            <div class="solution-details">
                <span class="detail-badge">⏸️ ${pauseCount} to pause</span>
                <span class="detail-badge">🚀 ${keepCount} to scale</span>
                <span class="detail-badge">📊 Data-driven decisions</span>
            </div>
        </div>
    `;
    
    container.innerHTML = solutionsHTML;
}

// 3. Priority Ranking Display
function displayPriorityRanking(data) {
    const container = document.getElementById('priorityRanking');
    
    // Use actual expected impact data from API
    const expectedImpact = data.expected_impact || {};
    const ctrImprovement = expectedImpact.ctr_improvement || "15-25%";
    const cpqlReduction = expectedImpact.cpql_reduction || "10-20%";
    const variantTimeline = expectedImpact.variant_timeline || "7-14 days";
    const rotationTimeline = expectedImpact.rotation_timeline || "Immediate";
    
    const rankingHTML = `
        <div class="priority-item priority-1">
            <div class="priority-header">
                <h4>🥇 Priority #1: Smart Campaign Rotation</h4>
                <span class="priority-badge">Highest Impact</span>
            </div>
            <div class="priority-metrics">
                <div class="metric">
                    <span class="metric-label">Expected CPQL Reduction:</span>
                    <span class="metric-value">-${cpqlReduction}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Timeline:</span>
                    <span class="metric-value">${rotationTimeline}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Confidence:</span>
                    <span class="metric-value">High (statistical significance)</span>
                </div>
            </div>
            <p class="priority-justification">
                <strong>Why Priority #1:</strong> Immediate cost savings by pausing underperformers. 
                Low-risk, high-impact action based on existing performance data.
            </p>
        </div>
        
        <div class="priority-item priority-2">
            <div class="priority-header">
                <h4>🥈 Priority #2: AI Variant Generation</h4>
                <span class="priority-badge">Medium-High Impact</span>
            </div>
            <div class="priority-metrics">
                <div class="metric">
                    <span class="metric-label">Expected CTR Improvement:</span>
                    <span class="metric-value">+${ctrImprovement}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Timeline:</span>
                    <span class="metric-value">${variantTimeline}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Confidence:</span>
                    <span class="metric-value">Medium (requires testing)</span>
                </div>
            </div>
            <p class="priority-justification">
                <strong>Why Priority #2:</strong> Higher potential upside but requires testing time. 
                Deploy after implementing rotation decisions for compound benefits.
            </p>
        </div>
    `;
    
    container.innerHTML = rankingHTML;
}

// UI State Management
function showLoading() {
    document.getElementById('loadingSection').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('analyzeBtn').disabled = true;
}

function hideLoading() {
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('analyzeBtn').disabled = false;
}

function showResults() {
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('analyzeBtn').disabled = false;
}

// CSV Download Functions
function downloadVariants() {
    if (!currentAnalysisData) {
        alert('No analysis data available. Please run analysis first.');
        return;
    }

    // Use real variants data from the analysis
    const variants = currentAnalysisData.variants_data?.variants || [];
    if (variants.length === 0) {
        alert('No variants data available. Please run analysis first.');
        return;
    }

    const variantsData = [
        ['Headline', 'Description', 'Type', 'Target Segment', 'Placement', 'Keyword Set', 'Keyword Type', 'Similarity Score', 'Bigram Score'],
        ...variants.map(v => [
            v.headline || 'N/A',
            v.description || 'N/A', 
            v.type || 'N/A',
            v.segment || 'N/A',
            v.placement || 'N/A',
            v.keyword_set || 'N/A',
            v.keyword_type || 'N/A',
            v.similarity_score || 'N/A',
            v.bigram_score || 'N/A'
        ])
    ];
    downloadCSV(variantsData, 'adlift_variants.csv');
}

function downloadPrioritization() {
    if (!currentAnalysisData) {
        alert('No analysis data available. Please run analysis first.');
        return;
    }

    // Use real campaign decisions data from the analysis
    const decisions = currentAnalysisData.campaign_decisions;
    if (!decisions) {
        alert('No prioritization data available. Please run analysis first.');
        return;
    }

    const totalCampaigns = decisions.pause_count + decisions.keep_count + decisions.monitor_count;
    
    const prioritizationData = [
        ['Decision', 'Count', 'Percentage', 'Action Required'],
        ['PAUSE', decisions.pause_count, `${((decisions.pause_count / totalCampaigns) * 100).toFixed(1)}%`, 'Stop underperforming campaigns immediately'],
        ['KEEP', decisions.keep_count, `${((decisions.keep_count / totalCampaigns) * 100).toFixed(1)}%`, 'Scale these winning campaigns'],
        ['MONITOR', decisions.monitor_count, `${((decisions.monitor_count / totalCampaigns) * 100).toFixed(1)}%`, 'Watch performance and decide next week']
    ];
    downloadCSV(prioritizationData, 'adlift_prioritization.csv');
}

function downloadAllFiles() {
    downloadVariants();
    setTimeout(() => downloadPrioritization(), 500);
}

function downloadCSV(data, filename) {
    const csvContent = data.map(row => 
        row.map(cell => {
            // Handle cells that contain commas or quotes
            if (typeof cell === 'string' && (cell.includes(',') || cell.includes('"'))) {
                return `"${cell.replace(/"/g, '""')}"`;
            }
            return cell;
        }).join(',')
    ).join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}