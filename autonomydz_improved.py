#!/usr/bin/env python3
"""
AutonomyBot Ultra - Improved RunPod-Optimized Conversational Coding Agent
Builds, fixes, and explains modern web projects from prompts.
Optimized for cloud deployment with better resource management and error handling.
"""

import os
import sys
import json
import subprocess
import time
import logging
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import signal
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

try:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.logging import RichHandler
except ImportError as e:
    raise ImportError("[!] 'rich' library is required. Install with: pip install rich") from e

# Configure logging for RunPod environment
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("autonomybot")

class ProjectType(Enum):
    """Supported project types."""
    NEXTJS = "nextjs"
    REACT = "react"
    VITE = "vite"
    EXPRESS = "express"
    FASTAPI = "fastapi"
    FLASK = "flask"
    VANILLA = "vanilla"

@dataclass
class ProjectConfig:
    """Project configuration structure."""
    name: str
    type: ProjectType
    description: str
    features: List[str]
    tech_stack: List[str]
    setup_git: bool = False
    repo_url: Optional[str] = None
    port: int = 3000

class ResourceManager:
    """Manages system resources and cleanup for RunPod environment."""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.temp_files: List[Path] = []
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def register_process(self, process: subprocess.Popen):
        """Register a process for cleanup."""
        self.processes.append(process)
        
    def register_temp_file(self, file_path: Path):
        """Register a temporary file for cleanup."""
        self.temp_files.append(file_path)
        
    def cleanup(self):
        """Clean up all resources."""
        # Terminate processes
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except (subprocess.TimeoutExpired, OSError):
                try:
                    process.kill()
                except OSError:
                    pass
                    
        # Remove temp files
        for file_path in self.temp_files:
            try:
                if file_path.exists():
                    file_path.unlink()
            except OSError:
                pass
                
        self.executor.shutdown(wait=False)

class ModelManager:
    """Manages LLM models with fallback and optimization for RunPod."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.primary_models = [
            "qwen2.5-coder:32b",
            "deepseek-coder:33b", 
            "codellama:34b",
            "qwen2.5-coder:14b",
            "deepseek-coder:6.7b",
            "codellama:13b"
        ]
        self.available_models: List[str] = []
        self.current_model: Optional[str] = None
        
    async def initialize(self) -> bool:
        """Initialize and check available models."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get('models', [])
                        self.available_models = [model['name'] for model in models]
                        
                        # Find best available model
                        for model in self.primary_models:
                            if model in self.available_models:
                                self.current_model = model
                                logger.info(f"Using model: {model}")
                                return True
                                
                        if self.available_models:
                            self.current_model = self.available_models[0]
                            logger.warning(f"Using fallback model: {self.current_model}")
                            return True
                        else:
                            logger.error("No models available")
                            return False
                    else:
                        logger.error(f"Ollama API error: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Cannot connect to Ollama: {e}")
            return False
            
    async def call_llm(self, prompt: str, system_prompt: str = "", timeout: int = 120) -> str:
        """Call LLM with improved error handling and timeout."""
        if not self.current_model:
            logger.error("No model available")
            return ""
            
        payload = {
            "model": self.current_model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "num_ctx": 4096
            }
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "")
                    else:
                        logger.error(f"LLM Error: {response.status}")
                        return ""
        except asyncio.TimeoutError:
            logger.error("LLM request timed out")
            return ""
        except Exception as e:
            logger.error(f"Failed to call LLM: {e}")
            return ""

