// Basic interactions for the prototype

document.addEventListener('DOMContentLoaded', function () {
    console.log("AgriSmart System Loaded");

    // Mobile Navigation Toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    // Placeholder for "Learn More" buttons
    const learnMoreBtns = document.querySelectorAll('.btn-card');
    learnMoreBtns.forEach(btn => {
        btn.addEventListener('click', function (e) {
            if (this.tagName === 'BUTTON') {
                alert("This feature module will provide detailed analytics and controls in the full version.");
            }
        });
    });

    // Voice Support Mock
    const voiceCard = document.querySelector('.card .fa-microphone').parentElement;
    if (voiceCard) {
        const voiceBtn = voiceCard.querySelector('button');
        voiceBtn.addEventListener('click', () => {
            alert("Listening... (Voice Support Activated)");
        });
    }

    // Dashboard features
    initDashboard();

    // Disease Detection Logic
    initDiseaseDetection();

    // Market Price Filters
    initMarketTable();
});

function initDashboard() {
    // Only run if chart canvas exists
    const ctx = document.getElementById('soilChart');
    if (ctx) {
        // Mock Chart Data
        new Chart(ctx, {
            type: 'bar', // Using bar for clear comparison, could be line
            data: {
                labels: ['Moisture', 'pH', 'Temp (°C)', 'Humidity (%)'],
                datasets: [{
                    label: 'Current Levels',
                    data: [65, 6.8, 28, 75],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.6)', // Blue for Moisture
                        'rgba(255, 206, 86, 0.6)', // Yellow for pH
                        'rgba(255, 99, 132, 0.6)', // Red for Temp
                        'rgba(75, 192, 192, 0.6)'  // Green for Humidity
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

function initDiseaseDetection() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', () => {
            const input = document.getElementById('cropImage');
            if (input.files && input.files[0]) {
                // Mock Processing
                document.getElementById('resultSection').style.display = 'block';
                document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
            } else {
                alert("Please upload an image first.");
            }
        });
    }
}

function initMarketTable() {
    const sellButtons = document.querySelectorAll('.btn-sell');
    sellButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            alert("Contacting buyer... Market linkage initiated.");
        });
    });
}
