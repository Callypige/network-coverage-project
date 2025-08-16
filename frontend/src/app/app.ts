import { Component, signal, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { CoverageService } from './services/coverage';

interface OperatorCoverage {
  two_g: boolean;  // 2G
  three_g: boolean; // 3G
  four_g: boolean;  // 4G
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