class BotMemory:
    """Enhanced memory management with persistence."""
    
    def __init__(self, storage_path: Path = Path("bot_memory.json")):
        self.storage_path = storage_path
        self.history: List[Dict[str, Any]] = []
        self.project_context: Dict[str, Any] = {}
        self.user_feedback: List[str] = []
        self.load_from_disk()

    def remember(self, key: str, value: Any):
        """Store a key-value pair in memory."""
        self.project_context[key] = value
        self.save_to_disk()

    def recall(self, key: str, default=None):
        """Retrieve a value from memory."""
        return self.project_context.get(key, default)

    def log(self, entry: Dict[str, Any]):
        """Log an entry to history."""
        entry['timestamp'] = time.time()
        self.history.append(entry)
        self.save_to_disk()

    def add_feedback(self, feedback: str):
        """Add user feedback."""
        self.user_feedback.append({
            'feedback': feedback,
            'timestamp': time.time()
        })
        self.save_to_disk()
        
    def save_to_disk(self):
        """Save memory to disk."""
        try:
            data = {
                'history': self.history,
                'project_context': self.project_context,
                'user_feedback': self.user_feedback
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to save memory: {e}")
            
    def load_from_disk(self):
        """Load memory from disk."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])
                    self.project_context = data.get('project_context', {})
                    self.user_feedback = data.get('user_feedback', [])
        except Exception as e:
            logger.warning(f"Failed to load memory: {e}")

class GitHubInspiration:
    """Enhanced GitHub integration with async support."""
    
    def __init__(self):
        self.api_base = "https://api.github.com"
        
    async def search_repositories(self, project_type: str, keywords: List[str]) -> List[Dict]:
        """Search GitHub for relevant repositories."""
        logger.info("🔍 Searching GitHub for inspiration...")
        try:
            query = f"{project_type} {' '.join(keywords)} stars:>100"
            url = f"{self.api_base}/search/repositories"
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': 10
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        repos = data.get('items', [])
                        inspiration = []
                        for repo in repos[:5]:
                            inspiration.append({
                                'name': repo['name'],
                                'description': repo.get('description', ''),
                                'stars': repo['stargazers_count'],
                                'url': repo['html_url'],
                                'topics': repo.get('topics', []),
                                'language': repo.get('language', '')
                            })
                        return inspiration
                    else:
                        logger.error(f"GitHub API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"GitHub search failed: {e}")
            return []

class ProjectTemplates:
    """Project templates for different frameworks."""
    
    @staticmethod
    def get_template(project_type: ProjectType) -> Dict[str, Any]:
        """Get project template configuration."""
        templates = {
            ProjectType.NEXTJS: {
                "package_json": {
                    "name": "{project_name}",
                    "version": "0.1.0",
                    "private": True,
                    "scripts": {
                        "dev": "next dev",
                        "build": "next build",
                        "start": "next start",
                        "lint": "next lint"
                    },
                    "dependencies": {
                        "next": "14.0.0",
                        "react": "^18",
                        "react-dom": "^18"
                    },
                    "devDependencies": {
                        "typescript": "^5",
                        "@types/node": "^20",
                        "@types/react": "^18",
                        "@types/react-dom": "^18",
                        "eslint": "^8",
                        "eslint-config-next": "14.0.0"
                    }
                },
                "files": {
                    "app/page.tsx": """import React from 'react';

export default function Home() {
  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-center mb-8">
        Welcome to {project_name}
      </h1>
      <p className="text-lg text-center text-gray-600">
        Your Next.js application is ready!
      </p>
    </main>
  );
}""",
                    "app/layout.tsx": """import React from 'react';
import './globals.css';

export const metadata = {
  title: '{project_name}',
  description: 'Generated by AutonomyBot Ultra',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}""",
                    "app/globals.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: system-ui, sans-serif;
}""",
                    "next.config.js": """/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
};

module.exports = nextConfig;""",
                    "tailwind.config.js": """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};""",
                    "tsconfig.json": """{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}"""
                }
            },
            ProjectType.REACT: {
                "package_json": {
                    "name": "{project_name}",
                    "version": "0.1.0",
                    "private": True,
                    "dependencies": {
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0",
                        "react-scripts": "5.0.1"
                    },
                    "scripts": {
                        "start": "react-scripts start",
                        "build": "react-scripts build --legacy-peer-deps",
                        "test": "react-scripts test",
                        "eject": "react-scripts eject"
                    },
                    "devDependencies": {
                        "typescript": "^4.9.5"
                    }
                },
                "files": {
                    "public/index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>""",
                    "src/index.js": """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);""",
                    "src/App.js": """import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to {project_name}</h1>
        <p>Your React application is ready!</p>
      </header>
    </div>
  );
}

export default App;""",
                    "src/App.css": """.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}"""
                }
            }
        }
        return templates.get(project_type, templates[ProjectType.REACT])

