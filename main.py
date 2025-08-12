from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Odin School - EdTech Solutions",
    description="AI-driven solutions for EdTech problems",
    version="1.0.0"
)

# CORS middleware
# Read CORS origins from env: comma-separated list, e.g. "http://localhost:8000,http://localhost:8001"
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://localhost:8001")
origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

# Browsers disallow credentials with wildcard origin. If '*' is present, disable credentials.
allow_credentials = True
if any(o == "*" for o in origins):
    origins = ["*"]
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for each problem
from problems.hotlead.routes import router as hotlead_router
from problems.creatorfit.routes import router as creatorfit_router
from problems.trustdesk.routes import router as trustdesk_router
from problems.adlift.routes import router as adlift_router
# from problems.refermore.routes import router as refermore_router  # Temporarily disabled
from problems.pricesense.routes import router as pricesense_router
from problems.firsttouch.routes import router as firsttouch_router
from problems.onetruth.routes import router as onetruth_router
from problems.closemore.routes import router as closemore_router

app.include_router(hotlead_router, prefix="/api/hotlead", tags=["HotLead - Sales"])
app.include_router(creatorfit_router, prefix="/api/creatorfit", tags=["CreatorFit - Influencer Marketing"])
app.include_router(trustdesk_router, prefix="/api/trustdesk", tags=["TrustDesk - Branding"])
app.include_router(adlift_router, prefix="/api/adlift", tags=["AdLift - Marketing"])
# app.include_router(refermore_router, prefix="/api/refermore", tags=["ReferMore - Sales"])  # Temporarily disabled
app.include_router(pricesense_router, prefix="/api/pricesense", tags=["PriceSense - Product"])
app.include_router(firsttouch_router, prefix="/api/firsttouch", tags=["FirstTouch BOT - Sales"])
app.include_router(onetruth_router, prefix="/api/onetruth", tags=["OneTruth - Marketing Analytics"])
app.include_router(closemore_router, prefix="/api/closemore", tags=["CloseMore - Sales"])

@app.get("/")
async def root():
    return {
        "message": "Odin School EdTech Solutions API",
        "problems": [
            "HotLead - Sales Lead Scoring",
            "CreatorFit - Influencer Marketing",
            "TrustDesk - Comment/Review Management", 
            "AdLift - Marketing Optimization",
            "ReferMore - Referral System",
            "PriceSense - Pricing Optimization",
            "FirstTouch BOT - Sales Automation",
            "OneTruth - Analytics Dashboard",
            "CloseMore - Sales Conversation Analysis"
        ],
        "docs": "/docs",
        "status": "Running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
