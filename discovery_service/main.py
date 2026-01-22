"""
FastAPI Main Application for Product Discovery Service
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

from .models import DiscoveryRequest, DiscoveryResponse
from .analyzer import ProductDiscoveryAnalyzer
from .config import DEFAULT_MODEL_FREE, PRO_MODELS
from .email_service import send_email_report

app = FastAPI(
    title="Product Discovery API",
    description="AI-powered Amazon product discovery and analysis service",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (CSS, JS, Images)
# Mount specific directories to ensure assets load correctly from root paths
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/data", StaticFiles(directory="data"), name="data")
app.mount("/js", StaticFiles(directory="js"), name="js")
app.mount("/images", StaticFiles(directory="images"), name="images")

# Fallback: Mount root for other static files (like .html pages in root)
# Note: Specific mounts above take precedence.
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def read_index():
    return FileResponse('index.html')

@app.get("/{filename}.html")
async def read_html(filename: str):
    # Security check: prevent directory traversal
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
        
    file_path = f"{filename}.html"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    
    # Check if it's a blog post (e.g. blog/xxx.html requested as xxx.html? No, usually it's /blog/xxx)
    # If filename matches a known page, return it.
    
    raise HTTPException(status_code=404, detail="Page not found")

# Handle blog post paths if they are like /blog/some-post.html
@app.get("/blog/{post_slug}.html")
async def read_blog_post(post_slug: str):
    # Strategy 1: If static HTML exists in data/blog/
    path1 = f"data/blog/{post_slug}.html"
    if os.path.exists(path1):
        return FileResponse(path1)
        
    # Strategy 2: If we use a template (blog-post.html) and client-side rendering
    # This is likely how it works if no static HTMLs exist.
    if os.path.exists("blog-post.html"):
        return FileResponse("blog-post.html")
        
    raise HTTPException(status_code=404, detail="Blog post not found")

@app.get("/styles.css")
async def read_css():
    return FileResponse('styles.css')

@app.get("/script_v2.js")
async def read_js():
    return FileResponse('script_v2.js')


# Global analyzer instance
analyzer = ProductDiscoveryAnalyzer()

# Store for completed reports (in production, use database)
reports_store = {}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Product Discovery API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/models")
async def get_available_models():
    """Get list of available models for Pro users"""
    return {
        "free_model": DEFAULT_MODEL_FREE,
        "pro_models": PRO_MODELS,
        "default_pro_model": PRO_MODELS[0]
    }


async def run_analysis_task(request: DiscoveryRequest):
    """Background task to run analysis"""
    try:
        report = await analyzer.analyze(request)
        reports_store[report.report_id] = report
        
        # Send email with report
        await send_email_report(report)
        
        print(f"Report {report.report_id} completed and stored")
    except Exception as e:
        print(f"Error in analysis task: {str(e)}")
        # TODO: Send error notification email


@app.post("/api/discovery/analyze", response_model=DiscoveryResponse)
async def analyze_product(
    request: DiscoveryRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a product discovery analysis
    
    This endpoint accepts the analysis request and starts processing in the background.
    The user will receive the report via email when complete.
    """
    try:
        # Validate request
        if not request.category or not request.keywords:
            raise HTTPException(
                status_code=400,
                detail="Category and keywords are required"
            )
        
        if not request.user_email or "@" not in request.user_email:
            raise HTTPException(
                status_code=400,
                detail="Valid email address is required"
            )
        
        # Start analysis in background
        background_tasks.add_task(run_analysis_task, request)
        
        return DiscoveryResponse(
            success=True,
            message=f"Analysis started! Report will be sent to {request.user_email} within 5-10 minutes.",
            estimated_delivery_minutes=10
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error starting analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start analysis: {str(e)}"
        )


@app.post("/api/discovery/analyze-sync")
async def analyze_product_sync(request: DiscoveryRequest):
    """
    Synchronous analysis endpoint (for testing)
    
    This endpoint runs the analysis synchronously and returns the report immediately.
    Use this for testing or when you need the report right away.
    """
    try:
        report = await analyzer.analyze(request)
        reports_store[report.report_id] = report
        
        # Return first 500 chars as preview
        preview = report.report_markdown[:500] + "..."
        
        return DiscoveryResponse(
            success=True,
            message="Analysis complete!",
            report_id=report.report_id,
            report_preview=preview,
            estimated_delivery_minutes=0
        )
        
    except Exception as e:
        print(f"Error in sync analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/api/discovery/report/{report_id}")
async def get_report(report_id: str):
    """Get a completed report by ID"""
    if report_id not in reports_store:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )
    
    report = reports_store[report_id]
    return report


@app.get("/api/discovery/reports")
async def list_reports():
    """List all reports (for testing)"""
    return {
        "count": len(reports_store),
        "reports": [
            {
                "report_id": r.report_id,
                "keywords": r.keywords,
                "generated_at": r.generated_at
            }
            for r in reports_store.values()
        ]
    }


if __name__ == "__main__":
    print("Starting Product Discovery Service...")
    print("API will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )
