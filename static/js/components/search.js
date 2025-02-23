import Utils from '../core/utils.js';
import state from '../core/state.js';

class SearchComponent {
    constructor(options = {}) {
        this.options = {
            searchInputSelector: '[data-search-input]',
            resultsContainerSelector: '[data-search-results]',
            suggestionsContainerSelector: '[data-search-suggestions]',
            loadingIndicatorSelector: '[data-search-loading]',
            minChars: 2,
            debounceTime: 300,
            maxSuggestions: 5,
            highlightMatches: true,
            ...options
        };

        this.state = {
            query: '',
            results: [],
            suggestions: [],
            loading: false,
            error: null
        };

        this.init();
    }

    init() {
        // Initialize search state
        state.set('search', this.state);

        // Cache DOM elements
        this.searchInput = document.querySelector(this.options.searchInputSelector);
        this.resultsContainer = document.querySelector(this.options.resultsContainerSelector);
        this.suggestionsContainer = document.querySelector(this.options.suggestionsContainerSelector);
        this.loadingIndicator = document.querySelector(this.options.loadingIndicatorSelector);

        if (!this.searchInput) {
            console.error('Search input element not found');
            return;
        }

        // Bind event listeners
        this.bindEvents();

        // Subscribe to state changes
        state.subscribe('search', this.handleStateChange.bind(this));
    }

    bindEvents() {
        // Handle input changes with debounce
        this.searchInput.addEventListener('input', Utils.events.debounce(
            this.handleInput.bind(this),
            this.options.debounceTime
        ));

        // Handle form submission
        this.searchInput.closest('form')?.addEventListener('submit', 
            this.handleSubmit.bind(this)
        );

        // Handle suggestion selection
        this.suggestionsContainer?.addEventListener('click', 
            this.handleSuggestionClick.bind(this)
        );

        // Handle keyboard navigation
        this.searchInput.addEventListener('keydown', 
            this.handleKeyboardNavigation.bind(this)
        );

        // Close suggestions on outside click
        document.addEventListener('click', (e) => {
            if (!e.target.closest(this.options.suggestionsContainerSelector)) {
                this.closeSuggestions();
            }
        });
    }

    async handleInput(event) {
        const query = event.target.value.trim();

        if (query.length < this.options.minChars) {
            this.updateState({ suggestions: [], loading: false });
            return;
        }

        this.updateState({ query, loading: true });

        try {
            const suggestions = await this.fetchSuggestions(query);
            this.updateState({ 
                suggestions: suggestions.slice(0, this.options.maxSuggestions),
                loading: false 
            });
        } catch (error) {
            this.updateState({ 
                error: 'Failed to fetch suggestions',
                loading: false 
            });
        }
    }

    async handleSubmit(event) {
        event.preventDefault();
        const query = this.searchInput.value.trim();

        if (!query) return;

        this.updateState({ loading: true });

        try {
            const results = await this.fetchResults(query);
            this.updateState({ 
                results,
                loading: false,
                suggestions: [] 
            });
        } catch (error) {
            this.updateState({ 
                error: 'Search failed',
                loading: false 
            });
        }
    }

    handleSuggestionClick(event) {
        const suggestion = event.target.closest('[data-suggestion]');
        if (!suggestion) return;

        const value = suggestion.dataset.suggestion;
        this.searchInput.value = value;
        this.closeSuggestions();
        this.searchInput.closest('form')?.requestSubmit();
    }

