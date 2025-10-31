// Navigation scroll effect
const navbar = document.getElementById('navbar');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
    
    lastScroll = currentScroll;
});

// Mobile menu toggle
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const navLinks = document.querySelector('.nav-links');

if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        mobileMenuToggle.classList.toggle('active');
    });
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offset = 80;
            const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Getting Started tabs
const startTabs = document.querySelectorAll('.start-tab');
const startPanels = document.querySelectorAll('.start-panel');

startTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const targetTab = tab.getAttribute('data-tab');
        
        // Remove active class from all tabs and panels
        startTabs.forEach(t => t.classList.remove('active'));
        startPanels.forEach(p => p.classList.remove('active'));
        
        // Add active class to clicked tab and corresponding panel
        tab.classList.add('active');
        const panel = document.getElementById(`${targetTab}-panel`);
        if (panel) {
            panel.classList.add('active');
        }
    });
});

// Copy to clipboard functionality
const copyButtons = document.querySelectorAll('.copy-btn');

copyButtons.forEach(button => {
    button.addEventListener('click', async () => {
        const codeId = button.getAttribute('data-copy');
        const codeElement = document.getElementById(codeId);
        
        if (codeElement) {
            const code = codeElement.textContent;
            
            try {
                await navigator.clipboard.writeText(code);
                button.textContent = 'Copied!';
                button.style.background = '#10B981';
                
                setTimeout(() => {
                    button.textContent = 'Copy';
                    button.style.background = '';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        }
    });
});

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all sections
document.querySelectorAll('section').forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(20px)';
    section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(section);
});

// Code syntax highlighting helper
function highlightCode() {
    const codeBlocks = document.querySelectorAll('.code-block pre code, .demo-code pre code');
    
    codeBlocks.forEach(block => {
        // Simple keyword highlighting
        let html = block.innerHTML;
        
        // Highlight keywords
        html = html.replace(/(\w+):/g, '<span class="code-key">$1</span>:');
        html = html.replace(/"([^"]+)"/g, '<span class="code-string">"$1"</span>');
        html = html.replace(/(\d+)/g, '<span class="code-number">$1</span>');
        html = html.replace(/(true|false)/g, '<span class="code-boolean">$1</span>');
        html = html.replace(/\/\/(.*)/g, '<span class="code-comment">//$1</span>');
        
        block.innerHTML = html;
    });
}

// Run highlighting on load
document.addEventListener('DOMContentLoaded', highlightCode);

// Stats counter animation
const statNumbers = document.querySelectorAll('.stat-number');
const animateCounter = (element) => {
    const target = element.textContent;
    if (target.includes('%')) {
        const targetValue = parseInt(target);
        let current = 0;
        const increment = targetValue / 50;
        const timer = setInterval(() => {
            current += increment;
            if (current >= targetValue) {
                element.textContent = targetValue + '%';
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current) + '%';
            }
        }, 20);
    }
};

const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateCounter(entry.target);
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

statNumbers.forEach(stat => {
    statsObserver.observe(stat);
});

// Parallax effect for hero
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroBackground = document.querySelector('.hero-background');
    if (heroBackground) {
        heroBackground.style.transform = `translateY(${scrolled * 0.5}px)`;
    }
});

// Add active state to current nav item based on scroll position
const sections = document.querySelectorAll('section[id]');
const navLinksItems = document.querySelectorAll('.nav-links a[href^="#"]');

window.addEventListener('scroll', () => {
    let current = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (window.pageYOffset >= sectionTop - 100) {
            current = section.getAttribute('id');
        }
    });
    
    navLinksItems.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
});

