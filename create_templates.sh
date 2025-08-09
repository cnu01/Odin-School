#!/bin/bash

# Array of problems with descriptions
declare -A problems
problems[adlift]="Marketing Campaign Optimization"
problems[refermore]="Referral System Enhancement" 
problems[pricesense]="Pricing and Payment Plan Optimization"
problems[firsttouch]="Sales Automation and First Contact"
problems[onetruth]="Marketing Analytics and Data Unification"
problems[closemore]="Sales Conversation Analysis"

for problem in "${!problems[@]}"; do
    desc="${problems[$problem]}"
    
    # Create models.py
    cat > "problems/$problem/models.py" << EOF
from pydantic import BaseModel

class ${problem^}Base(BaseModel):
    """Base model for ${problem^} - define your models here"""
    pass

# TODO: Add your models here
EOF

    # Create routes.py
    cat > "problems/$problem/routes.py" << EOF
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def ${problem}_home():
    """${problem^} - $desc"""
    return {
        "problem": "${problem^} - $desc",
        "description": "Ready for development",
        "status": "Template created"
    }

# TODO: Add your routes here
EOF

    # Create service.py
    cat > "problems/$problem/service.py" << EOF
class ${problem^}Service:
    """Service class for ${problem^} operations"""
    
    def __init__(self):
        # TODO: Initialize database connections, etc.
        pass
    
    # TODO: Add your service methods here
EOF

    # Create __init__.py with problem description
    cat > "problems/$problem/__init__.py" << EOF
"""
${problem^} - $desc

Problem Statement: [Add your problem description here]

Target Solutions: [Add your solutions here]

Success Metrics: [Add your metrics here]
"""
EOF

done

echo "Created template files for all problems!"
