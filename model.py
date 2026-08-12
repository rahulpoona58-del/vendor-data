import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.infrastructure.database.models import Vendor

def get_vendor(vendor_id):
    """Retrieves a single vendor profile from the unified database by ID."""
    try:
        vendor_id = int(vendor_id)
        v = Vendor.query.get(vendor_id)
        if not v:
            v = Vendor.query.filter_by(id=vendor_id).first()
        return v.to_dict() if v else None
    except Exception:
        return None

def get_all_vendors():
    """Retrieves all vendor profiles from the unified database."""
    try:
        vendors = Vendor.query.all()
        return [v.to_dict() for v in vendors]
    except Exception:
        return []

def get_top_vendors(n=5):
    """Retrieves top vendors sorted by trust score from the unified database."""
    try:
        vendors = Vendor.query.order_by(Vendor.trust_score.desc()).limit(n).all()
        return [v.to_dict() for v in vendors]
    except Exception:
        return []

def generate_chart():
    """Generates the trust score distribution histogram from live database records."""
    try:
        vendors = Vendor.query.all()
        scores = [v.trust_score for v in vendors] if vendors else [75.0]
        
        plt.figure(figsize=(8, 4))
        plt.hist(scores, bins=10, color='#3b82f6', edgecolor='#1e3a8a')
        plt.title("Vendor Trust Score Distribution", fontsize=12, fontweight='bold')
        plt.xlabel("Trust Score (0 - 100)")
        plt.ylabel("Vendor Count")
        plt.tight_layout()
        
        os.makedirs("static", exist_ok=True)
        plt.savefig("static/chart.png", dpi=150)
        plt.close()
    except Exception as e:
        print(f"Chart generation error: {e}")