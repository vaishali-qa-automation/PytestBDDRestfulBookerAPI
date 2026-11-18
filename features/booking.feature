@booking @smoke
Feature: Booking end-to-end verification

  @create @get
  Scenario: Create a booking and verify it via retrieval
    Given a guest wants to book a random stay
    When the booking is created
    Then the booking is created successfully
    And retrieving the booking returns the same guest details

  @create @validation
  Scenario: Created booking matches a valid schema
    Given a guest wants to book a random stay
    When the booking is created
    Then the booking response matches the expected schema