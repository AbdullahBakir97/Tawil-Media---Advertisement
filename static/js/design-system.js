/**
 * Tawil Media - Professional Design System
 * Advanced JavaScript functionality for premium UI components
 */

// Import necessary libraries
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { computePosition, flip, shift, offset, arrow } from '@floating-ui/dom';
import Chart from 'chart.js/auto';

// Register GSAP plugins
gsap.registerPlugin(ScrollTrigger);

/**
 * Initialize the design system
 */
function initDesignSystem() {
  console.log('Initializing Tawil Media Professional Design System');
  
  // Initialize all components
  initAnimations();
  initScrollAnimations();
  initTooltips();
  initDropdowns();
  initModals();
  initTabs();
  initAccordions();
  initToasts();
  initCarousels();
  initFormValidation();
  initCharts();
  init3DEffects();
  initSkeletonLoaders();
  initThemeSwitcher();
}

/**
 * Advanced animations using GSAP
 */
function initAnimations() {
  // Entrance animations for elements with data-animate attribute
  const animatedElements = document.querySelectorAll('[data-animate]');
  
  animatedElements.forEach(element => {
    const animationType = element.getAttribute('data-animate');
    const delay = element.getAttribute('data-delay') || 0;
    
    // Set initial state
    gsap.set(element, { autoAlpha: 0 });
    
    // Create animation based on type
    switch(animationType) {
      case 'fade-in':
        gsap.to(element, { 
          duration: 0.6, 
          autoAlpha: 1, 
          delay: parseFloat(delay),
          ease: 'power2.out'
        });
        break;
      case 'slide-up':
        gsap.fromTo(element, 
          { y: 50, autoAlpha: 0 },
          { 
            duration: 0.6, 
            y: 0, 
            autoAlpha: 1, 
            delay: parseFloat(delay),
            ease: 'power2.out'
          }
        );
        break;
      case 'slide-down':
        gsap.fromTo(element, 
          { y: -50, autoAlpha: 0 },
          { 
            duration: 0.6, 
            y: 0, 
            autoAlpha: 1, 
            delay: parseFloat(delay),
            ease: 'power2.out'
          }
        );
        break;
      case 'slide-left':
        gsap.fromTo(element, 
          { x: 50, autoAlpha: 0 },
          { 
            duration: 0.6, 
            x: 0, 
            autoAlpha: 1, 
            delay: parseFloat(delay),
            ease: 'power2.out'
          }
        );
        break;
      case 'slide-right':
        gsap.fromTo(element, 
          { x: -50, autoAlpha: 0 },
          { 
            duration: 0.6, 
            x: 0, 
            autoAlpha: 1, 
            delay: parseFloat(delay),
            ease: 'power2.out'
          }
        );
        break;
      case 'zoom-in':
        gsap.fromTo(element, 
          { scale: 0.8, autoAlpha: 0 },
          { 
            duration: 0.6, 
            scale: 1, 
            autoAlpha: 1, 
            delay: parseFloat(delay),
            ease: 'power2.out'
          }
        );
        break;
      case 'zoom-out':
        gsap.fromTo(element, 
          { scale: 1.2, autoAlpha: 0 },
          { 
            duration: 0.6, 
            scale: 1, 
            autoAlpha: 1, 
            delay: parseFloat(delay),
            ease: 'power2.out'
          }
        );
        break;
      default:
        gsap.to(element, { 
          duration: 0.6, 
          autoAlpha: 1, 
          delay: parseFloat(delay),
          ease: 'power2.out'
        });
    }
  });
  
  // Parallax scrolling effect
  const parallaxElements = document.querySelectorAll('[data-parallax]');
  
  parallaxElements.forEach(element => {
    const speed = parseFloat(element.getAttribute('data-parallax')) || 0.2;
    
    window.addEventListener('scroll', () => {
      const scrollPosition = window.pageYOffset;
      const parallaxOffset = scrollPosition * speed;
      
      gsap.to(element, {
        y: parallaxOffset,
        duration: 0.3,
        ease: 'power1.out'
      });
    });
  });
}

