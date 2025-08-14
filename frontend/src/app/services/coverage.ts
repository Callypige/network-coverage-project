import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CoverageService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000';

  // This method checks the coverage for a given address
  checkCoverage(address: string): Observable<any> {
    // We send the request to the backend
    const payload = {
      "id1": address
    };

    return this.http.post(`${this.apiUrl}/coverage`, payload);
  }
}
