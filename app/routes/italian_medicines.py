from flask import Blueprint, request, jsonify
from app.models.italian_medicine import ItalianMedicine
from app.utils.auth import token_required, create_response, serialize_doc

italian_medicines_bp = Blueprint("italian_medicines", __name__)


@italian_medicines_bp.route("/search", methods=["GET"])
def search_italian_medicines():
    """
    Search Italian medicines by various criteria
    GET /api/italian-medicines/search?q=<query>&type=<name|aic|manufacturer|ingredient>&limit=<20>
    """
    query = request.args.get("q", "").strip()
    search_type = request.args.get("type", "name")  # name, aic, manufacturer, ingredient
    limit = int(request.args.get("limit", 20))

    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    try:
        if search_type == "aic":
            # Exact match for AIC code
            result = ItalianMedicine.find_by_aic(query)
            medicines = [result] if result else []
        elif search_type == "manufacturer":
            medicines = ItalianMedicine.search_by_manufacturer(query, limit)
        elif search_type == "ingredient":
            medicines = ItalianMedicine.search_by_active_ingredient(query, limit)
        else:  # default to name search
            medicines = ItalianMedicine.search_by_name(query, limit)

        return create_response(data=serialize_doc(medicines), status=200)

    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@italian_medicines_bp.route("/aic/<codice_aic>", methods=["GET"])
def get_by_aic(codice_aic):
    """
    Get Italian medicine details by AIC code
    GET /api/italian-medicines/aic/<codice_aic>
    """
    try:
        medicine = ItalianMedicine.find_by_aic(codice_aic)
        
        if not medicine:
            return create_response(message="Medicine not found", status=404)

        return create_response(data=serialize_doc(medicine), status=200)

    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@italian_medicines_bp.route("/stats", methods=["GET"])
def get_stats():
    """
    Get statistics about Italian medicines database
    GET /api/italian-medicines/stats
    """
    try:
        total_count = ItalianMedicine.count()
        
        return create_response(
            data={"total_medicines": total_count},
            status=200
        )

    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@italian_medicines_bp.route("/list", methods=["GET"])
def list_medicines():
    """
    Get paginated list of Italian medicines
    GET /api/italian-medicines/list?limit=<100>&skip=<0>
    """
    try:
        limit = int(request.args.get("limit", 100))
        skip = int(request.args.get("skip", 0))
        
        medicines = ItalianMedicine.get_all(limit, skip)
        total_count = ItalianMedicine.count()

        return create_response(
            data={
                "medicines": serialize_doc(medicines),
                "count": len(medicines),
                "total": total_count,
                "skip": skip,
                "limit": limit
            },
            status=200
        )

    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)