/**
 * Scroll-triggered animations using GSAP ScrollTrigger
 */
function initScrollAnimations() {
  // Handle animate-on-scroll elements
  const scrollElements = document.querySelectorAll('.animate-on-scroll');
  
  scrollElements.forEach(element => {
    const animationType = element.getAttribute('data-scroll-animation') || 'fade-up';
    const delay = parseFloat(element.getAttribute('data-scroll-delay') || 0);
    const duration = parseFloat(element.getAttribute('data-scroll-duration') || 0.8);
    const offset = parseFloat(element.getAttribute('data-scroll-offset') || 100);
    
    // Set initial state
    gsap.set(element, { autoAlpha: 0 });
    
    // Create scroll-triggered animation
    switch(animationType) {
      case 'fade-up':
        gsap.fromTo(element, 
          { y: 30, autoAlpha: 0 },
          { 
            y: 0, 
            autoAlpha: 1, 
            duration: duration,
            delay: delay,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: element,
              start: `top bottom-=${offset}px`,
              toggleActions: 'play none none reverse'
            }
          }
        );
        break;
      case 'fade-down':
        gsap.fromTo(element, 
          { y: -30, autoAlpha: 0 },
          { 
            y: 0, 
            autoAlpha: 1, 
            duration: duration,
            delay: delay,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: element,
              start: `top bottom-=${offset}px`,
              toggleActions: 'play none none reverse'
            }
          }
        );
        break;
      case 'fade-left':
        gsap.fromTo(element, 
          { x: -50, autoAlpha: 0 },
          { 
            x: 0, 
            autoAlpha: 1, 
            duration: duration,
            delay: delay,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: element,
              start: `top bottom-=${offset}px`,
              toggleActions: 'play none none reverse'
            }
          }
        );
        break;
      case 'fade-right':
        gsap.fromTo(element, 
          { x: 50, autoAlpha: 0 },
          { 
            x: 0, 
            autoAlpha: 1, 
            duration: duration,
            delay: delay,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: element,
              start: `top bottom-=${offset}px`,
              toggleActions: 'play none none reverse'
            }
          }
        );
        break;
      case 'zoom-in':
        gsap.fromTo(element, 
          { scale: 0.8, autoAlpha: 0 },
          { 
            scale: 1, 
            autoAlpha: 1, 
            duration: duration,
            delay: delay,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: element,
              start: `top bottom-=${offset}px`,
              toggleActions: 'play none none reverse'
            }
          }
        );
        break;
      case 'zoom-out':
        gsap.fromTo(element, 
          { scale: 1.2, autoAlpha: 0 },
          { 
            scale: 1, 
            autoAlpha: 1, 
            duration: duration,
            delay: delay,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: element,
              start: `top bottom-=${offset}px`,
              toggleActions: 'play none none reverse'
            }
          }
        );
        break;
      default:
        gsap.fromTo(element, 
          { autoAlpha: 0 },
          { 
            autoAlpha: 1, 
            duration: duration,
            delay: delay,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: element,
              start: `top bottom-=${offset}px`,
              toggleActions: 'play none none reverse'
            }
          }
        );
    }
  });
  
  // Handle staggered animations
  const staggerContainers = document.querySelectorAll('.stagger-container');
  
  staggerContainers.forEach(container => {
    const staggerItems = container.querySelectorAll('.stagger-item');
    const staggerDelay = parseFloat(container.getAttribute('data-stagger-delay') || 0.1);
    const staggerDuration = parseFloat(container.getAttribute('data-stagger-duration') || 0.5);
    const offset = parseFloat(container.getAttribute('data-scroll-offset') || 100);
    
    // Create staggered animation
    gsap.fromTo(staggerItems, 
      { y: 20, autoAlpha: 0 },
      { 
        y: 0, 
        autoAlpha: 1, 
        duration: staggerDuration,
        stagger: staggerDelay,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: container,
          start: `top bottom-=${offset}px`,
          toggleActions: 'play none none reverse'
        }
      }
    );
  });
}