class AutonomyBotUltra:
    """Enhanced AutonomyBot Ultra optimized for RunPod deployment."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.console = Console()
        self.model_manager = ModelManager(ollama_url)
        self.memory = BotMemory()
        self.github_inspiration = GitHubInspiration()
        self.resource_manager = ResourceManager()
        self.project_path: Optional[Path] = None
        self.current_config: Optional[ProjectConfig] = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info("Received shutdown signal, cleaning up...")
        self.resource_manager.cleanup()
        sys.exit(0)

    async def initialize(self) -> bool:
        """Initialize the bot and check dependencies."""
        logger.info("Initializing AutonomyBot Ultra...")
        
        # Check Ollama connection and models
        if not await self.model_manager.initialize():
            logger.error("Failed to initialize models")
            return False
            
        # Check system dependencies
        dependencies = ['node', 'npm', 'git']
        missing = []
        for dep in dependencies:
            try:
                subprocess.run([dep, '--version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing.append(dep)
                
        if missing:
            logger.error(f"Missing dependencies: {', '.join(missing)}")
            return False
            
        logger.info("✅ Initialization complete")
        return True

    def display_banner(self):
        """Display the enhanced banner."""
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                🤖 AUTONOMYBOT ULTRA v2.0 🤖                   ║
║         RunPod-Optimized Conversational Coding Agent         ║
║        Build • Fix • Explain • Deploy • Scale • Repeat       ║
╚═══════════════════════════════════════════════════════════════╝
        """
        self.console.print(Panel(banner, style="bold cyan"))
        self.console.print("[bold green]Welcome![/bold green] I'm your AI coding companion, optimized for cloud deployment.\n")

    async def gather_requirements(self) -> ProjectConfig:
        """Gather project requirements from user."""
        self.console.print("[bold blue]Let's create your project![/bold blue]\n")
        
        # Project name
        project_name = Prompt.ask(
            "[yellow]Project name[/yellow]",
            default="my-awesome-app"
        ).strip().lower().replace(' ', '-')
        
        # Project type
        self.console.print("\n[bold]Available project types:[/bold]")
        for i, ptype in enumerate(ProjectType, 1):
            self.console.print(f"{i}. {ptype.value.upper()}")
            
        type_choice = Prompt.ask(
            "[yellow]Choose project type[/yellow]",
            choices=[str(i) for i in range(1, len(ProjectType) + 1)],
            default="1"
        )
        project_type = list(ProjectType)[int(type_choice) - 1]
        
        # Description
        description = Prompt.ask(
            "[yellow]Project description[/yellow]",
            default=f"A modern {project_type.value} application"
        )
        
        # Features
        feature_input = Prompt.ask(
            "[yellow]Key features (comma-separated)[/yellow]",
            default="responsive design, modern UI, fast performance"
        )
        features = [f.strip() for f in feature_input.split(',')]
        
        # Tech stack
        tech_input = Prompt.ask(
            "[yellow]Additional technologies (comma-separated)[/yellow]",
            default="tailwindcss, typescript"
        )
        tech_stack = [t.strip() for t in tech_input.split(',')]
        
        # Git setup
        setup_git = Confirm.ask("[yellow]Setup Git repository?[/yellow]", default=True)
        repo_url = None
        if setup_git:
            repo_url = Prompt.ask(
                "[yellow]GitHub repository URL (optional)[/yellow]",
                default=""
            ) or None
            
        return ProjectConfig(
            name=project_name,
            type=project_type,
            description=description,
            features=features,
            tech_stack=tech_stack,
            setup_git=setup_git,
            repo_url=repo_url
        )

    async def create_project_structure(self, config: ProjectConfig) -> Path:
        """Create project directory structure."""
        project_path = Path.cwd() / config.name
        
        # Remove existing directory if it exists
        if project_path.exists():
            import shutil
            shutil.rmtree(project_path)
            
        project_path.mkdir(exist_ok=True)
        logger.info(f"📁 Created project directory: {project_path}")
        
        return project_path

    async def generate_code(self, config: ProjectConfig, project_path: Path):
        """Generate project code based on configuration."""
        template = ProjectTemplates.get_template(config.type)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Generating project files...", total=None)
            
            # Generate package.json
            package_json = template["package_json"].copy()
            package_json["name"] = config.name
            package_json["description"] = config.description
            
            # Add additional dependencies based on tech stack
            if "tailwindcss" in config.tech_stack:
                package_json.setdefault("devDependencies", {})["tailwindcss"] = "^3.3.0"
                package_json["devDependencies"]["autoprefixer"] = "^10.4.16"
                package_json["devDependencies"]["postcss"] = "^8.4.31"
                
            if "typescript" in config.tech_stack and config.type != ProjectType.NEXTJS:
                package_json.setdefault("devDependencies", {})["typescript"] = "^5.0.0"
                
            # Write package.json
            with open(project_path / "package.json", "w", encoding="utf-8") as f:
                json.dump(package_json, f, indent=2)
                
            # Generate other files
            for file_path, content in template["files"].items():
                full_path = project_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Replace placeholders
                content = content.replace("{project_name}", config.name)
                
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                    
            progress.update(task, description="✅ Project files generated")

    async def enhance_with_llm(self, config: ProjectConfig, project_path: Path):
        """Enhance the generated code using LLM."""
        system_prompt = """You are a senior full-stack developer. Enhance the provided project with the requested features. 
Return a JSON object with file paths as keys and enhanced code content as values.
Focus on modern best practices, clean code, and the specific features requested."""
        
        prompt = f"""
Enhance this {config.type.value} project with the following:
- Project: {config.name}
- Description: {config.description}
- Features: {', '.join(config.features)}
- Tech Stack: {', '.join(config.tech_stack)}

Current project structure: {list(f.name for f in project_path.rglob('*') if f.is_file())}

Please enhance the code to include the requested features and improve the overall architecture.
"""

        response = await self.model_manager.call_llm(prompt, system_prompt)
        
        if response:
            try:
                enhanced_files = json.loads(response)
                for file_path, content in enhanced_files.items():
                    full_path = project_path / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(content)
                logger.info("🚀 Enhanced project with AI improvements")
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM response for enhancements")

    async def install_dependencies(self, project_path: Path) -> bool:
        """Install project dependencies."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Installing dependencies...", total=None)
                
                process = await asyncio.create_subprocess_exec(
                    "npm", "install", "--legacy-peer-deps",
                    cwd=project_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    progress.update(task, description="✅ Dependencies installed")
                    return True
                else:
                    logger.error(f"npm install failed: {stderr.decode()}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False

    async def setup_git_repository(self, config: ProjectConfig, project_path: Path):
        """Setup Git repository."""
        if not config.setup_git:
            return
            
        try:
            # Initialize git
            await asyncio.create_subprocess_exec(
                "git", "init",
                cwd=project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Create .gitignore
            gitignore_content = """
