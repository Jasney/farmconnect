from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from market.models import MarketPrice

from .models import Crop

User = get_user_model()


def normalize_crop_name(value):
    return " ".join((value or "").strip().lower().split())


def get_market_price_queryset(crop_name):
    normalized_name = normalize_crop_name(crop_name)
    if not normalized_name:
        return MarketPrice.objects.none()
    return MarketPrice.objects.filter(crop_name__iexact=normalized_name).order_by("-updated_at")


def get_crop_price_insights(crop_name, listing_price=None, location=None):
    price_rows = list(get_market_price_queryset(crop_name))
    if not price_rows:
        return {
            "available": False,
            "crop_name": crop_name,
            "message": "No market price data is available for this crop yet.",
        }

    prices = [row.price for row in price_rows]
    avg_price = sum(prices) / len(prices)
    highest = max(price_rows, key=lambda row: row.price)
    lowest = min(price_rows, key=lambda row: row.price)
    selected_market = None

    if location:
        selected_market = next(
            (row for row in price_rows if row.location and row.location.lower() == location.lower()),
            None,
        )

    price_gap = None
    position_label = None
    if listing_price is not None:
        listing_decimal = Decimal(listing_price)
        price_gap = listing_decimal - avg_price
        if price_gap > 0:
            position_label = "above"
        elif price_gap < 0:
            position_label = "below"
        else:
            position_label = "aligned"

    return {
        "available": True,
        "crop_name": crop_name,
        "market_count": len(price_rows),
        "average_price": avg_price,
        "highest_price": highest.price,
        "highest_market": highest.location or "Best available market",
        "lowest_price": lowest.price,
        "lowest_market": lowest.location or "Lowest available market",
        "selected_market": selected_market,
        "listing_price": listing_price,
        "price_gap": price_gap,
        "price_position": position_label,
        "latest_updated_at": max(price_rows, key=lambda row: row.updated_at).updated_at,
        "message": f"Average market price is KES {avg_price:.2f}.",
    }


def get_price_insight_cards(crops, limit=3):
    insight_cards = []
    seen = set()

    for crop in crops:
        key = normalize_crop_name(crop.name)
        if not key or key in seen:
            continue
        seen.add(key)
        insight = get_crop_price_insights(
            crop.name,
            listing_price=crop.price_per_unit,
            location=getattr(crop.farmer, "location", ""),
        )
        if insight["available"]:
            insight_cards.append(
                {
                    "crop": crop,
                    "insight": insight,
                }
            )
        if len(insight_cards) >= limit:
            break

    return insight_cards


def get_buyer_matches(crop, limit=5):
    buyers = (
        User.objects.filter(role="buyer", account_status="active")
        .exclude(id=crop.farmer_id)
        .annotate(
            same_crop_requests=Count(
                "purchase_requests",
                filter=Q(purchase_requests__crop__name__iexact=crop.name),
                distinct=True,
            ),
            same_type_requests=Count(
                "purchase_requests",
                filter=Q(purchase_requests__crop__type=crop.type),
                distinct=True,
            ),
            completed_deals=Count(
                "purchase_requests",
                filter=Q(purchase_requests__status="completed"),
                distinct=True,
            ),
            same_crop_saves=Count(
                "saved_listings",
                filter=Q(saved_listings__crop__name__iexact=crop.name),
                distinct=True,
            ),
            same_type_saves=Count(
                "saved_listings",
                filter=Q(saved_listings__crop__type=crop.type),
                distinct=True,
            ),
        )
        .order_by("-same_crop_requests", "-same_crop_saves", "-completed_deals", "username")
    )

    matches = []
    farmer_location = normalize_crop_name(getattr(crop.farmer, "location", ""))

    for buyer in buyers:
        score = (
            buyer.same_crop_requests * 5
            + buyer.same_crop_saves * 4
            + buyer.same_type_requests * 3
            + buyer.same_type_saves * 2
            + buyer.completed_deals
        )

        reasons = []
        if buyer.same_crop_requests:
            reasons.append(f"{buyer.same_crop_requests} request(s) for {crop.name}")
        if buyer.same_crop_saves:
            reasons.append(f"{buyer.same_crop_saves} saved listing(s) for {crop.name}")
        if buyer.same_type_requests:
            reasons.append(f"active interest in {crop.get_type_display().lower()}")
        if buyer.completed_deals:
            reasons.append(f"{buyer.completed_deals} completed marketplace deal(s)")

        buyer_location = normalize_crop_name(getattr(buyer, "location", ""))
        if farmer_location and buyer_location and farmer_location == buyer_location:
            score += 3
            reasons.append("same location as the farmer")

        if score <= 0:
            continue

        matches.append(
            {
                "buyer": buyer,
                "score": score,
                "reasons": reasons[:3],
            }
        )

    matches.sort(key=lambda item: (-item["score"], item["buyer"].username.lower()))
    return matches[:limit]


