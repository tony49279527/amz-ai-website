import os
import json
import time
from supabase_client import create_report, update_report_done, update_report_failed

def process_analysis_request(data):
    """
    Handles the analysis request from the frontend.
    1. Extracts ASIN and Marketplace.
    2. Creates a record in Supabase (AnalysisReports).
    3. Triggers the actual analysis (currently mocked or via n8n in frontend).
    
    Returns:
        tuple: (response_dict, status_code)
    """
    asin = data.get('asin')
    marketplace = data.get('marketplace', 'us')

    if not asin:
        return {"error": "ASIN is required"}, 400

    print(f"Processing analysis for ASIN: {asin}, Marketplace: {marketplace}")

    # 1. Create pending report in Supabase
    report_id = create_report(asin, marketplace)
    
    if not report_id:
        # Fallback if DB fails (or keys missing)
        return {"error": "Failed to create report in database (check .env keys)"}, 500

    # 2. In a real async worker setup, we would trigger a background task here.
    # For now, since the frontend uses n8n directly for the heavy lifting, 
    # we just acknowledge the creation. 
    
    # If we want to move n8n logic to backend, we would call it here.
    # But user wants to "integrate database", so primarily we store the record.
    
    return {
        "message": "Report initialized",
        "report_id": report_id,
        "status": "pending"
    }, 200
