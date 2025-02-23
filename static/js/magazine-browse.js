document.addEventListener('DOMContentLoaded', function() {
    const magazineBrowse = {
        init() {
            this.setupViewToggle();
            this.setupFiltersSidebar();
            this.setupModal();
            this.setupInfiniteScroll();
            this.setupSearch();
        },

        setupViewToggle() {
            const gridBtn = document.querySelector('.grid-view');
            const listBtn = document.querySelector('.list-view');
            const magazineGrid = document.querySelector('.magazine-grid');

            gridBtn?.addEventListener('click', () => {
                magazineGrid.classList.remove('list-layout');
                gridBtn.classList.add('active');
                listBtn.classList.remove('active');
                localStorage.setItem('magazineView', 'grid');
            });

            listBtn?.addEventListener('click', () => {
                magazineGrid.classList.add('list-layout');
                listBtn.classList.add('active');
                gridBtn.classList.remove('active');
                localStorage.setItem('magazineView', 'list');
            });

            // Restore previous view preference
            const savedView = localStorage.getItem('magazineView');
            if (savedView === 'list') {
                listBtn?.click();
            }
        },

        setupFiltersSidebar() {
            const sidebar = document.querySelector('.filters-sidebar');
            const mobileToggle = document.createElement('button');
            mobileToggle.className = 'filters-toggle';
            mobileToggle.innerHTML = `
                <svg width="24" height="24" viewBox="0 0 24 24">
                    <path d="M3 6H21M3 12H21M3 18H21" stroke="currentColor" stroke-width="2"/>
                </svg>
            `;

            document.querySelector('.grid-header')?.prepend(mobileToggle);

            mobileToggle.addEventListener('click', () => {
                sidebar?.classList.toggle('active');
            });

            // Close sidebar when clicking outside
            document.addEventListener('click', (e) => {
                if (sidebar?.classList.contains('active') && 
                    !sidebar.contains(e.target) && 
                    !mobileToggle.contains(e.target)) {
                    sidebar.classList.remove('active');
                }
            });
        },

        setupModal() {
            const modal = document.querySelector('#preview-modal');

            // Close modal on background click
            modal?.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });

            // Close modal on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.closeModal();
                }
            });

            // Handle modal content loading
            htmx.on('htmx:afterSwap', (e) => {
                if (e.detail.target.id === 'preview-modal') {
                    this.openModal();
                }
            });
        },

        openModal() {
            const modal = document.querySelector('#preview-modal');
            document.body.style.overflow = 'hidden';
            modal?.classList.add('active');

            // Initialize magazine viewer if present
            const viewer = modal?.querySelector('.magazine-preview');
            if (viewer) {
                new MagazineViewer({
                    container: '.magazine-preview',
                    pages: JSON.parse(viewer.dataset.pages || '[]')
                });
            }
        },

        closeModal() {
            const modal = document.querySelector('#preview-modal');
            document.body.style.overflow = '';
            modal?.classList.remove('active');
        },

        setupInfiniteScroll() {
            const loadMoreBtn = document.querySelector('.load-more-btn');
            const options = {
                root: null,
                rootMargin: '100px',
                threshold: 0.1
            };

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && !loadMoreBtn?.hasAttribute('data-loading')) {
                        loadMoreBtn?.click();
                    }
                });
            }, options);

            if (loadMoreBtn) {
                observer.observe(loadMoreBtn);
            }

            // Handle loading state
            htmx.on('htmx:beforeRequest', (e) => {
                if (e.detail.elt === loadMoreBtn) {
                    loadMoreBtn.setAttribute('data-loading', '');
                    loadMoreBtn.innerHTML = `
                        <span class="loading-spinner"></span>
                        Loading...
                    `;
                }
            });

            htmx.on('htmx:afterRequest', (e) => {
                if (e.detail.elt === loadMoreBtn) {
                    loadMoreBtn.removeAttribute('data-loading');
                    loadMoreBtn.innerHTML = 'Load More';
                }
            });
        },

        setupSearch() {
            const searchInput = document.querySelector('.search-input');
            let searchTimeout;

            searchInput?.addEventListener('input', () => {
                const spinner = document.querySelector('.search-icon');
                spinner.innerHTML = `
                    <svg class="animate-spin" width="24" height="24" viewBox="0 0 24 24">
                        <path d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10" 
                              stroke="currentColor" fill="none" stroke-width="2"/>
                    </svg>
                `;

                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    spinner.innerHTML = `
                        <svg width="24" height="24" viewBox="0 0 24 24">
                            <path d="M21 21L16.5 16.5M19 11C19 15.4183 15.4183 19 11 19C6.58172 19 3 15.4183 3 11C3 6.58172 6.58172 3 11 3C15.4183 3 19 6.58172 19 11Z" 
                                  stroke="currentColor" fill="none" stroke-width="2"/>
                        </svg>
                    `;
                }, 500);
            });
        }
    };

    magazineBrowse.init();
});
