import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Modal from '../Modal';

describe('Modal Component', () => {
  const defaultProps = {
    isOpen: true,
    onClose: jest.fn(),
    title: 'Test Modal',
    children: <div>Modal Content</div>,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders when isOpen is true', () => {
    render(<Modal {...defaultProps} />);
    expect(screen.getByText('Test Modal')).toBeInTheDocument();
    expect(screen.getByText('Modal Content')).toBeInTheDocument();
  });

  it('does not render when isOpen is false', () => {
    render(<Modal {...defaultProps} isOpen={false} />);
    expect(screen.queryByText('Test Modal')).not.toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    render(<Modal {...defaultProps} />);
    const closeButton = screen.getByLabelText('Close');
    fireEvent.click(closeButton);
    expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when overlay is clicked', () => {
    render(<Modal {...defaultProps} />);
    const overlay = screen.getByTestId('modal-overlay');
    fireEvent.click(overlay);
    expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('does not close when modal content is clicked', () => {
    render(<Modal {...defaultProps} />);
    const content = screen.getByText('Modal Content');
    fireEvent.click(content);
    expect(defaultProps.onClose).not.toHaveBeenCalled();
  });

  it('renders small size modal', () => {
    render(<Modal {...defaultProps} size="sm" />);
    const modalContent = screen.getByRole('dialog');
    expect(modalContent).toHaveClass('max-w-md');
  });

  it('renders medium size modal', () => {
    render(<Modal {...defaultProps} size="md" />);
    const modalContent = screen.getByRole('dialog');
    expect(modalContent).toHaveClass('max-w-2xl');
  });

  it('renders large size modal', () => {
    render(<Modal {...defaultProps} size="lg" />);
    const modalContent = screen.getByRole('dialog');
    expect(modalContent).toHaveClass('max-w-4xl');
  });

  it('renders extra large size modal', () => {
    render(<Modal {...defaultProps} size="xl" />);
    const modalContent = screen.getByRole('dialog');
    expect(modalContent).toHaveClass('max-w-6xl');
  });

  it('handles Escape key press', () => {
    render(<Modal {...defaultProps} />);
    fireEvent.keyDown(document, { key: 'Escape', code: 'Escape' });
    expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('renders footer when provided', () => {
    render(
      <Modal {...defaultProps} footer={<button>Action</button>} />
    );
    expect(screen.getByText('Action')).toBeInTheDocument();
  });

  it('prevents body scroll when modal is open', () => {
    render(<Modal {...defaultProps} />);
    expect(document.body.style.overflow).toBe('hidden');
  });

  it('restores body scroll when modal is closed', () => {
    const { rerender } = render(<Modal {...defaultProps} />);
    expect(document.body.style.overflow).toBe('hidden');
    
    rerender(<Modal {...defaultProps} isOpen={false} />);
    expect(document.body.style.overflow).toBe('');
  });
});