node_modules/
.next/
.env.local
.env
dist/
build/
*.log
.DS_Store
.vscode/
.idea/
coverage/
.nyc_output/
            """.strip()
            
            with open(project_path / ".gitignore", "w") as f:
                f.write(gitignore_content)
                
            # Configure git user
            await asyncio.create_subprocess_exec(
                "git", "config", "user.name", "AutonomyBot Ultra",
                cwd=project_path
            )
            await asyncio.create_subprocess_exec(
                "git", "config", "user.email", "autonomybot@runpod.ai",
                cwd=project_path
            )
            
            # Add and commit
            await asyncio.create_subprocess_exec(
                "git", "add", ".",
                cwd=project_path
            )
            await asyncio.create_subprocess_exec(
                "git", "commit", "-m", f"🚀 Initial commit for {config.name}",
                cwd=project_path
            )
            
            logger.info("📚 Git repository initialized")
            
            # Push to remote if URL provided
            if config.repo_url:
                try:
                    await asyncio.create_subprocess_exec(
                        "git", "remote", "add", "origin", config.repo_url,
                        cwd=project_path
                    )
                    await asyncio.create_subprocess_exec(
                        "git", "branch", "-M", "main",
                        cwd=project_path
                    )
                    await asyncio.create_subprocess_exec(
                        "git", "push", "-u", "origin", "main",
                        cwd=project_path
                    )
                    logger.info(f"🚀 Pushed to {config.repo_url}")
                except Exception as e:
                    logger.warning(f"Failed to push to remote: {e}")
                    
        except Exception as e:
            logger.error(f"Git setup failed: {e}")

    async def run_development_server(self, project_path: Path) -> Optional[subprocess.Popen]:
        """Start the development server."""
        try:
            self.console.print("[yellow]🚀 Starting development server...[/yellow]")
            
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.resource_manager.register_process(process)
            
            # Wait a moment for server to start
            await asyncio.sleep(3)
            
            if process.poll() is None:
                self.console.print("[green]✅ Development server started![/green]")
                self.console.print("[blue]🌐 Visit http://localhost:3000 to view your app[/blue]")
                return process
            else:
                stderr = process.stderr.read() if process.stderr else ""
                logger.error(f"Development server failed to start: {stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to start development server: {e}")
            return None

    async def conversational_loop(self):
        """Main conversational loop."""
        try:
            # Gather requirements
            config = await self.gather_requirements()
            self.current_config = config
            self.memory.remember('project_config', config.__dict__)
            
            # Create project
            project_path = await self.create_project_structure(config)
            self.project_path = project_path
            
            # Generate code
            await self.generate_code(config, project_path)
            
            # Enhance with LLM
            await self.enhance_with_llm(config, project_path)
            
            # Install dependencies
            if await self.install_dependencies(project_path):
                self.console.print("[green]✅ Project setup complete![/green]")
            else:
                self.console.print("[yellow]⚠️ Dependency installation failed, but project is created[/yellow]")
                
            # Setup Git
            await self.setup_git_repository(config, project_path)
            
            # Success message
            self.console.print(f"\n[bold green]🎉 SUCCESS! Project '{config.name}' created![/bold green]")
            self.console.print(f"[green]📁 Location: {project_path}[/green]")
            
            # Ask if user wants to start dev server
            if Confirm.ask("[yellow]Start development server?[/yellow]", default=True):
                await self.run_development_server(project_path)
                
            # Interactive commands
            await self.interactive_mode()
            
        except KeyboardInterrupt:
            logger.info("Operation cancelled by user")
        except Exception as e:
            logger.error(f"Error in conversational loop: {e}")
        finally:
            self.resource_manager.cleanup()

    async def interactive_mode(self):
        """Interactive command mode."""
        while True:
            self.console.print("\n[bold magenta]What would you like to do?[/bold magenta]")
            self.console.print("Commands: [cyan]feature[/cyan] | [cyan]fix[/cyan] | [cyan]explain[/cyan] | [cyan]deploy[/cyan] | [cyan]status[/cyan] | [cyan]exit[/cyan]")
            
            try:
                command = Prompt.ask("[bold yellow]Command[/bold yellow]").strip().lower()
                
                if command in ("exit", "quit"):
                    break
                elif "feature" in command:
                    await self.add_feature()
                elif "fix" in command:
                    await self.fix_issue()
                elif "explain" in command:
                    await self.explain_code()
                elif "deploy" in command:
                    await self.deploy_guide()
                elif "status" in command:
                    await self.show_status()
                else:
                    self.console.print("[red]Unknown command. Try again.[/red]")
                    
            except KeyboardInterrupt:
                break

    async def add_feature(self):
        """Add a new feature to the project."""
        if not self.project_path:
            self.console.print("[red]No active project[/red]")
            return
            
        feature_description = Prompt.ask("[green]Describe the feature to add[/green]")
        
        system_prompt = """You are a senior developer. Add the requested feature to the existing project.
