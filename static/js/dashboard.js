// Dashboard Auto-Refresh and Manual Run Functionality

(function() {
    const config = {
        refreshInterval: 30000, // 30 seconds (from config.yaml)
        apiEndpoint: '/api/stats'
    };
    
    let refreshTimer = null;
    
    // Auto-refresh dashboard data
    function refreshDashboard() {
        fetch(config.apiEndpoint)
            .then(response => response.json())
            .then(data => {
                updateDashboard(data);
            })
            .catch(error => {
                console.error('Error refreshing dashboard:', error);
            });
    }
    
    // Update dashboard with new data
    function updateDashboard(data) {
        const stats = data.stats;
        
        // Update stat cards
        document.getElementById('total-reviews').textContent = formatNumber(stats.total_reviews);
        document.getElementById('total-whiskeys').textContent = formatNumber(stats.total_whiskeys);
        document.getElementById('reviews-today').textContent = stats.reviews_today;
        document.getElementById('reviews-week').textContent = stats.reviews_this_week;
        
        // Update last captured
        document.getElementById('last-scraped').textContent = stats.last_review_captured || 'No reviews yet';
        document.getElementById('last-published').textContent = stats.last_review_published || 'N/A';
        document.getElementById('last-update').textContent = new Date().toLocaleString();
        
        // Update reviews by site table
        updateReviewsBySite(stats.reviews_by_site);
        
        // Update recent reviews table
        updateRecentReviews(stats.recent_reviews);
        
        // Update error reports
        updateErrorReports(data.error_reports);
        
        // Update daily summaries
        updateDailySummaries(data.daily_summaries);
    }
    
    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }
    
    function updateReviewsBySite(sites) {
        const tbody = document.getElementById('reviews-by-site');
        tbody.innerHTML = '';
        
        for (const [site, count] of Object.entries(sites)) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${site}</td>
                <td style="text-align: right;">${formatNumber(count)}</td>
            `;
            tbody.appendChild(row);
        }
    }
    
    function updateRecentReviews(reviews) {
        const tbody = document.getElementById('recent-reviews');
        tbody.innerHTML = '';
        
        reviews.forEach(review => {
            const row = document.createElement('tr');
            const name = review[1].length > 60 ? review[1].substring(0, 60) + '...' : review[1];
            row.innerHTML = `
                <td>${review[0]}</td>
                <td>${review[2]}</td>
                <td>${name}</td>
                <td><a href="${review[3]}" target="_blank">View</a></td>
                <td><a href="/review/${review[0]}">View Details</a></td>
            `;
            tbody.appendChild(row);
        });
    }
    
    function updateErrorReports(reports) {
        const tbody = document.getElementById('error-reports');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        reports.forEach(report => {
            const row = document.createElement('tr');
            row.className = `status-${report.status}`;
            
            const statusIcon = {
                'success': '✅',
                'partial': '⚠️',
                'error': '❌',
                'skipped': '⊘'
            }[report.status] || '';
            
            const errorHtml = report.error_message 
                ? `<details><summary>View Error</summary><pre>${escapeHtml(report.error_message)}</pre></details>`
                : '-';
            
            row.innerHTML = `
                <td>${report.run_date}</td>
                <td>${report.source_site}</td>
                <td>${statusIcon} ${report.status.toUpperCase()}</td>
                <td>${report.reviews_found}</td>
                <td>${report.reviews_added}</td>
                <td>${errorHtml}</td>
            `;
            tbody.appendChild(row);
        });
    }
    
    function updateDailySummaries(summaries) {
        const tbody = document.getElementById('daily-summaries');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        summaries.forEach(summary => {
            const row = document.createElement('tr');
            row.className = `status-${summary.status}`;
            
            const statusIcon = {
                'success': '✅',
                'partial': '⚠️',
                'error': '❌',
                'skipped': '⊘'
            }[summary.status] || '';
            
            row.innerHTML = `
                <td>${summary.summary_date}</td>
                <td>${statusIcon} ${summary.status.toUpperCase()}</td>
                <td>${summary.total_reviews_found}</td>
                <td>${summary.total_reviews_added}</td>
                <td>${summary.total_duplicates}</td>
                <td>${summary.total_errors}</td>
                <td>${(summary.execution_time || 0).toFixed(2)}s</td>
            `;
            tbody.appendChild(row);
        });
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Manual scraper run
    const runBtn = document.getElementById('run-scraper-btn');
    const statusDiv = document.getElementById('scraper-status');
    
    if (runBtn) {
        runBtn.addEventListener('click', function() {
            runBtn.disabled = true;
            statusDiv.className = 'scraper-status active';
            statusDiv.textContent = 'Starting scraper...';
            
            const eventSource = new EventSource('/api/run-scraper');
            
            eventSource.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                if (data.error) {
                    statusDiv.className = 'scraper-status error';
                    statusDiv.textContent = 'Error: ' + data.error;
                    runBtn.disabled = false;
                    eventSource.close();
                } else if (data.status === 'complete') {
                    statusDiv.className = 'scraper-status success';
                    statusDiv.textContent = 'Scraper completed! Refreshing dashboard...';
                    runBtn.disabled = false;
                    eventSource.close();
                    
                    // Refresh dashboard after completion
                    setTimeout(refreshDashboard, 2000);
                } else if (data.message) {
                    statusDiv.textContent = data.message;
                }
            };
            
            eventSource.onerror = function() {
                statusDiv.className = 'scraper-status error';
                statusDiv.textContent = 'Connection error';
                runBtn.disabled = false;
                eventSource.close();
            };
        });
    }
    
    // Start auto-refresh
    refreshTimer = setInterval(refreshDashboard, config.refreshInterval);
    
    // Also refresh on page load
    window.addEventListener('load', function() {
        setTimeout(refreshDashboard, 1000);
    });
})();