    handleKeyboardNavigation(event) {
        const suggestions = this.suggestionsContainer?.querySelectorAll('[data-suggestion]');
        if (!suggestions?.length) return;

        const currentIndex = Array.from(suggestions).findIndex(
            el => el.classList.contains('active')
        );

        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                this.navigateSuggestions(currentIndex, 1, suggestions);
                break;

            case 'ArrowUp':
                event.preventDefault();
                this.navigateSuggestions(currentIndex, -1, suggestions);
                break;

            case 'Enter':
                const activeSuggestion = this.suggestionsContainer.querySelector('[data-suggestion].active');
                if (activeSuggestion) {
                    event.preventDefault();
                    this.searchInput.value = activeSuggestion.dataset.suggestion;
                    this.closeSuggestions();
                    this.searchInput.closest('form')?.requestSubmit();
                }
                break;

            case 'Escape':
                this.closeSuggestions();
                break;
        }
    }

    navigateSuggestions(currentIndex, direction, suggestions) {
        let newIndex = currentIndex + direction;
        
        if (newIndex < 0) {
            newIndex = suggestions.length - 1;
        } else if (newIndex >= suggestions.length) {
            newIndex = 0;
        }

        suggestions.forEach((el, i) => {
            el.classList.toggle('active', i === newIndex);
        });

        const activeSuggestion = suggestions[newIndex];
        if (activeSuggestion) {
            this.searchInput.value = activeSuggestion.dataset.suggestion;
            activeSuggestion.scrollIntoView({ block: 'nearest' });
        }
    }

    async fetchSuggestions(query) {
        // Replace with your API endpoint
        const response = await fetch(`/api/search/suggestions?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Failed to fetch suggestions');
        return response.json();
    }

    async fetchResults(query) {
        // Replace with your API endpoint
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Failed to fetch results');
        return response.json();
    }

    updateState(newState) {
        state.set('search', {
            ...state.get('search'),
            ...newState
        });
    }

    handleStateChange(searchState) {
        // Update loading state
        this.loadingIndicator?.classList.toggle('hidden', !searchState.loading);

        // Update suggestions
        if (this.suggestionsContainer) {
            this.suggestionsContainer.innerHTML = searchState.suggestions
                .map(suggestion => this.renderSuggestion(suggestion))
                .join('');
            
            this.suggestionsContainer.classList.toggle('hidden', 
                !searchState.suggestions.length
            );
        }

        // Update results
        if (this.resultsContainer) {
            this.resultsContainer.innerHTML = searchState.results
                .map(result => this.renderResult(result))
                .join('');
        }

        // Handle errors
        if (searchState.error) {
            this.showError(searchState.error);
        }
    }

    renderSuggestion(suggestion) {
        let text = suggestion.text;
        
        if (this.options.highlightMatches && this.state.query) {
            text = this.highlightMatches(text, this.state.query);
        }

        return `
            <div class="suggestion-item" data-suggestion="${suggestion.text}">
                <span class="suggestion-text">${text}</span>
                ${suggestion.category ? `
                    <span class="suggestion-category">${suggestion.category}</span>
                ` : ''}
            </div>
        `;
    }

    renderResult(result) {
        return `
            <article class="search-result">
                <h3 class="result-title">
                    <a href="${result.url}">${result.title}</a>
                </h3>
                <p class="result-excerpt">${result.excerpt}</p>
                ${result.metadata ? `
                    <div class="result-metadata">
                        <span class="result-date">${Utils.date.relative(result.metadata.date)}</span>
                        <span class="result-category">${result.metadata.category}</span>
                    </div>
                ` : ''}
            </article>
        `;
    }

    highlightMatches(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    showError(message) {
        const errorElement = Utils.dom.create('div', {
            class: 'search-error',
            role: 'alert'
        }, [message]);

        this.resultsContainer?.appendChild(errorElement);
        
        setTimeout(() => {
            errorElement.remove();
        }, 5000);
    }

    closeSuggestions() {
        this.updateState({ suggestions: [] });
    }
}

export default SearchComponent;

// Example usage:
/*
import SearchComponent from './components/search.js';

document.addEventListener('DOMContentLoaded', () => {
    const search = new SearchComponent({
        searchInputSelector: '#search-input',
        resultsContainerSelector: '#search-results',
        suggestionsContainerSelector: '#search-suggestions',
        loadingIndicatorSelector: '#search-loading',
        minChars: 2,
        debounceTime: 300,
        maxSuggestions: 5,
        highlightMatches: true
    });
});
*/