Return a JSON object with file paths as keys and updated/new code as values.
Consider the existing project structure and maintain consistency."""
        
        prompt = f"""
Add this feature to the project: {feature_description}
Project type: {self.current_config.type.value if self.current_config else 'unknown'}
Current files: {list(f.name for f in self.project_path.rglob('*') if f.is_file())}
"""

        response = await self.model_manager.call_llm(prompt, system_prompt)
        
        if response:
            try:
                updated_files = json.loads(response)
                for file_path, content in updated_files.items():
                    full_path = self.project_path / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(content)
                self.console.print("[green]✅ Feature added successfully![/green]")
            except json.JSONDecodeError:
                self.console.print("[red]Failed to parse response[/red]")

    async def fix_issue(self):
        """Fix an issue in the project."""
        if not self.project_path:
            self.console.print("[red]No active project[/red]")
            return
            
        issue_description = Prompt.ask("[green]Describe the issue or paste error message[/green]")
        
        system_prompt = """You are a senior developer. Fix the described issue in the project.
Return a JSON object with file paths as keys and fixed code as values."""
        
        prompt = f"""
Fix this issue: {issue_description}
Project type: {self.current_config.type.value if self.current_config else 'unknown'}
"""

        response = await self.model_manager.call_llm(prompt, system_prompt)
        
        if response:
            try:
                fixed_files = json.loads(response)
                for file_path, content in fixed_files.items():
                    full_path = self.project_path / file_path
                    if full_path.exists():
                        with open(full_path, "w", encoding="utf-8") as f:
                            f.write(content)
                self.console.print("[green]✅ Issue fixed![/green]")
            except json.JSONDecodeError:
                self.console.print("[red]Failed to parse response[/red]")

    async def explain_code(self):
        """Explain code in the project."""
        if not self.project_path:
            self.console.print("[red]No active project[/red]")
            return
            
        # List available files
        files = [f for f in self.project_path.rglob('*') if f.is_file() and f.suffix in ['.js', '.jsx', '.ts', '.tsx', '.py']]
        if not files:
            self.console.print("[red]No code files found[/red]")
            return
            
        self.console.print("\n[bold]Available files:[/bold]")
        for i, file in enumerate(files, 1):
            self.console.print(f"{i}. {file.relative_to(self.project_path)}")
            
        try:
            choice = int(Prompt.ask("[yellow]Choose file to explain[/yellow]")) - 1
            if 0 <= choice < len(files):
                file_path = files[choice]
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                    
                system_prompt = "You are a senior developer. Explain this code in detail for someone learning the project."
                prompt = f"Explain this {file_path.suffix} file:\n\n{code}"
                
                explanation = await self.model_manager.call_llm(prompt, system_prompt)
                if explanation:
                    self.console.print(Panel(explanation, title=f"📖 {file_path.name}", style="cyan"))
            else:
                self.console.print("[red]Invalid choice[/red]")
        except ValueError:
            self.console.print("[red]Invalid input[/red]")

    async def deploy_guide(self):
        """Show deployment guide for RunPod."""
        guide = """
