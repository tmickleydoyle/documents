import React from 'react';
import { Button as MUIButton } from '@mui/material';

interface ButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  variant?: 'contained' | 'outlined' | 'text';
  disabled?: boolean;
  size?: 'small' | 'medium' | 'large';
}

const Button: React.FC<ButtonProps> = ({ 
  children, 
  onClick, 
  variant = 'contained',
  disabled = false,
  size = 'medium'
}) => {
  return (
    <MUIButton
      variant={variant}
      onClick={onClick}
      disabled={disabled}
      size={size}
      sx={{
        textTransform: 'none',
        borderRadius: 2,
        fontWeight: 600,
      }}
    >
      {children}
    </MUIButton>
  );
};

export default Button;