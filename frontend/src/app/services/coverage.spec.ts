import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';

import { CoverageService } from './coverage';

describe('CoverageService', () => {
  let service: CoverageService;
  let httpMock: HttpTestingController;
  const apiUrl = 'http://localhost:8000';

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        // We provide the real service and the tools to mock HTTP requests
        CoverageService,
        provideHttpClient(),
        provideHttpClientTesting(),
      ]
    });

    service = TestBed.inject(CoverageService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should send a POST request to the correct URL with the correct payload', (done: DoneFn) => {
    const testAddress = '123 Rue du Test, 75001 Paris';
    const mockResponse = { status: 'ok' };

    // We simulate the HTTP request
    service.checkCoverage(testAddress).subscribe(response => {
      expect(response).toEqual(mockResponse);
      done();
    });

    // 1. We expect a single request to be made to this URL
    const req = httpMock.expectOne(`${apiUrl}/coverage`);

    // 2. We check that the method is indeed POST and that the request body is correct
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ "id1": testAddress });

    // Simulate successful server response
    req.flush(mockResponse);
  });

  it('should handle HTTP errors', (done: DoneFn) => {
    const testAddress = 'une-adresse-erreur';
    const errorMessage = 'Internal Server Error';

    service.checkCoverage(testAddress).subscribe({
      next: () => fail('should have failed with an error'), // We expect the observable to fail
      error: (error) => {
        expect(error.status).toBe(500);
        expect(error.statusText).toBe(errorMessage);
        done();
      }
    });

    const req = httpMock.expectOne(`${apiUrl}/coverage`);

    // Simulate server error response
    req.flush(errorMessage, { status: 500, statusText: errorMessage });
  });
});
