import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  variant?: string;
  disabled?: boolean;
}

function Button(props: ButtonProps) {
  const { children, onClick, variant = 'primary', disabled = false } = props;
  
  const getButtonClass = () => {
    let baseClass = 'btn ';
    if (variant === 'primary') {
      baseClass += 'btn-primary';
    } else if (variant === 'secondary') {
      baseClass += 'btn-secondary';
    }
    return baseClass;
  };
  
  return (
    <button
      className={getButtonClass()}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

export default Button;