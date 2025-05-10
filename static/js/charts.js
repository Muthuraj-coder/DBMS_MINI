/**
 * Student Information System Charts
 * This file contains functions for data visualization using Chart.js
 */

// Initialize charts when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Look for chart containers in the page
    if (document.getElementById('attendanceChart')) {
        initializeAttendanceChart();
    }
    
    if (document.getElementById('gradesChart')) {
        initializeGradesChart();
    }
    
    if (document.getElementById('enrollmentChart')) {
        initializeEnrollmentChart();
    }
    
    if (document.getElementById('attendanceComparisonChart')) {
        initializeAttendanceComparisonChart();
    }
});

/**
 * Initialize the attendance chart for a specific student
 */
function initializeAttendanceChart() {
    const chartContainer = document.getElementById('attendanceChart');
    const studentId = chartContainer.getAttribute('data-student-id');
    
    // Fetch attendance data from the API
    fetch(`/api/attendance_data/${studentId}`)
        .then(response => response.json())
        .then(data => {
            // Prepare data for the chart
            const labels = data.map(item => item.course);
            const presentData = data.map(item => item.present);
            const absentData = data.map(item => item.absent);
            const excusedData = data.map(item => item.excused);
            const percentages = data.map(item => item.percentage);
            
            // Create the attendance chart
            const ctx = chartContainer.getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Present',
                            data: presentData,
                            backgroundColor: 'rgba(40, 167, 69, 0.7)',
                            borderColor: 'rgba(40, 167, 69, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Absent',
                            data: absentData,
                            backgroundColor: 'rgba(220, 53, 69, 0.7)',
                            borderColor: 'rgba(220, 53, 69, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Excused',
                            data: excusedData,
                            backgroundColor: 'rgba(255, 193, 7, 0.7)',
                            borderColor: 'rgba(255, 193, 7, 1)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            stacked: true,
                            title: {
                                display: true,
                                text: 'Courses'
                            }
                        },
                        y: {
                            stacked: true,
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Number of Classes'
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                afterLabel: function(context) {
                                    return `Attendance Rate: ${percentages[context.dataIndex].toFixed(1)}%`;
                                }
                            }
                        },
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Attendance Summary'
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching attendance data:', error);
            chartContainer.innerHTML = '<div class="alert alert-danger">Failed to load attendance data</div>';
        });
}

/**
 * Initialize the grades chart for a specific student
 */
function initializeGradesChart() {
    const chartContainer = document.getElementById('gradesChart');
    const studentId = chartContainer.getAttribute('data-student-id');
    
    // Fetch grade data from the API
    fetch(`/api/grade_data/${studentId}`)
        .then(response => response.json())
        .then(data => {
            // Prepare data for the chart
            const labels = data.map(item => item.course);
            const studentGrades = data.map(item => item.overall_grade);
            const classAvgGrades = data.map(item => item.avg_class_grade);
            
            // Create the grades chart
            const ctx = chartContainer.getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Your Grade',
                            data: studentGrades,
                            backgroundColor: 'rgba(0, 123, 255, 0.7)',
                            borderColor: 'rgba(0, 123, 255, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Class Average',
                            data: classAvgGrades,
                            backgroundColor: 'rgba(108, 117, 125, 0.7)',
                            borderColor: 'rgba(108, 117, 125, 1)',
                            borderWidth: 1,
                            type: 'line'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Grade (%)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Courses'
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.dataset.label}: ${context.raw.toFixed(1)}%`;
                                }
                            }
                        },
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Grade Summary'
                        }
                    }
                }
            });
            
            // For each course, create a detailed grade chart
            data.forEach((course, index) => {
                if (course.grades.length === 0) return;
                
                const detailContainer = document.createElement('div');
                detailContainer.className = 'mt-4';
                detailContainer.innerHTML = `
                    <h5>${course.course} Grades</h5>
                    <canvas id="gradeDetail-${index}"></canvas>
                `;
                chartContainer.parentNode.appendChild(detailContainer);
                
                const detailCtx = document.getElementById(`gradeDetail-${index}`).getContext('2d');
                
                // Prepare detailed grade data
                const assignmentNames = course.grades.map(g => g.name);
                const scores = course.grades.map(g => g.percentage);
                
                new Chart(detailCtx, {
                    type: 'bar',
                    data: {
                        labels: assignmentNames,
                        datasets: [{
                            label: 'Score (%)',
                            data: scores,
                            backgroundColor: 'rgba(23, 162, 184, 0.7)',
                            borderColor: 'rgba(23, 162, 184, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100,
                                title: {
                                    display: true,
                                    text: 'Score (%)'
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            },
                            title: {
                                display: false
                            }
                        }
                    }
                });
            });
        })
        .catch(error => {
            console.error('Error fetching grade data:', error);
            chartContainer.innerHTML = '<div class="alert alert-danger">Failed to load grade data</div>';
        });
}

/**
 * Initialize the enrollment chart for admin dashboard
 */
function initializeEnrollmentChart() {
    const chartContainer = document.getElementById('enrollmentChart');
    
    // Fetch enrollment data from the API
    fetch('/api/course_enrollment_stats')
        .then(response => response.json())
        .then(data => {
            // Prepare data for the chart
            const labels = data.map(item => item.course);
            const counts = data.map(item => item.count);
            
            // Create the enrollment chart
            const ctx = chartContainer.getContext('2d');
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: counts,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.7)',
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(255, 206, 86, 0.7)',
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(153, 102, 255, 0.7)',
                            'rgba(255, 159, 64, 0.7)',
                            'rgba(199, 199, 199, 0.7)',
                            'rgba(83, 102, 255, 0.7)',
                            'rgba(40, 159, 64, 0.7)',
                            'rgba(210, 199, 199, 0.7)',
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)',
                            'rgba(199, 199, 199, 1)',
                            'rgba(83, 102, 255, 1)',
                            'rgba(40, 159, 64, 1)',
                            'rgba(210, 199, 199, 1)',
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'right',
                        },
                        title: {
                            display: true,
                            text: 'Course Enrollment Distribution'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.formattedValue;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = Math.round((context.raw / total) * 100);
                                    return `${label}: ${value} students (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching enrollment data:', error);
            chartContainer.innerHTML = '<div class="alert alert-danger">Failed to load enrollment data</div>';
        });
}

/**
 * Initialize the attendance comparison chart for admin dashboard
 */
function initializeAttendanceComparisonChart() {
    const chartContainer = document.getElementById('attendanceComparisonChart');
    
    // Fetch attendance data from the API
    fetch('/api/course_attendance_stats')
        .then(response => response.json())
        .then(data => {
            // Prepare data for the chart
            const labels = data.map(item => item.course);
            const percentages = data.map(item => item.percentage);
            
            // Create the attendance comparison chart
            const ctx = chartContainer.getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Attendance Rate (%)',
                        data: percentages,
                        backgroundColor: 'rgba(40, 167, 69, 0.7)',
                        borderColor: 'rgba(40, 167, 69, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Attendance Rate (%)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Courses'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Course Attendance Comparison'
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching attendance data:', error);
            chartContainer.innerHTML = '<div class="alert alert-danger">Failed to load attendance data</div>';
        });
}
