import { Component, signal, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { CoverageService } from './services/coverage';

interface OperatorCoverage {
  '2G': boolean;
  '3G': boolean;
  '4G': boolean;
}

interface AddressCoverage {
  orange: OperatorCoverage;
  SFR: OperatorCoverage;
  bouygues: OperatorCoverage;
  Free: OperatorCoverage;
}

interface CoverageResults {
  [key: string]: AddressCoverage;
}

@Component({
  selector: 'app-root',
  imports: [FormsModule, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  private coverageService = inject(CoverageService);

  protected readonly title = signal('frontend');
  address = signal('');
  results = signal<CoverageResults | null>(null);
  loading = signal(false);

  search() {
    if (!this.address()) return;

    console.log('Recherche pour:', this.address());
    this.loading.set(true);
    this.results.set({});

    this.coverageService.checkCoverage(this.address()).subscribe({
      next: (data) => {
        console.log('Résultats reçus:', data);
        this.results.set(data);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Erreur:', error);
        this.loading.set(false);
      }
    });
  }
}
