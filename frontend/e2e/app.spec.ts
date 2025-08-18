import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('/');
});

test.describe('Coverage Application End-to-End Test', () => {

  test('should allow a user to search for an address and see coverage results', async ({ page }) => {
    // 1. Locate and fill the input field
    const addressInput = page.locator('input[placeholder="Tapez au moins 3 lettres pour rechercher une adresse..."]');
    await addressInput.fill('1 rue de la paix');

    // 2. Wait for suggestions to appear and select the first one
    const firstSuggestion = page.locator('.suggestion-item').first();
    await firstSuggestion.waitFor({ timeout: 10000 });

    // 3. Get the suggestion text before clicking
    const suggestionLabel = firstSuggestion.locator('.suggestion-label');
    const textWithEmoji = await suggestionLabel.textContent();
    expect(textWithEmoji).not.toBeNull();
    const expectedText = textWithEmoji!.replace('📍', '').trim();

    // 4. Click on the suggestion to select it
    await firstSuggestion.click();

    // 5. Verify the input field value and that address is selected
    await expect(addressInput).toHaveValue(expectedText);

    // 6. Verify the selected address confirmation appears
    const selectedAddressConfirmation = page.locator('.selected-address');
    await expect(selectedAddressConfirmation).toBeVisible();
    await expect(selectedAddressConfirmation).toContainText('Adresse sélectionnée');

    // 7. Verify search button is enabled and click it
    const searchButton = page.locator('button.search-btn');
    await expect(searchButton).toBeEnabled();
    await expect(searchButton).toHaveText('Vérifier la couverture');

    await searchButton.click();

    // 8. Wait for loading state to begin
    await expect(searchButton).toHaveText('Recherche...', { timeout: 5000 });

    // 9. Wait for loading to complete (button text returns to normal)
    await expect(searchButton).toHaveText('Vérifier la couverture', { timeout: 15000 });

    // 10. Verify results section is visible
    const resultsSection = page.locator('.results');
    await expect(resultsSection).toBeVisible();

    // 11. Check if we have actual results or the default message
    const operatorsGrid = page.locator('.operators-grid');
    const noResultsMessage = page.locator('.results p');

    // Wait a bit for the DOM to update
    await page.waitForTimeout(1000);

    const hasGrid = await operatorsGrid.isVisible();
    const hasMessage = await noResultsMessage.isVisible();

    // We should have either results or the default message
    expect(hasGrid || hasMessage).toBeTruthy();

    if (hasGrid) {
      // If we have results, verify the grid content
      console.log('✅ Results found - verifying operators grid');

      await expect(operatorsGrid).toBeVisible();

      // Verify we have operator cards
      const operatorCards = page.locator('.operator-card');
      await expect(operatorCards.first()).toBeVisible();

      // Verify the four operators are present
      await expect(page.locator('.operator-name', { hasText: 'Orange' })).toBeVisible();
      await expect(page.locator('.operator-name', { hasText: 'SFR' })).toBeVisible();
      await expect(page.locator('.operator-name', { hasText: 'Bouygues' })).toBeVisible();
      await expect(page.locator('.operator-name', { hasText: 'Free' })).toBeVisible();

      // Verify each operator has technology badges
      const orangeCard = page.locator('.operator-card').filter({ hasText: 'Orange' });
      await expect(orangeCard.locator('.badge')).toHaveCount(3); // 2G, 3G, 4G

    } else if (hasMessage) {
      // If no results, verify the default message
      console.log('No results returned - verifying default message');
      await expect(noResultsMessage).toBeVisible();
      await expect(noResultsMessage).toContainText('Sélectionnez une adresse');
    }
  });

  test('should disable search button if no address is selected', async ({ page }) => {
    // 1. Fill input but don't select any suggestion
    const addressInput = page.locator('input[placeholder="Tapez au moins 3 lettres pour rechercher une adresse..."]');
    await addressInput.fill('adresse non sélectionnée');

    // 2. Wait for potential suggestions to appear
    await page.waitForTimeout(1000);

    // 3. Verify search button is disabled when no address is selected
    const searchButton = page.locator('button.search-btn');
    await expect(searchButton).toBeDisabled();
    await expect(searchButton).toHaveClass(/disabled/);

    // 4. Verify no selected address confirmation appears
    const selectedAddressConfirmation = page.locator('.selected-address');
    await expect(selectedAddressConfirmation).not.toBeVisible();
  });

  test('should show suggestions when typing at least 3 characters', async ({ page }) => {
    const addressInput = page.locator('input[placeholder="Tapez au moins 3 lettres pour rechercher une adresse..."]');

    // 1. Type less than 3 characters - no suggestions should appear
    await addressInput.fill('pa');

    // Verify info message appears
    const infoMessage = page.locator('.info-message');
    await expect(infoMessage).toBeVisible();
    await expect(infoMessage).toContainText('Tapez au moins 3 caractères');

    // No suggestions dropdown should be visible
    const suggestionsDropdown = page.locator('.suggestions-dropdown');
    await expect(suggestionsDropdown).not.toBeVisible();

    // 2. Type 3 or more characters - suggestions should appear
    await addressInput.fill('par');

    // Info message should disappear
    await expect(infoMessage).not.toBeVisible();

    // Suggestions should appear (either real suggestions or "no results")
    await expect(suggestionsDropdown).toBeVisible({ timeout: 5000 });
  });

  test('should allow clearing selected address', async ({ page }) => {
    const addressInput = page.locator('input[placeholder="Tapez au moins 3 lettres pour rechercher une adresse..."]');

    // 1. Search and select an address
    await addressInput.fill('1 rue de la paix');

    const firstSuggestion = page.locator('.suggestion-item').first();
    await firstSuggestion.waitFor({ timeout: 10000 });
    await firstSuggestion.click();

    // 2. Verify address is selected
    const selectedAddressConfirmation = page.locator('.selected-address');
    await expect(selectedAddressConfirmation).toBeVisible();

    // 3. Verify clear button appears and click it
    const clearButton = page.locator('button.clear-btn');
    await expect(clearButton).toBeVisible();
    await clearButton.click();

    // 4. Verify address is cleared
    await expect(addressInput).toHaveValue('');
    await expect(selectedAddressConfirmation).not.toBeVisible();
    await expect(clearButton).not.toBeVisible();

    // 5. Verify search button is disabled again
    const searchButton = page.locator('button.search-btn');
    await expect(searchButton).toBeDisabled();
  });
});