🚀 RunPod Deployment Guide

1. **Prepare for Deployment:**
   - Ensure your project builds successfully: `npm run build`
   - Test locally: `npm start`

2. **RunPod Setup:**
   - Upload your project to RunPod storage
   - Use a Node.js template
   - Set environment variables if needed

3. **Container Configuration:**
   - Expose port 3000 (or your app's port)
   - Set startup command: `npm start`
   - Configure health checks

4. **Environment Variables:**
   - NODE_ENV=production
   - PORT=3000
   - Any app-specific variables

5. **Scaling:**
   - Use RunPod's auto-scaling features
   - Monitor performance metrics
   - Set up load balancing if needed
        """
        self.console.print(Panel(guide, title="🚀 RunPod Deployment", style="blue"))

    async def show_status(self):
        """Show current project status."""
        if not self.project_path:
            self.console.print("[red]No active project[/red]")
            return
            
        table = Table(title="📊 Project Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        if self.current_config:
            table.add_row("Name", self.current_config.name)
            table.add_row("Type", self.current_config.type.value)
            table.add_row("Description", self.current_config.description)
            table.add_row("Features", ", ".join(self.current_config.features))
            table.add_row("Tech Stack", ", ".join(self.current_config.tech_stack))
            
        table.add_row("Location", str(self.project_path))
        table.add_row("Files", str(len(list(self.project_path.rglob('*')))))
        
        # Check if package.json exists
        if (self.project_path / "package.json").exists():
            table.add_row("Dependencies", "✅ Configured")
        else:
            table.add_row("Dependencies", "❌ Missing")
            
        self.console.print(table)

    async def run(self):
        """Main entry point."""
        self.display_banner()
        
        if not await self.initialize():
            self.console.print("[red]❌ Initialization failed. Please check your setup.[/red]")
            return
            
        await self.conversational_loop()
        
        # Cleanup
        self.resource_manager.cleanup()
        self.console.print("[bold cyan]👋 Goodbye![/bold cyan]")

def main():
    """Main function to run the bot."""
    try:
        bot = AutonomyBotUltra()
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
