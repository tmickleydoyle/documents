"""
Test configuration and fixtures for the Fern Model Evaluation Framework.
"""

import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_react_component():
    """Sample React component code for testing."""
    return """
import React, { useState } from 'react';

interface ButtonProps {
    children: React.ReactNode;
    onClick: () => void;
    variant?: 'primary' | 'secondary';
    disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({
    children,
    onClick,
    variant = 'primary',
    disabled = false
}) => {
    const [isClicked, setIsClicked] = useState(false);

    const handleClick = () => {
        setIsClicked(true);
        onClick();
        setTimeout(() => setIsClicked(false), 200);
    };

    return (
        <button
            className={`btn btn-${variant} ${isClicked ? 'clicked' : ''}`}
            onClick={handleClick}
            disabled={disabled}
            aria-pressed={isClicked}
        >
            {children}
        </button>
    );
};

export default Button;
"""


@pytest.fixture
def sample_nextjs_page():
    """Sample Next.js page component for testing."""
    return """
import React from 'react';
import Head from 'next/head';
import { GetServerSideProps } from 'next';
import Button from '../components/Button';

interface HomePageProps {
    title: string;
    description: string;
}

const HomePage: React.FC<HomePageProps> = ({ title, description }) => {
    const handleButtonClick = () => {
        console.log('Button clicked!');
    };

    return (
        <>
            <Head>
                <title>{title}</title>
                <meta name="description" content={description} />
            </Head>

            <main className="container">
                <h1>{title}</h1>
                <p>{description}</p>

                <Button onClick={handleButtonClick} variant="primary">
                    Get Started
                </Button>
            </main>
        </>
    );
};

export const getServerSideProps: GetServerSideProps = async () => {
    return {
        props: {
            title: "Welcome to Our App",
            description: "The best Next.js application ever built"
        }
    };
};

export default HomePage;
"""


@pytest.fixture
def sample_package_json():
    """Sample package.json for testing."""
    return {
        "name": "test-nextjs-app",
        "version": "1.0.0",
        "dependencies": {
            "next": "13.4.0",
            "react": "18.2.0",
            "react-dom": "18.2.0",
            "@types/react": "18.2.0",
        },
        "devDependencies": {"typescript": "5.0.0", "@types/node": "20.0.0"},
    }


@pytest.fixture
def mock_application_structure(
    temp_dir, sample_react_component, sample_nextjs_page, sample_package_json
):
    """Create a mock Next.js application structure for testing."""
    import json

    # Create directories
    (temp_dir / "components").mkdir()
    (temp_dir / "pages").mkdir()
    (temp_dir / "styles").mkdir()
    (temp_dir / "utils").mkdir()

    # Create component files
    (temp_dir / "components" / "Button.tsx").write_text(sample_react_component)

    # Create page files
    (temp_dir / "pages" / "index.tsx").write_text(sample_nextjs_page)

    # Create style files
    (temp_dir / "styles" / "globals.css").write_text(
        """
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
}

.btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.btn-primary {
    background-color: #007bff;
    color: white;
}

.btn-secondary {
    background-color: #6c757d;
    color: white;
}
"""
    )

    # Create utility files
    (temp_dir / "utils" / "helpers.ts").write_text(
        """
export const formatDate = (date: Date): string => {
    return date.toISOString().split('T')[0];
};

export const debounce = <T extends (...args: any[]) => any>(
    func: T,
    delay: number
): ((...args: Parameters<T>) => void) => {
    let timeoutId: NodeJS.Timeout;
    return (...args: Parameters<T>) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
};
"""
    )

    # Create package.json
    (temp_dir / "package.json").write_text(json.dumps(sample_package_json, indent=2))

    # Create config files
    (temp_dir / "next.config.js").write_text(
        """
/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    swcMinify: true,
};

module.exports = nextConfig;
"""
    )

    (temp_dir / "tsconfig.json").write_text(
        json.dumps(
            {
                "compilerOptions": {
                    "target": "es5",
                    "lib": ["dom", "dom.iterable", "es6"],
                    "allowJs": True,
                    "skipLibCheck": True,
                    "strict": True,
                    "forceConsistentCasingInFileNames": True,
                    "noEmit": True,
                    "esModuleInterop": True,
                    "module": "esnext",
                    "moduleResolution": "node",
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "jsx": "preserve",
                    "incremental": True,
                    "plugins": [{"name": "next"}],
                    "baseUrl": ".",
                    "paths": {"@/*": ["./*"]},
                },
                "include": [
                    "next-env.d.ts",
                    "**/*.ts",
                    "**/*.tsx",
                    ".next/types/**/*.ts",
                ],
                "exclude": ["node_modules"],
            },
            indent=2,
        )
    )

    return temp_dir


@pytest.fixture
def evaluation_weights():
    """Standard evaluation weights for testing."""
    return {
        "semantic": 0.25,
        "functional": 0.25,
        "structural": 0.20,
        "style": 0.15,
        "maintainability": 0.10,
        "accessibility": 0.05,
    }
