// Global variable to store current analysis data
let currentAnalysisData = null;

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 AdLift Frontend Loaded - Initializing...');
    
    // Get DOM elements
    const dragDropArea = document.getElementById('dragDropArea');
    const csvFile = document.getElementById('csvFile');
    const fileStatus = document.getElementById('fileStatus');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const removeFileBtn = document.getElementById('removeFileBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingSection = document.getElementById('loadingSection');
    const resultsSection = document.getElementById('resultsSection');
    
    if (!dragDropArea || !csvFile || !analyzeBtn) {
        console.error('❌ Required elements not found');
        return;
    }
    
    console.log('✅ All elements found, setting up event listeners...');
    
    // File selection state
    let selectedFile = null;
    
    // Drag & Drop Events
    dragDropArea.addEventListener('click', () => csvFile.click());
    
    dragDropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dragDropArea.classList.add('dragover');
    });
    
    dragDropArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dragDropArea.classList.remove('dragover');
    });
    
    dragDropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dragDropArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });
    
    // File input change
    csvFile.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });
    
    // Remove file button
    removeFileBtn.addEventListener('click', () => {
        clearFileSelection();
    });
    
    // Analyze button
    analyzeBtn.addEventListener('click', () => {
        if (selectedFile) {
            uploadAndAnalyze(selectedFile);
        }
    });
    
    // Handle file selection
    function handleFileSelection(file) {
        console.log('📁 File selected:', file.name);
        
        // Validate file type
        if (!file.name.toLowerCase().endsWith('.csv')) {
            alert('Please select a CSV file only.');
            return;
        }
        
        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('File size must be less than 10MB.');
            return;
        }
        
        selectedFile = file;
        
        // Update UI
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        
        // Show file status, hide drag area
        dragDropArea.style.display = 'none';
        fileStatus.style.display = 'block';
        analyzeBtn.disabled = false;
        
        console.log('✅ File ready for upload:', file.name);
    }
    
    // Clear file selection
    function clearFileSelection() {
        selectedFile = null;
        csvFile.value = '';
        
        // Reset UI
        dragDropArea.style.display = 'block';
        fileStatus.style.display = 'none';
        analyzeBtn.disabled = true;
        
        console.log('🗑️ File selection cleared');
    }
    
    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Upload and analyze file
    async function uploadAndAnalyze(file) {
        console.log('🚀 Starting upload and analysis...');
        
        try {
            showLoading();
            
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/api/adlift/analyze', {
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
                showResults();
                console.log('✅ Analysis completed successfully!');
            } else {
                throw new Error(result.message || 'Analysis failed');
            }
            
        } catch (error) {
            console.error('❌ Analysis failed:', error);
            alert(`Analysis failed: ${error.message}`);
        } finally {
            hideLoading();
        }
    }
    
    // UI State Functions
    function showLoading() {
        loadingSection.style.display = 'block';
        analyzeBtn.disabled = true;
        analyzeBtn.textContent = '⏳ Analyzing...';
    }
    
    function hideLoading() {
        loadingSection.style.display = 'none';
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = '🚀 Analyze Campaign Data';
    }
    
    function showResults() {
        resultsSection.style.display = 'block';
    }
    
    console.log('🎯 Event listeners attached successfully!');
});

// DISPLAY FUNCTIONS - ONLY 3 SECTIONS AS REQUIRED

