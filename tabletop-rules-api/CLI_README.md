# 🎲 Tabletop Rules CLI - Command Line Interface

A comprehensive CLI tool for efficient tabletop game rules management with the FastAPI backend.

## 🚀 Quick Start

### Setup
```bash
# Install CLI dependencies
python setup_cli.py

# Or install manually
pip install -r cli_requirements.txt

# Test the CLI
python tabletop_cli.py --help
```

### Basic Usage
```bash
# Check backend status
python tabletop_cli.py status

# List all games
python tabletop_cli.py list-games

# Upload a rules file
python tabletop_cli.py upload rules_data/chess_rules.md

# Show rules for a game
python tabletop_cli.py show-rules chess

# Validate game integrity
python tabletop_cli.py validate chess
```

## 📋 Available Commands

### Core Commands

#### `status`
Check backend connection and authentication status.
```bash
python tabletop_cli.py status
```

#### `upload <file>`
Upload a single markdown rules file.
```bash
python tabletop_cli.py upload rules_data/chess_rules.md
python tabletop_cli.py upload --verbose rules_data/monopoly_rules.md
```

#### `list-games`
List all registered games with metadata.
```bash
python tabletop_cli.py list-games
python tabletop_cli.py list-games --verbose  # Show creation dates
```

#### `show-rules <game_id>`
Display rules for a specific game.
```bash
python tabletop_cli.py show-rules chess
python tabletop_cli.py show-rules chess --limit 5  # Show first 5 rules
```

### Management Commands

#### `delete <game_id>`
Delete a game and all its rules.
```bash
python tabletop_cli.py delete chess
python tabletop_cli.py delete chess --force  # Skip confirmation
```

#### `validate <game_id>`
Validate game rules integrity and auto-fix issues.
```bash
python tabletop_cli.py validate chess
```

#### `batch-upload <directory>`
Upload multiple files from a directory.
```bash
python tabletop_cli.py batch-upload rules_data/
python tabletop_cli.py batch-upload rules_data/ --pattern "*.md" --max 20
```

### Configuration Commands

#### `config`
Show current CLI configuration.
```bash
python tabletop_cli.py config
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```bash
API_BASE_URL=http://localhost:8000
ENVIRONMENT=development
```

### Authentication
The CLI uses hardcoded admin credentials for MVP:
- Username: `admin`
- Password: `secret`

## 📄 Markdown File Format

Rules files should follow this structure:
```markdown
---
game_id: "chess"
name: "Chess"
publisher: "FIDE"
version: "Official Rules"
description: "Classic strategy board game"
complexity: "medium"
min_players: 2
max_players: 2
ai_tags: ["strategy", "board-game"]
---

# Chess Rules

## Pawn Movement
Pawns move forward one square at a time...

## Piece Capture
Pieces capture diagonally...

## Special Moves
### Castling
The king and rook can castle under specific conditions...

### En Passant
A special pawn capture rule...
```

## 🎯 Common Workflows

### Initial Game Setup
```bash
# Upload game rules
python tabletop_cli.py upload rules_data/new_game.md

# Verify upload
python tabletop_cli.py list-games
python tabletop_cli.py validate new_game

# Test with queries
python tabletop_cli.py show-rules new_game --limit 3
```

### Bulk Content Import
```bash
# Upload multiple games
python tabletop_cli.py batch-upload rules_data/ --pattern "*.md"

# Validate all games
python tabletop_cli.py list-games --verbose
# Then validate each game individually
python tabletop_cli.py validate game1
python tabletop_cli.py validate game2
```

### Content Maintenance
```bash
# Check system status
python tabletop_cli.py status

# Validate integrity
python tabletop_cli.py validate chess

# Re-upload updated rules
python tabletop_cli.py delete chess --force
python tabletop_cli.py upload rules_data/chess_rules_v2.md
```

## 🚀 Advanced Usage

### Custom API Endpoint
```bash
# Set custom backend URL
export API_BASE_URL=https://your-api.com
python tabletop_cli.py status
```

### Verbose Output
```bash
# Get detailed information
python tabletop_cli.py upload rules_data/game.md --verbose
python tabletop_cli.py list-games --verbose
```

### Batch Processing Script
```bash
#!/bin/bash
# batch_import.sh
for file in rules_data/*.md; do
    echo "Uploading $file..."
    python tabletop_cli.py upload "$file"
done
python tabletop_cli.py list-games
```

## 🐛 Troubleshooting

### Common Issues

**Authentication Failed**
```bash
# Check backend is running
python tabletop_cli.py status

# Verify credentials in backend
curl -X POST "http://localhost:8000/token" -d "username=admin&password=secret"
```

**Upload Errors**
```bash
# Check file format
python tabletop_cli.py upload --verbose problem_file.md

# Use debug endpoint
curl -X POST "http://localhost:8000/api/admin/debug/parse-markdown" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@problem_file.md"
```

**Backend Connection**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify API endpoints
curl http://localhost:8000/docs
```

### Error Codes
- `Exit 1`: General error (authentication, file not found, etc.)
- Network timeouts: Backend not responding
- `422`: Invalid request format
- `404`: Game/resource not found
- `500`: Internal server error

## 📊 Performance Tips

1. **Batch Operations**: Use `batch-upload` for multiple files
2. **Validation**: Run `validate` after bulk imports
3. **Limits**: Use `--limit` for large rule sets
4. **Verbose Mode**: Only use `--verbose` when needed

## 🔗 Integration with Backend

The CLI integrates with these FastAPI endpoints:
- `POST /token` - Authentication
- `GET /api/admin/games/` - List games (detailed)
- `GET /api/admin/games/{game_id}/rules` - Get game rules
- `POST /api/admin/upload/markdown-simple` - Upload single file
- `POST /api/admin/batch/upload` - Batch upload
- `DELETE /api/admin/games/{game_id}` - Delete game
- `POST /api/admin/games/{game_id}/validate` - Validate integrity
- `PUT /api/admin/rules/{rule_id}` - Update rule
- `DELETE /api/admin/rules/{rule_id}` - Delete rule

## 🎯 Development

### Adding New Commands
```python
@app.command("new-command")
def new_command(
    param: str = typer.Argument(..., help="Parameter description"),
    option: bool = typer.Option(False, "--option", help="Option description")
):
    """Command description."""
    # Implementation
    pass
```

### Testing
```bash
# Test all CLI functionality
python tabletop_cli.py status
python tabletop_cli.py list-games
python tabletop_cli.py upload rules_data/chess_rules.md
python tabletop_cli.py show-rules chess
python tabletop_cli.py validate chess
python tabletop_cli.py delete chess --force
```

This CLI provides a complete content management workflow optimized for single-admin scenarios while maintaining flexibility for future enhancements.