/**
 * Advanced tooltips using Floating UI
 */
function initTooltips() {
  const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
  
  tooltipTriggers.forEach(trigger => {
    const tooltipText = trigger.getAttribute('data-tooltip');
    const tooltipPosition = trigger.getAttribute('data-tooltip-position') || 'top';
    
    // Create tooltip element
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip hidden';
    tooltip.textContent = tooltipText;
    document.body.appendChild(tooltip);
    
    // Show tooltip on hover
    trigger.addEventListener('mouseenter', () => {
      tooltip.classList.remove('hidden');
      
      // Position the tooltip using Floating UI
      computePosition(trigger, tooltip, {
        placement: tooltipPosition,
        middleware: [
          offset(8),
          flip(),
          shift({ padding: 5 })
        ]
      }).then(({ x, y }) => {
        Object.assign(tooltip.style, {
          left: `${x}px`,
          top: `${y}px`
        });
      });
    });
    
    // Hide tooltip on mouse leave
    trigger.addEventListener('mouseleave', () => {
      tooltip.classList.add('hidden');
    });
  });
}

/**
 * Advanced dropdowns
 */
function initDropdowns() {
  const dropdownTriggers = document.querySelectorAll('[data-dropdown-trigger]');
  
  dropdownTriggers.forEach(trigger => {
    const dropdownId = trigger.getAttribute('data-dropdown-trigger');
    const dropdown = document.getElementById(dropdownId);
    
    if (!dropdown) return;
    
    // Toggle dropdown on click
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      const isOpen = !dropdown.classList.contains('hidden');
      
      // Close all other dropdowns
      document.querySelectorAll('[data-dropdown].active').forEach(el => {
        if (el !== dropdown) {
          el.classList.add('hidden');
          el.classList.remove('active');
        }
      });
      
      // Toggle current dropdown
      if (isOpen) {
        dropdown.classList.add('hidden');
        dropdown.classList.remove('active');
        
        // Animation
        gsap.to(dropdown, {
          opacity: 0,
          y: -10,
          duration: 0.2,
          ease: 'power2.in'
        });
      } else {
        dropdown.classList.remove('hidden');
        dropdown.classList.add('active');
        
        // Position the dropdown using Floating UI
        computePosition(trigger, dropdown, {
          placement: 'bottom-start',
          middleware: [
            offset(4),
            flip(),
            shift({ padding: 5 })
          ]
        }).then(({ x, y }) => {
          Object.assign(dropdown.style, {
            left: `${x}px`,
            top: `${y}px`
          });
          
          // Animation
          gsap.fromTo(dropdown, 
            { opacity: 0, y: -10 },
            { opacity: 1, y: 0, duration: 0.3, ease: 'power2.out' }
          );
        });
      }
    });
  });
  
  // Close dropdowns when clicking outside
  document.addEventListener('click', () => {
    document.querySelectorAll('[data-dropdown].active').forEach(dropdown => {
      dropdown.classList.add('hidden');
      dropdown.classList.remove('active');
      
      // Animation
      gsap.to(dropdown, {
        opacity: 0,
        y: -10,
        duration: 0.2,
        ease: 'power2.in'
      });
    });
  });
}

/**
 * Modal dialogs
 */