function displayResults(data) {
    console.log('📊 Displaying results:', data);
    
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
    const expectedImpact = data.expected_impact || {};
    
    // Use dynamic values from API or provide meaningful defaults
    const ctrImprovement = expectedImpact.ctr_improvement || "15-25%";
    const cpqlReduction = expectedImpact.cpql_reduction || "10-20%";
    const variantTimeline = expectedImpact.variant_timeline || "7-14 days";
    const rotationTimeline = expectedImpact.rotation_timeline || "Immediate";
    const confidenceLevel = expectedImpact.confidence_level || "Medium";
    
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
                    <span class="metric-value">${confidenceLevel}</span>
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
                    <span class="metric-value">${confidenceLevel}</span>
                </div>
            </div>
            <p class="priority-justification">
                <strong>Why Priority #2:</strong> Higher potential upside by testing fresh creatives. 
                Requires some testing time to find new winners.
            </p>
        </div>
    `;
    
    container.innerHTML = rankingHTML;
}

// CSV DOWNLOAD FUNCTIONS - Only triggered by button clicks

function downloadVariants() {
    if (!currentAnalysisData || !currentAnalysisData.variants_data?.variants) {
        alert('No variants data available. Please run analysis first.');
        return;
    }
    
    console.log('📥 Downloading detailed variants CSV...');
    
    const variants = currentAnalysisData.variants_data.variants;
    const variantsData = [
        ['Headline', 'Description', 'Type', 'Target Segment', 'Placement', 'Keyword Set', 'Keyword Type', 'Generated From', 'Use Case']
    ];
    
    variants.forEach((v, index) => {
        const useCase = v.type === 'winner-like' ? 'High confidence - based on top performers' : 'Explorer - test new creative directions';
        const generatedFrom = v.type === 'winner-like' ? 'Top performing patterns' : 'Creative exploration';
        
        variantsData.push([
            v.headline || 'N/A',
            v.description || 'N/A', 
            v.type || 'N/A',
            v.segment || 'N/A',
            v.placement || 'N/A',
            v.keyword_set || 'N/A',
            v.keyword_type || 'N/A',
            generatedFrom,
            useCase
        ]);
    });
    
    downloadCSV(variantsData, 'adlift_detailed_variants.csv');
}

function downloadPrioritization() {
    if (!currentAnalysisData || !currentAnalysisData.campaign_decisions) {
        alert('No prioritization data available. Please run analysis first.');
        return;
    }
    
    console.log('📥 Downloading detailed campaign decisions CSV...');
    
    // Get detailed campaign data if available
    const campaignDetails = currentAnalysisData.campaign_details;
    const decisions = currentAnalysisData.campaign_decisions;
    
    if (campaignDetails && Object.keys(campaignDetails).length > 0) {
        // Create detailed CSV with all campaign information
        const detailedData = [
            ['Decision', 'Campaign Name', 'Ad Group', 'Segment', 'Placement', 'Headline', 'Description', 'QPI', 'CPQL', 'Score', 'Reason', 'Action Required']
        ];
        
        // Add PAUSE campaigns
        if (campaignDetails.pause && campaignDetails.pause.length > 0) {
            campaignDetails.pause.forEach(campaign => {
                detailedData.push([
                    'PAUSE',
                    campaign.campaign_name,
                    campaign.ad_group,
                    campaign.segment,
                    campaign.placement,
                    campaign.headline,
                    campaign.description,
                    campaign.qpi,
                    campaign.cpql,
                    campaign.score,
                    campaign.reason,
                    'Stop underperforming campaign immediately'
                ]);
            });
        }
        
        // Add KEEP campaigns
        if (campaignDetails.keep && campaignDetails.keep.length > 0) {
            campaignDetails.keep.forEach(campaign => {
                detailedData.push([
                    'KEEP',
                    campaign.campaign_name,
                    campaign.ad_group,
                    campaign.segment,
                    campaign.placement,
                    campaign.headline,
                    campaign.description,
                    campaign.qpi,
                    campaign.cpql,
                    campaign.score,
                    campaign.reason,
                    'Scale this winning campaign'
                ]);
            });
        }
        
        // Add MONITOR campaigns
        if (campaignDetails.monitor && campaignDetails.monitor.length > 0) {
            campaignDetails.monitor.forEach(campaign => {
                detailedData.push([
                    'MONITOR',
                    campaign.campaign_name,
                    campaign.ad_group,
                    campaign.segment,
                    campaign.placement,
                    campaign.headline,
                    campaign.description,
                    campaign.qpi,
                    campaign.cpql,
                    campaign.score,
                    campaign.reason,
                    'Watch performance and decide next week'
                ]);
            });
        }
        
        downloadCSV(detailedData, 'adlift_detailed_campaign_decisions.csv');
        
    } else {
        // Fallback to summary data if detailed data not available
        const totalCampaigns = decisions.pause_count + decisions.keep_count + decisions.monitor_count;
        
        const summaryData = [
            ['Decision', 'Count', 'Percentage', 'Action Required'],
            ['PAUSE', decisions.pause_count, `${((decisions.pause_count / totalCampaigns) * 100).toFixed(1)}%`, 'Stop underperforming campaigns immediately'],
            ['KEEP', decisions.keep_count, `${((decisions.keep_count / totalCampaigns) * 100).toFixed(1)}%`, 'Scale these winning campaigns'],
            ['MONITOR', decisions.monitor_count, `${((decisions.monitor_count / totalCampaigns) * 100).toFixed(1)}%`, 'Watch performance and decide next week']
        ];
        
        downloadCSV(summaryData, 'adlift_campaign_summary.csv');
    }
}

function downloadAllFiles() {
    console.log('📦 Downloading all files...');
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
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    console.log(`✅ Downloaded: ${filename}`);
}