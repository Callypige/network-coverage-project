import { Component, signal, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { CoverageService } from './services/coverage';
import { debounceTime, Subject } from 'rxjs';

export interface OperatorCoverage {
  '2G': boolean;
  '3G': boolean;
  '4G': boolean;
}

export interface AddressCoverage {
  orange: OperatorCoverage;
  SFR: OperatorCoverage;
  bouygues: OperatorCoverage;
  Free: OperatorCoverage;
}

export interface CoverageResults {
  [addressId: string]: AddressCoverage;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  private http = inject(HttpClient);
  private coverageService = inject(CoverageService);

  address = signal('');
  selectedAddress = signal<any>(null); // Store the complete selected address object
  results = signal<CoverageResults | null>(null);
  loading = signal(false);

  // Autocomplete
  suggestions = signal<any[]>([]);
  showSuggestions = signal(false);
  searchSubject = new Subject<string>();

  constructor() {
    // Debounce search to avoid too many API calls
    this.searchSubject.pipe(
      debounceTime(300)
    ).subscribe(query => {
      if (query.length >= 3) {
        this.fetchSuggestions(query);
      }
    });
  }

  onAddressInput(value: string) {
    this.address.set(value);
    this.selectedAddress.set(null); // Reset selection when typing

    if (value.length < 3) {
      this.suggestions.set([]);
      this.showSuggestions.set(false);
      return;
    }

    this.searchSubject.next(value);
  }

  async fetchSuggestions(query: string) {
    const url = `https://api-adresse.data.gouv.fr/search/?q=${encodeURIComponent(query)}&limit=5&autocomplete=1`;

    this.http.get(url).subscribe({
      next: (data: any) => {
        if (data.features && data.features.length > 0) {
          // Filter for good quality results only
          const goodSuggestions = data.features.filter((f: any) =>
            f.properties.score > 0.3 &&
            f.properties.type !== 'municipality' // Avoid generic city results
          );
          this.suggestions.set(goodSuggestions);
          this.showSuggestions.set(true);
        } else {
          this.suggestions.set([]);
          this.showSuggestions.set(false);
        }
      },
      error: (error) => {
        console.error('Error fetching suggestions:', error);
        this.suggestions.set([]);
        this.showSuggestions.set(false);
      }
    });
  }

  selectSuggestion(suggestion: any) {
    // Store the full suggestion object
    this.selectedAddress.set(suggestion);
    this.address.set(suggestion.properties.label);
    this.suggestions.set([]);
    this.showSuggestions.set(false);
  }

  canSearch(): boolean {
    // Only allow search if an address was selected from suggestions
    return this.selectedAddress() !== null && !this.loading();
  }

  search() {
    if (!this.canSearch()) {
      alert('Veuillez sélectionner une adresse dans la liste de suggestions');
      return;
    }

    const selected = this.selectedAddress();
    console.log('Searching for selected address:', selected);

    this.loading.set(true);
    this.results.set(null);

    // Use the selected address label for the API call
    this.coverageService.checkCoverage(selected.properties.label).subscribe({
      next: (data) => {
        console.log('Results received:', data);
        this.results.set(data);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error:', error);
        this.loading.set(false);
        alert('Erreur lors de la vérification de la couverture');
      }
    });
  }

  clearAddress() {
    this.address.set('');
    this.selectedAddress.set(null);
    this.suggestions.set([]);
    this.showSuggestions.set(false);
    this.results.set(null);
  }
}
