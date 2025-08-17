import { TestBed, ComponentFixture, fakeAsync, tick } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { of, Subject, throwError } from 'rxjs';

import { App, CoverageResults } from './app';
import { CoverageService } from './services/coverage';

// Create a mock for the CoverageService
const mockCoverageService = jasmine.createSpyObj('CoverageService', ['checkCoverage']);

// Test data to simulate API responses
const mockAddressSuggestions = {
  features: [
    { properties: { label: '1 Rue de la Paix, 75002 Paris', score: 0.9, type: 'housenumber' } },
    { properties: { label: '2 Rue de la Paix, 75002 Paris', score: 0.8, type: 'housenumber' } },
    { properties: { label: 'Paris', score: 0.5, type: 'municipality' } }
  ]
};

const mockCoverageResults: CoverageResults = {
  '1 Rue de la Paix, 75002 Paris': {
    orange: { '2G': true, '3G': true, '4G': true },
    SFR: { '2G': true, '3G': true, '4G': false },
    bouygues: { '2G': true, '3G': true, '4G': true },
    Free: { '2G': false, '3G': true, '4G': true }
  }
};

describe('App Component', () => {
  let fixture: ComponentFixture<App>;
  let component: App;
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        App // Import the standalone component
      ],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        // Provide our mocked service instead of the real one
        { provide: CoverageService, useValue: mockCoverageService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(App);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);

    // Reset spies before each test to prevent interference
    mockCoverageService.checkCoverage.calls.reset();
  });

  afterEach(() => {
    // Ensure that there are no outstanding HTTP requests between tests
    httpMock.verify();
  });

  it('should create the app', () => {
    expect(component).toBeTruthy();
  });

  describe('Address Autocomplete', () => {
    // Use fakeAsync to control time (useful for debounceTime)
    it('should fetch suggestions when typing a long enough address', fakeAsync(() => {
      const input = '1 rue de la paix';
      component.onAddressInput(input);

      // Advance the clock by 300ms to trigger the debounce
      tick(300);

      const url = `https://api-adresse.data.gouv.fr/search/?q=${encodeURIComponent(input)}&limit=5&autocomplete=1`;
      const req = httpMock.expectOne(url);
      expect(req.request.method).toBe('GET');

      // Send mocked data as the response
      req.flush(mockAddressSuggestions);

      // Check that suggestions have been filtered and updated
      expect(component.suggestions().length).toBe(2);
      expect(component.suggestions()[0].properties.label).toBe('1 Rue de la Paix, 75002 Paris');
      expect(component.showSuggestions()).toBe(true);
    }));

    it('should NOT fetch suggestions if address is too short', fakeAsync(() => {
      component.onAddressInput('1');
      tick(300); // Advance the clock

      // No request should have been made
      httpMock.expectNone((req) => req.url.includes('api-adresse.data.gouv.fr'));
      expect(component.suggestions().length).toBe(0);
    }));

    it('should update state correctly when a suggestion is selected', () => {
      const suggestion = mockAddressSuggestions.features[0];
      component.selectSuggestion(suggestion);

      expect(component.address()).toBe('1 Rue de la Paix, 75002 Paris');
      expect(component.selectedAddress()).toEqual(suggestion);
      expect(component.showSuggestions()).toBe(false);
      expect(component.suggestions().length).toBe(0);
    });
  });

  describe('Coverage Search', () => {
    it('should NOT search if no address is selected', () => {
      spyOn(window, 'alert'); // Spy on the alert function to prevent it from popping up
      component.search();
      expect(mockCoverageService.checkCoverage).not.toHaveBeenCalled();
      expect(window.alert).toHaveBeenCalledWith('Veuillez sélectionner une adresse dans la liste de suggestions');
    });

    it('should call CoverageService, set loading state, and update results on success', fakeAsync(() => {
      const suggestion = mockAddressSuggestions.features[0];
      component.selectSuggestion(suggestion);

      // Use a Subject to manually control the value emission
      const coverage$ = new Subject<CoverageResults>();
      mockCoverageService.checkCoverage.and.returnValue(coverage$.asObservable());

      // Act
      component.search();

      // --- Assertions on the state DURING loading ---
      // The loading state must be true immediately after the call
      expect(component.loading()).toBe(true);
      expect(component.results()).toBeNull();
      expect(mockCoverageService.checkCoverage).toHaveBeenCalledWith('1 Rue de la Paix, 75002 Paris');

      // Simulate the arrival of the service response
      coverage$.next(mockCoverageResults);
      tick(); // Advance the clock for the subscription to complete

      // --- Assertions on the state AFTER loading ---
      expect(component.loading()).toBe(false);
      expect(component.results()).toEqual(mockCoverageResults);
    }));

    it('should handle errors from CoverageService and reset loading state', fakeAsync(() => {
        const suggestion = mockAddressSuggestions.features[0];
        component.selectSuggestion(suggestion);
        spyOn(window, 'alert');

        // Use a Subject to manually control the error emission
        const coverage$ = new Subject<CoverageResults>();
        mockCoverageService.checkCoverage.and.returnValue(coverage$.asObservable());

        // Act
        component.search();

        // --- Assertions on the state DURING loading ---
        expect(component.loading()).toBe(true);

        // Simulate the arrival of an error from the service
        coverage$.error(new Error('API Error'));
        tick(); // Advance the clock for the subscription to complete

        // --- Assertions on the state AFTER the error ---
        expect(component.loading()).toBe(false);
        expect(component.results()).toBeNull();
        expect(window.alert).toHaveBeenCalledWith('Erreur lors de la vérification de la couverture');
    }));
  });

  describe('Clear Address', () => {
    it('should reset all relevant signals', () => {
      // Put the component in a "filled" state
      component.address.set('some address');
      component.selectedAddress.set({ prop: 'value' });
      component.suggestions.set([{ prop: 'suggestion' }]);
      component.results.set({} as CoverageResults); // Set a non-null object

      component.clearAddress();

      expect(component.address()).toBe('');
      expect(component.selectedAddress()).toBeNull();
      expect(component.suggestions().length).toBe(0);
      expect(component.results()).toBeNull();
    });
  });
});
