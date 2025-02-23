// Import state management
import state from './core/state.js';
import { debounce } from './core/utils.js';

class ArchiveStats {
    constructor() {
        this.state = state;
        this.charts = {};
        this.init();
    }

    init() {
        // Initialize state
        this.state.init({
            stats: {
                loading: false,
                error: null,
                data: null
            },
            search: {
                query: '',
                filters: {
                    year: null,
                    categories: [],
                    contentType: null,
                    language: null,
                    startDate: null,
                    endDate: null,
                    isDigitized: null
                },
                results: [],
                totalResults: 0,
                page: 1,
                loading: false
            }
        });

        // Initialize UI components
        this.initializeAdvancedSearch();
        this.initializeCharts();
        this.setupEventListeners();

        // Load initial stats
        this.loadStats();
    }

    async loadStats() {
        try {
            this.state.set('stats.loading', true);
            
            const response = await fetch('/api/archives/summary/');
            if (!response.ok) throw new Error('Failed to load archive statistics');
            
            const data = await response.json();
            this.state.set('stats.data', data);
            this.updateCharts(data);
            
        } catch (error) {
            this.state.set('stats.error', error.message);
            console.error('Error loading stats:', error);
        } finally {
            this.state.set('stats.loading', false);
        }
    }

    initializeCharts() {
        // Category Distribution Chart
        this.charts.category = new Chart(
            document.getElementById('category-chart'),
            {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: [
                            '#3498db',
                            '#2ecc71',
                            '#f1c40f',
                            '#e74c3c',
                            '#9b59b6',
                            '#1abc9c'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            }
        );

        // Content Type Distribution Chart
        this.charts.contentType = new Chart(
            document.getElementById('content-type-chart'),
            {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: '#3498db'
                    }]
                },
                options: {
                    responsive: true,
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
            }
        );
    }

    updateCharts(data) {
        // Update category chart
        const categoryData = data.category_distribution;
        this.charts.category.data.labels = categoryData.map(item => item.categories__name);
        this.charts.category.data.datasets[0].data = categoryData.map(item => item.content_count);
        this.charts.category.update();

        // Update content type chart
        const contentTypeData = data.content_type_distribution;
        this.charts.contentType.data.labels = contentTypeData.map(item => item.content_type);
        this.charts.contentType.data.datasets[0].data = contentTypeData.map(item => item.type_count);
        this.charts.contentType.update();
    }

    initializeAdvancedSearch() {
        const form = document.getElementById('advanced-search-form');
        if (!form) return;

        // Initialize form with state values
        const filters = this.state.get('search.filters');
        Object.entries(filters).forEach(([key, value]) => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = value;
                } else {
                    input.value = value || '';
                }
            }
        });

        // Handle form submission
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.performSearch(new FormData(form));
        });

        // Handle form reset
        form.addEventListener('reset', () => {
            this.state.set('search.filters', {
                year: null,
                categories: [],
                contentType: null,
                language: null,
                startDate: null,
                endDate: null,
                isDigitized: null
            });
        });
    }

    async performSearch(formData) {
        try {
            this.state.set('search.loading', true);
            
            // Build query parameters
            const params = new URLSearchParams();
            for (const [key, value] of formData.entries()) {
                if (value) params.append(key, value);
            }
            
            const response = await fetch(`/api/archives/search/?${params.toString()}`);
            if (!response.ok) throw new Error('Search failed');
            
            const data = await response.json();
            
            this.state.batch(set => {
                set('search.results', data.results);
                set('search.totalResults', data.statistics.total_results);
                set('search.page', 1);
            });
            
            // Update URL with search parameters
            const url = new URL(window.location);
            url.search = params.toString();
            window.history.pushState({}, '', url);
            
        } catch (error) {
            console.error('Search error:', error);
        } finally {
            this.state.set('search.loading', false);
        }
    }

    setupEventListeners() {
        // Handle infinite scroll
        const loadMore = document.querySelector('.load-more-btn');
        if (loadMore) {
            const observer = new IntersectionObserver(
                entries => {
                    if (entries[0].isIntersecting && !this.state.get('search.loading')) {
                        this.loadMoreResults();
                    }
                },
                { threshold: 0.1 }
            );
            observer.observe(loadMore);
        }

        // Handle quick search input
        const quickSearch = document.querySelector('.search-input');
        if (quickSearch) {
            quickSearch.addEventListener('input', debounce(async (e) => {
                const query = e.target.value;
                this.state.set('search.query', query);
                await this.performQuickSearch(query);
            }, 500));
        }
    }

    async loadMoreResults() {
        const currentPage = this.state.get('search.page');
        const params = new URLSearchParams(window.location.search);
        params.set('page', currentPage + 1);

        try {
            this.state.set('search.loading', true);
            
            const response = await fetch(`/api/archives/search/?${params.toString()}`);
            if (!response.ok) throw new Error('Failed to load more results');
            
            const data = await response.json();
            
            this.state.batch(set => {
                set('search.results', [
                    ...this.state.get('search.results'),
                    ...data.results
                ]);
                set('search.page', currentPage + 1);
            });
            
        } catch (error) {
            console.error('Error loading more results:', error);
        } finally {
            this.state.set('search.loading', false);
        }
    }

    async performQuickSearch(query) {
        try {
            this.state.set('search.loading', true);
            
            const response = await fetch(`/api/archives/search/?q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error('Quick search failed');
            
            const data = await response.json();
            
            this.state.batch(set => {
                set('search.results', data.results);
                set('search.totalResults', data.statistics.total_results);
                set('search.page', 1);
            });
            
        } catch (error) {
            console.error('Quick search error:', error);
        } finally {
            this.state.set('search.loading', false);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.archiveStats = new ArchiveStats();
});
