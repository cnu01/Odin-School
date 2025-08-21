from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from database import connect_to_mongo, close_mongo_connection
import os

load_dotenv()

app = FastAPI(
    title="APEX AI - EdTech Solutions",
    description="AI-driven solutions for EdTech problems",
    version="1.0.0"
)

# Database connection events
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# ------------------------
# ✅ CORS configuration
# ------------------------
cors_origins_env = os.getenv("CORS_ORIGINS", "")
origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

# If wildcard is used, disable credentials (browser restriction)
allow_credentials = True
if "*" in origins:
    origins = ["*"]
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],  # default to * if empty
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# Static files
# ------------------------
app.mount("/adlift", StaticFiles(directory="problems/adlift/static"), name="adlift")

# ------------------------
# Routers
# ------------------------
from problems.hotlead.routes import router as hotlead_router
from problems.creatorfit.routes import router as creatorfit_router
from problems.trustdesk.routes import router as trustdesk_router
from problems.adlift.routes import router as adlift_router
from problems.refermore import router as refermore_router
from problems.pricesense.routes import router as pricesense_router
from problems.firsttouch.routes import router as firsttouch_router
from problems.onetruth.routes import router as onetruth_router
from problems.closemore.routes import router as closemore_router

app.include_router(hotlead_router, prefix="/api/hotlead", tags=["HotLead - Sales"])
app.include_router(creatorfit_router, prefix="/api/creatorfit", tags=["CreatorFit - Influencer Marketing"])
app.include_router(trustdesk_router, prefix="/api/trustdesk", tags=["TrustDesk - Branding"])
app.include_router(adlift_router, prefix="/api/adlift", tags=["AdLift - Marketing"])
app.include_router(refermore_router, prefix="/api/refermore", tags=["ReferMore - Sales"])
app.include_router(pricesense_router, prefix="/api/pricesense", tags=["PriceSense - Product"])
app.include_router(firsttouch_router, prefix="/api/firsttouch", tags=["FirstTouch BOT - Sales"])
app.include_router(onetruth_router, prefix="/api/onetruth", tags=["OneTruth - Marketing Analytics"])
app.include_router(closemore_router, prefix="/api/closemore", tags=["CloseMore - Sales"])

# ------------------------
# Routes
# ------------------------
@app.get("/")
async def root():
    return {
        "message": "APEX AI EdTech Solutions API",
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