function initModals() {
  const modalTriggers = document.querySelectorAll('[data-modal-trigger]');
  
  modalTriggers.forEach(trigger => {
    const modalId = trigger.getAttribute('data-modal-trigger');
    const modal = document.getElementById(modalId);
    
    if (!modal) return;
    
    const closeButtons = modal.querySelectorAll('[data-modal-close]');
    
    // Open modal on trigger click
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      
      modal.classList.remove('hidden');
      document.body.classList.add('overflow-hidden');
      
      // Animation
      const backdrop = modal.querySelector('.modal-backdrop');
      const dialog = modal.querySelector('.modal-dialog');
      
      gsap.to(backdrop, {
        opacity: 1,
        duration: 0.3,
        ease: 'power2.out'
      });
      
      gsap.fromTo(dialog,
        { opacity: 0, y: -50 },
        { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out', delay: 0.1 }
      );
    });
    
    // Close modal on close button click
    closeButtons.forEach(button => {
      button.addEventListener('click', () => {
        closeModal(modal);
      });
    });
    
    // Close modal on backdrop click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeModal(modal);
      }
    });
    
    // Close modal on ESC key press
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
        closeModal(modal);
      }
    });
  });
  
  function closeModal(modal) {
    const backdrop = modal.querySelector('.modal-backdrop');
    const dialog = modal.querySelector('.modal-dialog');
    
    gsap.to(backdrop, {
      opacity: 0,
      duration: 0.3,
      ease: 'power2.in'
    });
    
    gsap.to(dialog, {
      opacity: 0,
      y: -50,
      duration: 0.3,
      ease: 'power2.in',
      onComplete: () => {
        modal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
      }
    });
  }
}

/**
 * Tabs functionality
 */
function initTabs() {
  const tabGroups = document.querySelectorAll('[data-tabs]');
  
  tabGroups.forEach(tabGroup => {
    const tabs = tabGroup.querySelectorAll('[data-tab]');
    const tabPanels = document.querySelectorAll(`[data-tab-panel][data-tab-group="${tabGroup.getAttribute('data-tabs')}"]`);
    
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const tabId = tab.getAttribute('data-tab');
        
        // Deactivate all tabs
        tabs.forEach(t => t.classList.remove('active'));
        
        // Activate current tab
        tab.classList.add('active');
        
        // Hide all tab panels
        tabPanels.forEach(panel => {
          panel.classList.add('hidden');
          gsap.set(panel, { opacity: 0, display: 'none' });
        });
        
        // Show current tab panel
        const activePanel = document.querySelector(`[data-tab-panel="${tabId}"]`);
        if (activePanel) {
          activePanel.classList.remove('hidden');
          gsap.fromTo(activePanel,
            { opacity: 0, display: 'block' },
            { opacity: 1, duration: 0.3, ease: 'power2.out' }
          );
        }
      });
    });
    
    // Activate first tab by default
    if (tabs.length > 0) {
      tabs[0].click();
    }
  });
}

/**
 * Accordion functionality
 */
function initAccordions() {
  const accordions = document.querySelectorAll('[data-accordion]');
  
  accordions.forEach(accordion => {
    const items = accordion.querySelectorAll('[data-accordion-item]');
    const allowMultiple = accordion.getAttribute('data-accordion-multiple') === 'true';
    
    items.forEach(item => {
      const header = item.querySelector('[data-accordion-header]');
      const content = item.querySelector('[data-accordion-content]');
      
      if (!header || !content) return;
      
      // Set initial state
      if (!item.classList.contains('active')) {
        gsap.set(content, { height: 0, opacity: 0, display: 'none' });
      }
      
      header.addEventListener('click', () => {
        const isActive = item.classList.contains('active');
        
        // Close other items if not allowing multiple
        if (!allowMultiple && !isActive) {
          items.forEach(otherItem => {
            if (otherItem !== item && otherItem.classList.contains('active')) {
              const otherContent = otherItem.querySelector('[data-accordion-content]');
              
              otherItem.classList.remove('active');
              
              gsap.to(otherContent, {
                height: 0,
                opacity: 0,
                duration: 0.3,
                ease: 'power2.in',
                onComplete: () => {
                  gsap.set(otherContent, { display: 'none' });
                }
              });
            }
          });
        }
        
        // Toggle current item
        if (isActive) {
          item.classList.remove('active');
          
          gsap.to(content, {
            height: 0,
            opacity: 0,
            duration: 0.3,
            ease: 'power2.in',
            onComplete: () => {
              gsap.set(content, { display: 'none' });
            }
          });
        } else {
          item.classList.add('active');
          
          gsap.set(content, { display: 'block', height: 'auto', opacity: 1 });
          gsap.from(content, {
            height: 0,
            opacity: 0,
            duration: 0.3,
            ease: 'power2.out'
          });
        }
      });
    });
  });
}

