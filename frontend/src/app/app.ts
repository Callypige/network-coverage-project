import { Component, signal, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  imports: [FormsModule, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('frontend');
  address = signal('');
  results = signal<string[]>([]);
  loading = signal(false);
  // for suggestions
  suggestions = signal<any[]>([]);
  showSuggestions = signal(false);

  search() {
    this.loading.set(true);
    this.results.set([]);

    // Simulate an API call
    setTimeout(() => {
      this.results.set(['Result 1', 'Result 2', 'Result 3']);
      this.loading.set(false);
    }, 1000);
  }
}
