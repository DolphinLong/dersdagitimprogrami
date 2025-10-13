import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders application title', () => {
  render(<App />);
  const titleElement = screen.getByText(/Ders Dağıtım Sistemi/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders dashboard navigation button', () => {
  render(<App />);
  const dashboardButton = screen.getByRole('button', { name: /Dashboard/i });
  expect(dashboardButton).toBeInTheDocument();
});

test('renders scheduler navigation button', () => {
  render(<App />);
  const schedulerButtons = screen.getAllByRole('button', { name: /Çizelge/i });
  expect(schedulerButtons.length).toBeGreaterThan(0);
});