def build_assistant_response(user, question):
    normalized_question = normalize_crop_name(question)
    active_crops = Crop.objects.filter(is_active=True).select_related("farmer")
    market_prices = list(MarketPrice.objects.all())

    matching_crop = None
    for crop in active_crops:
        if normalize_crop_name(crop.name) in normalized_question:
            matching_crop = crop
            break

    matched_market_name = None
    for market_price in market_prices:
        candidate = normalize_crop_name(market_price.crop_name)
        if candidate and candidate in normalized_question:
            matched_market_name = market_price.crop_name
            break

    target_crop_name = (
        matching_crop.name
        if matching_crop
        else matched_market_name
    )

    if ("buyer" in normalized_question or "sell" in normalized_question or "market" in normalized_question) and user.role == "farmer":
        if not matching_crop:
            matching_crop = active_crops.filter(farmer=user).first()
        if matching_crop:
            matches = get_buyer_matches(matching_crop, limit=3)
            insight = get_crop_price_insights(
                matching_crop.name,
                listing_price=matching_crop.price_per_unit,
                location=user.location,
            )
            if matches:
                reasons = "; ".join(
                    f"{item['buyer'].username} ({', '.join(item['reasons'])})" for item in matches
                )
                price_line = insight["message"] if insight["available"] else "No market benchmark is available yet."
                return {
                    "title": f"Best next buyers for {matching_crop.name}",
                    "answer": f"{price_line} Strong buyer matches right now are {reasons}.",
                    "suggestions": [
                        "Message the top match first.",
                        "Compare your listing price with market averages.",
                        "Keep quantity and location updated to improve matching.",
                    ],
                }

    if target_crop_name and ("price" in normalized_question or "market" in normalized_question):
        insight = get_crop_price_insights(target_crop_name, location=getattr(user, "location", ""))
        if insight["available"]:
            selected_market = ""
            if insight["selected_market"]:
                selected_market = (
                    f" In {insight['selected_market'].location}, the latest price is "
                    f"KES {insight['selected_market'].price:.2f}/{insight['selected_market'].unit}."
                )
            return {
                "title": f"Market outlook for {target_crop_name}",
                "answer": (
                    f"Average market price is KES {insight['average_price']:.2f}. "
                    f"Best observed market is {insight['highest_market']} at KES {insight['highest_price']:.2f}, "
                    f"while the lowest is {insight['lowest_market']} at KES {insight['lowest_price']:.2f}.{selected_market}"
                ),
                "suggestions": [
                    "Review the market prices page for more locations.",
                    "Update listing prices when the gap is large.",
                    "Use buyer matching after pricing the crop.",
                ],
            }

    if user.role == "buyer":
        recommended_crops = active_crops.order_by("-created_at")[:3]
        crop_names = ", ".join(crop.name for crop in recommended_crops)
        return {
            "title": "Buyer assistant summary",
            "answer": (
                "You can compare current market prices, save listings, and message farmers directly. "
                f"Fresh listings to review now: {crop_names or 'none yet'}."
            ),
            "suggestions": [
                "Ask about a crop price by name.",
                "Open saved listings before sending requests.",
                "Compare listing price against market price first.",
            ],
        }

    return {
        "title": "Farm Connect assistant",
        "answer": (
            "Ask me about crop prices, where to sell a crop, or which buyers are likely to respond. "
            "I answer using your current marketplace data."
        ),
        "suggestions": [
            "What is the price of maize?",
            "Who are the best buyers for my beans listing?",
            "Which market is paying the most for tomatoes?",
        ],
    }
