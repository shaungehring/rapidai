/**
 * Extra JavaScript for RapidAI documentation
 */

// Add any custom JavaScript functionality here
// This file is loaded on all documentation pages

document.addEventListener('DOMContentLoaded', function() {
    // Add copy button functionality for code blocks (if not already handled by material theme)

    // Add external link icons
    const links = document.querySelectorAll('a[href^="http"]');
    links.forEach(link => {
        if (!link.hostname.includes(window.location.hostname)) {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
        }
    });

    // Console welcome message
    console.log('%cRapidAI Documentation', 'font-size: 20px; font-weight: bold; color: #00ffff;');
    console.log('%cLearn more at https://shaungehring.github.io/rapidai/', 'font-size: 12px; color: #999;');
});
