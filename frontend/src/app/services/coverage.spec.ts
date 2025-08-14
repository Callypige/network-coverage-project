import { TestBed } from '@angular/core/testing';

import { Coverage } from './coverage';

describe('Coverage', () => {
  let service: Coverage;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Coverage);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
