import type { SearchPlan } from './searchAgentApi';
import '../../App.css';

type SearchPlanPanelProps = {
  searchPlan: SearchPlan;
};

function formatPreferTerm(term: string): string {
  switch (term.toLowerCase()) {
    case 'historical':
    case 'old':
      return 'historical recordings';
    case 'recent':
    case 'modern':
      return 'recent recordings';
    case 'live':
      return 'live recordings';
    case 'studio':
      return 'studio recordings';
    default:
      return term;
  }
}

function formatPreferTerms(terms: string[]): string[] {
  return [...new Set(terms.map(formatPreferTerm))];
}

export function SearchPlanPanel({ searchPlan }: SearchPlanPanelProps) {
  const preferredLabels = formatPreferTerms(searchPlan.preferTerms);

  return (
    <section className="search-plan-panel">
      <h3>Search Plan</h3>

      <div className="search-plan-section">
        <p className="search-plan-label">Selected work:</p>
        <p>{searchPlan.comparisonTarget}</p>
      </div>

      {preferredLabels.length > 0 && (
        <div className="search-plan-section">
          <p className="search-plan-label">Preferred:</p>
          <ul className="search-plan-list">
            {preferredLabels.map((term) => (
              <li key={term}>{term}</li>
            ))}
          </ul>
        </div>
      )}

      {searchPlan.excludeTerms.length > 0 && (
        <div className="search-plan-section">
          <p className="search-plan-label">Excluded:</p>
          <ul className="search-plan-list">
            {searchPlan.excludeTerms.map((term) => (
              <li key={term}>{term}</li>
            ))}
          </ul>
        </div>
      )}

      {searchPlan.searchQueries.length > 0 && (
        <div className="search-plan-section">
          <p className="search-plan-label">Queries:</p>
          <ul className="search-plan-list">
            {searchPlan.searchQueries.map((query) => (
              <li key={query}>{query}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
