document.addEventListener('DOMContentLoaded', function() {
    // Only apply effects on non-touch devices
    if (!('ontouchstart' in window)) {
        const navLinks = document.querySelectorAll('[data-nav-text]');

        // Initialize links by wrapping each character
        navLinks.forEach(link => {
            const textElement = link.querySelector('span') || link;
            const text = textElement.textContent.trim();
            const wrappedText = text.split('').map(char => 
                `<span class="char-container"><span class="char">${char === ' ' ? '&nbsp;' : char}</span></span>`
            ).join('');
            textElement.innerHTML = wrappedText;

            // Preserve any existing elements after the text
            const otherElements = link.querySelector('svg');
            if (otherElements) {
                textElement.insertAdjacentElement('afterend', otherElements);
            }
        });

        // Add mouse movement handlers
        navLinks.forEach(link => {
            const chars = link.querySelectorAll('.char');
            
            link.addEventListener('mousemove', (e) => {
                const linkRect = link.getBoundingClientRect();
                const mouseX = e.clientX - linkRect.left;
                
                chars.forEach((char) => {
                    const charRect = char.getBoundingClientRect();
                    const charCenter = charRect.left + (charRect.width / 2) - linkRect.left;
                    const distance = Math.abs(mouseX - charCenter);
                    const maxDistance = linkRect.width / 2;
                    
                    // Calculate brightness based on distance from mouse
                    const brightness = Math.max(95 - (distance / maxDistance) * 60, 35);
                    const glow = Math.max(0, 10 - (distance / 30));
                    
                    // Apply the styles with a slight delay for smooth animation
                    requestAnimationFrame(() => {
                        char.style.color = `rgba(255, 255, 255, ${brightness / 100})`;
                        char.style.textShadow = glow > 0 ? 
                            `0 0 ${glow}px rgba(255, 255, 255, ${glow / 10})` : 'none';
                        char.style.transform = `translateY(${-glow / 4}px)`;
                    });
                });
            });

            // Reset styles on mouse leave with smooth transition
            link.addEventListener('mouseleave', () => {
                chars.forEach(char => {
                    char.style.transition = 'all 0.3s ease';
                    char.style.color = '';
                    char.style.textShadow = '';
                    char.style.transform = '';
                    
                    // Remove transition after it completes
                    setTimeout(() => {
                        char.style.transition = '';
                    }, 300);
                });
            });
        });
    }
});