/**
 * Toast notifications
 */
function initToasts() {
  // Create toast container if it doesn't exist
  let toastContainer = document.querySelector('.toast-container');
  
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container fixed top-4 right-4 z-50 flex flex-col gap-2';
    document.body.appendChild(toastContainer);
  }
  
  // Global function to show toasts
  window.showToast = function(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} flex items-center p-4 rounded-lg shadow-lg`;
    
    // Set background color based on type
    switch(type) {
      case 'success':
        toast.classList.add('bg-success-500', 'text-white');
        break;
      case 'error':
        toast.classList.add('bg-danger-500', 'text-white');
        break;
      case 'warning':
        toast.classList.add('bg-warning-500', 'text-white');
        break;
      default:
        toast.classList.add('bg-info-500', 'text-white');
    }
    
    toast.innerHTML = `
      <div class="mr-3">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
      </div>
      <div class="flex-1">${message}</div>
      <button class="ml-2 text-white">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    `;
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Animate in
    gsap.fromTo(toast,
      { x: 100, opacity: 0 },
      { x: 0, opacity: 1, duration: 0.3, ease: 'power2.out' }
    );
    
    // Close button
    const closeButton = toast.querySelector('button');
    closeButton.addEventListener('click', () => {
      closeToast(toast);
    });
    
    // Auto close after duration
    setTimeout(() => {
      closeToast(toast);
    }, duration);
  };
  
  function closeToast(toast) {
    gsap.to(toast, {
      x: 100,
      opacity: 0,
      duration: 0.3,
      ease: 'power2.in',
      onComplete: () => {
        toast.remove();
      }
    });
  }
}

/**
 * Carousel/slider functionality
 */
function initCarousels() {
  const carousels = document.querySelectorAll('[data-carousel]');
  
  carousels.forEach(carousel => {
    const track = carousel.querySelector('[data-carousel-track]');
    const slides = carousel.querySelectorAll('[data-carousel-slide]');
    const prevButton = carousel.querySelector('[data-carousel-prev]');
    const nextButton = carousel.querySelector('[data-carousel-next]');
    const indicators = carousel.querySelectorAll('[data-carousel-indicator]');
    
    if (!track || slides.length === 0) return;
    
    let currentIndex = 0;
    const slideWidth = slides[0].offsetWidth;
    const autoplay = carousel.getAttribute('data-carousel-autoplay') === 'true';
    const interval = parseInt(carousel.getAttribute('data-carousel-interval') || '5000');
    let autoplayInterval;
    
    // Set initial position
    updateCarousel();
    
    // Previous slide button
    if (prevButton) {
      prevButton.addEventListener('click', () => {
        currentIndex = (currentIndex - 1 + slides.length) % slides.length;
        updateCarousel();
        resetAutoplay();
      });
    }
    
    // Next slide button
    if (nextButton) {
      nextButton.addEventListener('click', () => {
        currentIndex = (currentIndex + 1) % slides.length;
        updateCarousel();
        resetAutoplay();
      });
    }
    
    // Indicators
    indicators.forEach((indicator, index) => {
      indicator.addEventListener('click', () => {
        currentIndex = index;
        updateCarousel();
        resetAutoplay();
      });
    });
    
    // Autoplay
    if (autoplay) {
      startAutoplay();
      
      // Pause on hover
      carousel.addEventListener('mouseenter', () => {
        clearInterval(autoplayInterval);
      });
      
      carousel.addEventListener('mouseleave', () => {
        startAutoplay();
      });
    }
    
    function updateCarousel() {
      // Update track position
      gsap.to(track, {
        x: -currentIndex * slideWidth,
        duration: 0.5,
        ease: 'power2.out'
      });
      
      // Update active indicator
      indicators.forEach((indicator, index) => {
        if (index === currentIndex) {
          indicator.classList.add('active');
        } else {
          indicator.classList.remove('active');
        }
      });
    }
    
    function startAutoplay() {
      autoplayInterval = setInterval(() => {
        currentIndex = (currentIndex + 1) % slides.length;
        updateCarousel();
      }, interval);
    }
    
    function resetAutoplay() {
      if (autoplay) {
        clearInterval(autoplayInterval);
        startAutoplay();
      }
    }
  });
}

/**
 * Form validation
 */
function initFormValidation() {
  const forms = document.querySelectorAll('[data-validate-form]');
  
  forms.forEach(form => {
    const inputs = form.querySelectorAll('[data-validate]');
    
    // Validate on submit
    form.addEventListener('submit', (e) => {
      let isValid = true;
      
      inputs.forEach(input => {
        if (!validateInput(input)) {
          isValid = false;
        }
      });
      
      if (!isValid) {
        e.preventDefault();
      }
    });
    
    // Validate on input change
    inputs.forEach(input => {
      input.addEventListener('blur', () => {
        validateInput(input);
      });
      
      input.addEventListener('input', () => {
        // Remove error when typing
        const errorElement = input.parentNode.querySelector('.error-message');
        if (errorElement) {
          errorElement.remove();
        }
        
        input.classList.remove('error');
      });
    });
  });
  
  function validateInput(input) {
    const value = input.value.trim();
    const validationType = input.getAttribute('data-validate');
    const errorMessage = input.getAttribute('data-error-message') || 'This field is invalid';
    let isValid = true;
    
    // Remove existing error
    const existingError = input.parentNode.querySelector('.error-message');
    if (existingError) {
      existingError.remove();
    }
    
    input.classList.remove('error');
    
    // Validate based on type
    switch(validationType) {
      case 'required':
        isValid = value !== '';
        break;
      case 'email':
        isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
        break;
      case 'number':
        isValid = !isNaN(value) && value !== '';
        break;
      case 'phone':
        isValid = /^[\d\s\+\-\(\)]{7,20}$/.test(value);
        break;
      case 'url':
        isValid = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/.test(value);
        break;
      case 'password':
        isValid = value.length >= 8;
        break;
    }
    
    // Show error if invalid
    if (!isValid) {
      input.classList.add('error');
      
      const errorElement = document.createElement('div');
      errorElement.className = 'error-message text-danger-500 text-sm mt-1';
      errorElement.textContent = errorMessage;
      
      input.parentNode.appendChild(errorElement);
      
      // Animate error
      gsap.fromTo(errorElement,
        { opacity: 0, y: -10 },
        { opacity: 1, y: 0, duration: 0.3, ease: 'power2.out' }
      );
    }
    
    return isValid;
  }
}

/**
 * Initialize charts and data visualizations
 */
function initCharts() {
  // Line Chart
  const lineChartEl = document.getElementById('lineChart');
  if (lineChartEl) {
    const lineChart = new Chart(lineChartEl, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Revenue',
          data: [12, 19, 3, 5, 2, 3],
          borderColor: '#4f46e5',
          backgroundColor: 'rgba(79, 70, 229, 0.1)',
          tension: 0.4,
          fill: true
        }, {
          label: 'Expenses',
          data: [5, 12, 7, 8, 12, 10],
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          tooltip: {
            mode: 'index',
            intersect: false,
          }
        },
        interaction: {
          mode: 'nearest',
          intersect: false,
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }

  // Bar Chart
  const barChartEl = document.getElementById('barChart');
  if (barChartEl) {
    const barChart = new Chart(barChartEl, {
      type: 'bar',
      data: {
        labels: ['Q1', 'Q2', 'Q3', 'Q4'],
        datasets: [{
          label: 'Sales',
          data: [65, 59, 80, 81],
          backgroundColor: [
            'rgba(79, 70, 229, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(239, 68, 68, 0.8)'
          ],
          borderColor: [
            'rgba(79, 70, 229, 1)',
            'rgba(16, 185, 129, 1)',
            'rgba(245, 158, 11, 1)',
            'rgba(239, 68, 68, 1)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }

  // Pie Chart
  const pieChartEl = document.getElementById('pieChart');
  if (pieChartEl) {
    const pieChart = new Chart(pieChartEl, {
      type: 'pie',
      data: {
        labels: ['Product A', 'Product B', 'Product C', 'Product D'],
        datasets: [{
          data: [12, 19, 3, 5],
          backgroundColor: [
            'rgba(79, 70, 229, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(239, 68, 68, 0.8)'
          ],
          borderColor: [
            'rgba(79, 70, 229, 1)',
            'rgba(16, 185, 129, 1)',
            'rgba(245, 158, 11, 1)',
            'rgba(239, 68, 68, 1)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'right',
          }
        }
      }
    });
  }

  // Doughnut Chart
  const doughnutChartEl = document.getElementById('doughnutChart');
  if (doughnutChartEl) {
    const doughnutChart = new Chart(doughnutChartEl, {
      type: 'doughnut',
      data: {
        labels: ['Marketing', 'Sales', 'Operations', 'IT'],
        datasets: [{
          data: [25, 35, 20, 20],
          backgroundColor: [
            'rgba(79, 70, 229, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(239, 68, 68, 0.8)'
          ],
          borderColor: [
            'rgba(79, 70, 229, 1)',
            'rgba(16, 185, 129, 1)',
            'rgba(245, 158, 11, 1)',
            'rgba(239, 68, 68, 1)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
          }
        },
        cutout: '70%'
      }
    });
  }
}

/**
 * Initialize 3D card effects
 */
function init3DEffects() {
  const cards3D = document.querySelectorAll('.card-3d');
  
  cards3D.forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      
      const rotateX = (y - centerY) / 10;
      const rotateY = (centerX - x) / 10;
      
      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    });
    
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
    });
  });
}

/**
 * Initialize skeleton loaders
 */
function initSkeletonLoaders() {
  const skeletons = document.querySelectorAll('.skeleton-loader');
  
  // Replace skeletons with actual content when loaded
  window.addEventListener('load', () => {
    skeletons.forEach(skeleton => {
      const contentId = skeleton.getAttribute('data-content-id');
      if (contentId) {
        const content = document.getElementById(contentId);
        if (content) {
          // Fade out skeleton
          gsap.to(skeleton, {
            opacity: 0,
            duration: 0.3,
            onComplete: () => {
              skeleton.style.display = 'none';
              // Fade in content
              gsap.fromTo(content, 
                { opacity: 0 },
                { 
                  opacity: 1, 
                  duration: 0.5,
                  onStart: () => {
                    content.style.display = '';
                  }
                }
              );
            }
          });
        }
      }
    });
  });
}

/**
 * Theme switcher functionality
 */
function initThemeSwitcher() {
  const themeToggles = document.querySelectorAll('[data-theme-toggle]');
  
  // Check for saved theme preference or respect OS preference
  const savedTheme = localStorage.getItem('theme');
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  // Apply theme based on saved preference or system preference
  if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
  
  // Toggle theme when clicking theme toggle buttons
  themeToggles.forEach(toggle => {
    toggle.addEventListener('click', () => {
      if (document.documentElement.classList.contains('dark')) {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('theme', 'light');
      } else {
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
      }
      
      // Animate theme change
      gsap.fromTo('body', 
        { opacity: 0.8 },
        { opacity: 1, duration: 0.3, ease: 'power1.out' }
      );
    });
  });
  
  // Listen for OS theme preference changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    if (!localStorage.getItem('theme')) {
      if (e.matches) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  });
}

// Initialize design system on DOM content loaded
document.addEventListener('DOMContentLoaded', initDesignSystem);

// Export functions for external use
export {
  initDesignSystem,
  initAnimations,
  initScrollAnimations,
  initTooltips,
  initDropdowns,
  initModals,
  initTabs,
  initAccordions,
  initToasts,
  initCarousels,
  initFormValidation,
  initCharts,
  init3DEffects,
  initSkeletonLoaders,
  initThemeSwitcher
};
